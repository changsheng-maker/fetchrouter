#!/usr/bin/env python3
"""
FetchRouter Orchestrator - 主编排 Agent
协调多个子 Agent 完成网页抓取任务
"""

import re
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Pattern
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from agents.fetch_agents import FetchResult
from core.logger import info, debug, warning, error

# 预编译 SITE_PATTERNS（性能优化）
# 注意：这些在模块导入时编译，避免每次匹配时重复编译
_SITE_PATTERNS_COMPILED: Dict[SiteType, List[Pattern]] = {
    SiteType.X_TWITTER: [re.compile(r"(x\.com|twitter\.com|t\.co)", re.IGNORECASE)],
    SiteType.WECHAT: [re.compile(r"mp\.weixin\.qq\.com", re.IGNORECASE)],
    SiteType.XIAOHONGSHU: [re.compile(r"xiaohongshu\.com", re.IGNORECASE)],
    SiteType.ZHIHU: [re.compile(r"zhihu\.com", re.IGNORECASE)],
    SiteType.DOUYIN: [re.compile(r"douyin\.com", re.IGNORECASE)],
    SiteType.BILIBILI: [re.compile(r"bilibili\.com/video", re.IGNORECASE)],
    SiteType.GITHUB: [re.compile(r"github\.com", re.IGNORECASE)],
    SiteType.MEDIUM: [re.compile(r"medium\.com", re.IGNORECASE)],
    SiteType.NEWS: [re.compile(r"(techcrunch|theverge|wired|nytimes|bbc)\.com", re.IGNORECASE)],
    SiteType.ECOMMERCE: [re.compile(r"(amazon|taobao|jd|tmall)\.(com|cn)", re.IGNORECASE)],
    SiteType.PDF: [re.compile(r"\.pdf$", re.IGNORECASE)],
    SiteType.IMAGE: [re.compile(r"\.(jpg|jpeg|png|gif|webp|svg)$", re.IGNORECASE)],
}


class Strategy(Enum):
    """抓取策略"""
    FAST_FIRST = "fast_first"      # 快速优先：Jina + Browser 并行
    LOGIN_FIRST = "login_first"    # 登录优先：Browser CDP
    SOCIAL_FIRST = "social_first"  # 社媒优先：专用工具
    ANTI_BOT = "anti_bot"          # 反爬对抗：Scrapling
    UNKNOWN = "unknown"            # 未知：自动探测


class SiteType(Enum):
    """网站类型"""
    GITHUB = "github"
    MEDIUM = "medium"
    BLOG = "blog"
    NEWS = "news"
    X_TWITTER = "x_twitter"
    WECHAT = "wechat"
    XIAOHONGSHU = "xiaohongshu"
    ZHIHU = "zhihu"
    DOUYIN = "douyin"
    BILIBILI = "bilibili"
    ECOMMERCE = "ecommerce"
    PDF = "pdf"
    IMAGE = "image"
    UNKNOWN = "unknown"


@dataclass
class URLAnalysis:
    """URL 分析结果"""
    url: str
    site_type: SiteType
    domain: str
    requires_login: bool
    requires_js: bool
    anti_bot_protection: bool
    recommended_strategy: Strategy
    agent_chain: List[str]
    priority: int
    note: str


