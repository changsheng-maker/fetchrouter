#!/usr/bin/env python3
"""
Fetch Agents - 具体执行抓取的子 Agents
每个 Agent 负责一种抓取方式
"""

import re
import json
import time
import asyncio
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from dataclasses import dataclass


# 预编译正则表达式（性能优化）
CLEAN_PATTERN = re.compile(r'\n\s*\n\s*\n')
LINK_PATTERN = re.compile(r'https?://[^\s\)\]\>\"\']+')

# 登录检测关键字（使用 frozenset 优化查找性能）
LOGIN_INDICATORS = frozenset([
    "请登录", "登录后查看", "需要登录", "sign in to view",
    "please log in", "login required", "authentication required"
])


@dataclass
class FetchResult:
    """抓取结果"""
    success: bool
    url: str
    agent: str
    tool: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    error: Optional[str] = None
    duration_ms: float = 0


class BaseAgent:
    """Agent 基类"""

    name = "base"
    tool = "base"

    def _is_safe_url(self, url: str) -> bool:
        """检查 URL 是否安全（防止 SSRF）"""
        from urllib.parse import urlparse
        import ipaddress

        try:
            parsed = urlparse(url)
            hostname = parsed.hostname

            if not hostname:
                return False

            # 检查内网地址
            internal_hosts = {'localhost', '127.0.0.1', '0.0.0.0', '::1', '[::1]'}
            if hostname.lower() in internal_hosts:
                return False

            # 检查私有 IP
            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast:
                    return False
            except ValueError:
                # 不是 IP 地址，是域名，继续检查
                pass

            return True
        except Exception:
            return False

    async def fetch(self, url: str) -> FetchResult:
        """子类必须实现"""
        raise NotImplementedError

    def _clean_content(self, text: str) -> str:
        """清理内容"""
        # 使用预编译的正则移除多余空行
        text = CLEAN_PATTERN.sub('\n\n', text)
        # 移除行首行尾空白
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text.strip()

    def _extract_title(self, text: str) -> Optional[str]:
        """提取标题"""
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith('http'):
                return line
        return None


class JinaAgent(BaseAgent):
    """
    Jina Agent - 使用 Jina Reader 快速抓取
    特点：速度快、无需浏览器、适合公开网页
    """

    name = "jina-agent"
    tool = "jina"

    async def fetch(self, url: str) -> FetchResult:
        """使用 Jina Reader API 抓取"""
        start_time = time.time()

        # SSRF 防护
        if not self._is_safe_url(url):
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool=self.tool,
                content={},
                metadata={},
                error="Access to internal addresses is forbidden",
                duration_ms=0
            )

        try:
            # 确保 URL 有协议
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Jina Reader API: 移除协议后拼接
            url_no_protocol = url.replace('https://', '').replace('http://', '')
            jina_url = f"https://r.jina.ai/http://{url_no_protocol}"

            req = urllib.request.Request(
                jina_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/plain, text/html"
                }
            )

            with urllib.request.urlopen(req, timeout=15) as resp:
                raw_content = resp.read().decode('utf-8', errors='ignore')

            duration = (time.time() - start_time) * 1000

            # 质量检查
            quality_check = self._check_quality(raw_content)
            if not quality_check["ok"]:
                return FetchResult(
                    success=False,
                    url=url,
                    agent=self.name,
                    tool=self.tool,
                    content={},
                    metadata={},
                    error=quality_check["error"],
                    duration_ms=duration
                )

            # 提取内容
            cleaned = self._clean_content(raw_content)
            title = self._extract_title(cleaned)

            # 提取链接（使用预编译正则）
            links = LINK_PATTERN.findall(raw_content)

            return FetchResult(
                success=True,
                url=url,
                agent=self.name,
                tool=self.tool,
                content={
                    "title": title or "",
                    "text": cleaned,
                    "links": list(set(links))[:20]  # 最多20个链接
                },
                metadata={
                    "word_count": len(cleaned.split()),
                    "char_count": len(cleaned),
                    "links_found": len(links)
                },
                duration_ms=duration
            )

        except urllib.error.HTTPError as e:
            duration = (time.time() - start_time) * 1000
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool=self.tool,
                content={},
                metadata={},
                error=f"HTTP {e.code}: {e.reason}",
                duration_ms=duration
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool=self.tool,
                content={},
                metadata={},
                error=str(e),
                duration_ms=duration
            )

    def _check_quality(self, content: str) -> Dict[str, Any]:
        """内容质量检查"""
        if not content:
            return {"ok": False, "error": "内容为空"}

        if len(content) < 500:
            return {"ok": False, "error": f"内容太短 ({len(content)} 字符)"}

        # 使用预定义的 frozenset 检查登录墙（性能优化）
        content_lower = content.lower()
        if any(indicator in content_lower for indicator in LOGIN_INDICATORS):
            # 找到匹配的指示器
            for indicator in LOGIN_INDICATORS:
                if indicator in content_lower:
                    return {"ok": False, "error": f"检测到登录墙: {indicator}"}

        return {"ok": True}