class Orchestrator:
    """
    主编排 Agent - 负责 URL 分析和任务分发
    """

    # 网站类型识别规则
    SITE_PATTERNS = {
        SiteType.X_TWITTER: [r"(x\.com|twitter\.com|t\.co)"],
        SiteType.WECHAT: [r"mp\.weixin\.qq\.com"],
        SiteType.XIAOHONGSHU: [r"xiaohongshu\.com"],
        SiteType.ZHIHU: [r"zhihu\.com"],
        SiteType.DOUYIN: [r"douyin\.com"],
        SiteType.BILIBILI: [r"bilibili\.com/video"],
        SiteType.GITHUB: [r"github\.com"],
        SiteType.MEDIUM: [r"medium\.com"],
        SiteType.NEWS: [r"(techcrunch|theverge|wired|nytimes|bbc)\.com"],
        SiteType.ECOMMERCE: [r"(amazon|taobao|jd|tmall)\.(com|cn)"],
        SiteType.PDF: [r"\.pdf$"],
        SiteType.IMAGE: [r"\.(jpg|jpeg|png|gif|webp|svg)$"],
    }

    # 策略配置
    STRATEGY_CONFIG = {
        SiteType.GITHUB: (Strategy.FAST_FIRST, ["jina-agent", "browser-agent"], 90, "公开代码仓库"),
        SiteType.MEDIUM: (Strategy.FAST_FIRST, ["jina-agent", "browser-agent"], 90, "博客平台"),
        SiteType.BLOG: (Strategy.FAST_FIRST, ["jina-agent", "browser-agent"], 85, "博客站点"),
        SiteType.NEWS: (Strategy.FAST_FIRST, ["jina-agent", "browser-agent"], 85, "新闻媒体"),
        SiteType.X_TWITTER: (Strategy.SOCIAL_FIRST, ["social-agent", "browser-agent", "jina-agent"], 100, "社交媒体"),
        SiteType.WECHAT: (Strategy.LOGIN_FIRST, ["browser-agent"], 95, "微信公众号，需登录"),
        SiteType.XIAOHONGSHU: (Strategy.LOGIN_FIRST, ["browser-agent"], 95, "小红书，需登录"),
        SiteType.ZHIHU: (Strategy.LOGIN_FIRST, ["browser-agent", "jina-agent"], 90, "知乎，部分需登录"),
        SiteType.ECOMMERCE: (Strategy.ANTI_BOT, ["scrapling-agent", "browser-agent"], 80, "电商平台，反爬严格"),
        SiteType.PDF: (Strategy.FAST_FIRST, ["browser-agent"], 70, "PDF文档"),
        SiteType.IMAGE: (Strategy.FAST_FIRST, ["direct-agent"], 60, "图片文件"),
        SiteType.UNKNOWN: (Strategy.FAST_FIRST, ["jina-agent", "browser-agent"], 50, "未知站点，自动探测"),
    }

    def __init__(self):
        self.cache = {}
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "by_agent": {}
        }
        self._stats_lock = asyncio.Lock()

    def analyze(self, url: str) -> URLAnalysis:
        """
        分析 URL，确定网站类型和抓取策略
        """
        domain = self._extract_domain(url)
        site_type = self._identify_site_type(url)
        strategy, agent_chain, priority, note = self.STRATEGY_CONFIG.get(
            site_type, self.STRATEGY_CONFIG[SiteType.UNKNOWN]
        )

        # 特殊判断
        requires_login = site_type in [SiteType.WECHAT, SiteType.XIAOHONGSHU]
        requires_js = site_type in [SiteType.DOUYIN, SiteType.BILIBILI]
        anti_bot = site_type == SiteType.ECOMMERCE

        return URLAnalysis(
            url=url,
            site_type=site_type,
            domain=domain,
            requires_login=requires_login,
            requires_js=requires_js,
            anti_bot_protection=anti_bot,
            recommended_strategy=strategy,
            agent_chain=agent_chain,
            priority=priority,
            note=note
        )

    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        url = url.replace("https://", "").replace("http://", "")
        return url.split("/")[0]

    def _identify_site_type(self, url: str) -> SiteType:
        """识别网站类型 - 使用预编译正则（性能优化）"""
        for site_type, patterns in _SITE_PATTERNS_COMPILED.items():
            for pattern in patterns:
                if pattern.search(url):
                    return site_type
        return SiteType.UNKNOWN

    async def fetch(self, url: str, force_strategy: Optional[Strategy] = None) -> FetchResult:
        """
        执行抓取 - 主入口
        """
        start_time = time.time()
        self.stats["total_requests"] += 1

        # 1. 分析 URL
        analysis = self.analyze(url)
        info(f"URL分析: {analysis.site_type.value}")
        info(f"  策略: {analysis.recommended_strategy.value}")
        info(f"  Agent链: {' → '.join(analysis.agent_chain)}")
        info(f"  说明: {analysis.note}")

        # 2. 根据策略执行
        if force_strategy:
            strategy = force_strategy
        else:
            strategy = analysis.recommended_strategy

        # 3. 执行抓取
        if strategy == Strategy.FAST_FIRST:
            result = await self._execute_fast_first(analysis)
        elif strategy == Strategy.LOGIN_FIRST:
            result = await self._execute_login_first(analysis)
        elif strategy == Strategy.SOCIAL_FIRST:
            result = await self._execute_social_first(analysis)
        elif strategy == Strategy.ANTI_BOT:
            result = await self._execute_anti_bot(analysis)
        else:
            result = await self._execute_fast_first(analysis)

        # 4. 更新统计
        duration = (time.time() - start_time) * 1000
        result.duration_ms = duration

        async with self._stats_lock:
            if result.success:
                self.stats["successful"] += 1
            else:
                self.stats["failed"] += 1

            agent = result.agent
            if agent not in self.stats["by_agent"]:
                self.stats["by_agent"][agent] = {"success": 0, "fail": 0}
            self.stats["by_agent"][agent]["success" if result.success else "fail"] += 1

        return result

    async def _execute_fast_first(self, analysis: URLAnalysis) -> FetchResult:
        """
        快速优先策略：并行启动 Jina + Browser
        谁先成功用谁
        """
        print("⚡ 执行策略: 快速优先 (并行)")

        # 创建任务
        tasks = []

        if "jina-agent" in analysis.agent_chain:
            tasks.append(self._call_jina_agent(analysis.url))

        if "browser-agent" in analysis.agent_chain:
            # Browser Agent 延迟 2 秒启动，给 Jina 一个机会先完成
            tasks.append(self._call_browser_agent_delayed(analysis.url, delay=2))

        # 等待第一个成功的结果
        done, pending = await asyncio.wait(
            [asyncio.create_task(t) for t in tasks],
            return_when=asyncio.FIRST_COMPLETED
        )

        # 取消未完成的任务
        for task in pending:
            task.cancel()

        # 获取结果
        for task in done:
            try:
                result = task.result()
                if result and result.success:
                    info(f"{result.agent} 率先成功")
                    return result
            except Exception as e:
                warning(f"Agent 异常: {e}")

        # 全部失败，返回第一个结果（包含错误信息）
        for task in done:
            try:
                return task.result()
            except Exception as e:
                return FetchResult(
                    success=False,
                    url=analysis.url,
                    agent="none",
                    tool="none",
                    content={},
                    metadata={},
                    error=str(e)
                )

        return FetchResult(
            success=False,
            url=analysis.url,
            agent="none",
            tool="none",
            content={},
            metadata={},
            error="所有 Agent 都失败"
        )

    async def _execute_login_first(self, analysis: URLAnalysis) -> FetchResult:
        """
        登录优先策略：只使用 Browser Agent (CDP)
        """
        info("执行策略: 登录优先")
        info("  注意: 需要 Chrome 已登录相应网站")

        return await self._call_browser_agent(analysis.url, use_cdp=True)

    async def _execute_social_first(self, analysis: URLAnalysis) -> FetchResult:
        """
        社媒优先策略：专用工具 → Browser → Jina
        """
        info("执行策略: 社媒优先 (串行)")

        for agent_name in analysis.agent_chain:
            info(f"  尝试 {agent_name}...")

            if agent_name == "social-agent":
                result = await self._call_social_agent(analysis.url)
            elif agent_name == "browser-agent":
                result = await self._call_browser_agent(analysis.url)
            elif agent_name == "jina-agent":
                result = await self._call_jina_agent(analysis.url)
            else:
                continue

            if result.success:
                return result

            warning(f"{agent_name} 失败，降级到下一个")

        return FetchResult(
            success=False,
            url=analysis.url,
            agent="none",
            tool="none",
            content={},
            metadata={},
            error="所有社媒 Agent 都失败"
        )

    async def _execute_anti_bot(self, analysis: URLAnalysis) -> FetchResult:
        """
        反爬对抗策略：Scrapling → Browser
        """
        info("执行策略: 反爬对抗")

        for agent_name in analysis.agent_chain:
            if agent_name == "scrapling-agent":
                result = await self._call_scrapling_agent(analysis.url)
            elif agent_name == "browser-agent":
                result = await self._call_browser_agent(analysis.url)
            else:
                continue

            if result.success:
                return result

        return FetchResult(
            success=False,
            url=analysis.url,
            agent="none",
            tool="none",
            content={},
            metadata={},
            error="反爬对抗失败"
        )

    # ============ Agent 调用方法 ============

    async def _call_jina_agent(self, url: str) -> FetchResult:
        """调用 Jina Agent"""
        from agents.fetch_agents import JinaAgent
        agent = JinaAgent()
        return await agent.fetch(url)

    async def _call_browser_agent(self, url: str, use_cdp: bool = False) -> FetchResult:
        """调用 Browser Agent"""
        from agents.fetch_agents import BrowserAgent
        agent = BrowserAgent(use_cdp=use_cdp)
        return await agent.fetch(url)

    async def _call_browser_agent_delayed(self, url: str, delay: int) -> FetchResult:
        """延迟调用 Browser Agent"""
        await asyncio.sleep(delay)
        return await self._call_browser_agent(url)

    async def _call_social_agent(self, url: str) -> FetchResult:
        """调用 Social Agent"""
        from agents.fetch_agents import SocialAgent
        agent = SocialAgent()
        return await agent.fetch(url)

    async def _call_scrapling_agent(self, url: str) -> FetchResult:
        """调用 Scrapling Agent"""
        # TODO: 实现 Scrapling Agent
        return FetchResult(
            success=False,
            url=url,
            agent="scrapling-agent",
            tool="scrapling",
            content={},
            metadata={},
            error="Scrapling Agent 未实现"
        )

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats


# 便捷函数
def analyze_url(url: str) -> URLAnalysis:
    """分析 URL"""
    orchestrator = Orchestrator()
    return orchestrator.analyze(url)


async def fetch_url(url: str, strategy: Optional[str] = None) -> FetchResult:
    """抓取 URL"""
    orchestrator = Orchestrator()

    if strategy:
        strategy_enum = Strategy(strategy)
    else:
        strategy_enum = None

    return await orchestrator.fetch(url, force_strategy=strategy_enum)