class BrowserAgent(BaseAgent):
    """
    Browser Agent - 使用 Playwright/CDP 抓取
    特点：支持 JS 渲染、可复用登录态
    """

    name = "browser-agent"
    tool = "playwright"

    def __init__(self, use_cdp: bool = False):
        self.use_cdp = use_cdp
        if use_cdp:
            self.tool = "web-access"

    async def fetch(self, url: str) -> FetchResult:
        """使用浏览器抓取"""
        start_time = time.time()

        try:
            if self.use_cdp:
                result = await self._fetch_with_cdp(url)
            else:
                result = await self._fetch_with_playwright(url)

            result.duration_ms = (time.time() - start_time) * 1000
            return result

        except Exception as e:
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool=self.tool,
                content={},
                metadata={},
                error=str(e)
            )

    async def _fetch_with_playwright(self, url: str) -> FetchResult:
        """使用 Playwright 抓取（直接调用）"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    page = await browser.new_page()
                    await page.goto(url, timeout=30000, wait_until="networkidle")

                    # 获取内容
                    text = await page.inner_text("body")
                    title = await page.title()

                    cleaned = self._clean_content(text)

                    return FetchResult(
                        success=True,
                        url=url,
                        agent=self.name,
                        tool=self.tool,
                        content={
                            "title": title,
                            "text": cleaned,
                            "links": []
                        },
                        metadata={
                            "word_count": len(cleaned.split()),
                            "char_count": len(cleaned)
                        }
                    )
                finally:
                    await browser.close()

        except Exception as e:
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool=self.tool,
                content={},
                metadata={},
                error=f"Playwright 错误: {str(e)[:200]}"
            )

    async def _fetch_with_cdp(self, url: str) -> FetchResult:
        """
        使用 CDP (Chrome DevTools Protocol) 抓取
        需要 Chrome 启动远程调试端口
        """
        import json
        import urllib.request

        CDP_PORT = 9222
        CDP_HOST = "localhost"

        try:
            # 1. 获取 Chrome 版本和可用页面列表
            version_url = f"http://{CDP_HOST}:{CDP_PORT}/json/version"
            req = urllib.request.Request(version_url, timeout=5)
            with urllib.request.urlopen(req) as resp:
                version_info = json.loads(resp.read().decode('utf-8'))

            # 2. 创建新页面或连接到现有页面
            new_page_url = f"http://{CDP_HOST}:{CDP_PORT}/json/new"
            req = urllib.request.Request(new_page_url, timeout=10)
            with urllib.request.urlopen(req) as resp:
                page_info = json.loads(resp.read().decode('utf-8'))

            if not page_info or 'webSocketDebuggerUrl' not in page_info:
                return FetchResult(
                    success=False,
                    url=url,
                    agent=self.name,
                    tool=self.tool,
                    content={},
                    metadata={},
                    error="无法创建 CDP 页面"
                )

            ws_url = page_info['webSocketDebuggerUrl']
            page_id = page_info.get('id')

            # 3. 使用 Playwright 连接 CDP
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                # 连接到已存在的 Chrome 实例
                browser = await p.chromium.connect_over_cdp(f"http://{CDP_HOST}:{CDP_PORT}")

                # 获取或创建页面
                if browser.contexts:
                    context = browser.contexts[0]
                    if context.pages:
                        page = context.pages[0]
                    else:
                        page = await context.new_page()
                else:
                    context = await browser.new_context()
                    page = await context.new_page()

                # 导航到 URL
                await page.goto(url, timeout=30000, wait_until="networkidle")

                # 等待页面加载完成
                await page.wait_for_load_state("domcontentloaded", timeout=10000)

                # 额外等待动态内容加载
                await asyncio.sleep(2)

                # 获取内容
                text = await page.inner_text("body")
                title = await page.title()

                # 关闭浏览器连接
                await browser.close()

                # 清理：关闭创建的页面
                if page_id:
                    try:
                        close_url = f"http://{CDP_HOST}:{CDP_PORT}/json/close/{page_id}"
                        urllib.request.urlopen(close_url, timeout=5)
                    except:
                        pass

                cleaned = self._clean_content(text)

                return FetchResult(
                    success=True,
                    url=url,
                    agent=self.name,
                    tool=self.tool,
                    content={
                        "title": title,
                        "text": cleaned,
                        "links": []
                    },
                    metadata={
                        "word_count": len(cleaned.split()),
                        "char_count": len(cleaned),
                        "source": "cdp"
                    }
                )

        except urllib.error.URLError as e:
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool=self.tool,
                content={},
                metadata={},
                error=f"CDP 连接失败: 请确保 Chrome 已启动远程调试 (--remote-debugging-port={CDP_PORT})"
            )
        except Exception as e:
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool=self.tool,
                content={},
                metadata={},
                error=f"CDP 错误: {str(e)}"
            )


class SocialAgent(BaseAgent):
    """
    Social Agent - 社交媒体专用抓取
    特点：针对 X/Twitter、微博等优化
    """

    name = "social-agent"
    tool = "xreach"

    async def fetch(self, url: str) -> FetchResult:
        """抓取社交媒体内容"""
        start_time = time.time()

        # 识别平台
        if "x.com" in url or "twitter.com" in url:
            return await self._fetch_twitter(url, start_time)
        elif "weibo.com" in url:
            return await self._fetch_weibo(url, start_time)
        else:
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool=self.tool,
                content={},
                metadata={},
                error="不支持的社交平台"
            )

    async def _fetch_twitter(self, url: str, start_time: float) -> FetchResult:
        """抓取推文"""
        import subprocess
        from urllib.parse import urlparse

        # 验证 URL 安全
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return FetchResult(
                    success=False,
                    url=url,
                    agent=self.name,
                    tool="xreach",
                    content={},
                    metadata={},
                    error="Invalid URL scheme",
                    duration_ms=(time.time() - start_time) * 1000
                )
            # 只允许 x.com 和 twitter.com
            if parsed.hostname not in ('x.com', 'twitter.com', 'www.x.com', 'www.twitter.com'):
                return FetchResult(
                    success=False,
                    url=url,
                    agent=self.name,
                    tool="xreach",
                    content={},
                    metadata={},
                    error="Invalid Twitter/X URL",
                    duration_ms=(time.time() - start_time) * 1000
                )
        except Exception as e:
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool="xreach",
                content={},
                metadata={},
                error=f"URL validation failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

        # 尝试使用 xreach（异步非阻塞）
        try:
            proc = await asyncio.create_subprocess_exec(
                "xreach", "thread", url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=30
            )

            duration = (time.time() - start_time) * 1000

            if proc.returncode == 0:
                content = stdout.decode('utf-8', errors='ignore')
                return FetchResult(
                    success=True,
                    url=url,
                    agent=self.name,
                    tool="xreach",
                    content={
                        "title": "",
                        "text": content,
                        "links": []
                    },
                    metadata={},
                    duration_ms=duration
                )
            else:
                stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
                return FetchResult(
                    success=False,
                    url=url,
                    agent=self.name,
                    tool="xreach",
                    content={},
                    metadata={},
                    error=f"xreach 失败: {stderr_text}",
                    duration_ms=(time.time() - start_time) * 1000
                )

        except FileNotFoundError:
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool="xreach",
                content={},
                metadata={},
                error="xreach 未安装",
                duration_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return FetchResult(
                success=False,
                url=url,
                agent=self.name,
                tool="xreach",
                content={},
                metadata={},
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )

    async def _fetch_weibo(self, url: str, start_time: float) -> FetchResult:
        """抓取微博"""
        # TODO: 实现微博抓取
        return FetchResult(
            success=False,
            url=url,
            agent=self.name,
            tool="weibo-fetcher",
            content={},
            metadata={},
            error="微博抓取未实现",
            duration_ms=(time.time() - start_time) * 1000
        )
