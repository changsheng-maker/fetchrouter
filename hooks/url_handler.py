#!/usr/bin/env python3
"""
URL Handler Hook - URL 检测处理钩子
当系统检测到用户输入中的 URL 时触发
"""

import re
from typing import List, Dict, Any

# URL 检测正则
URL_PATTERN = re.compile(
    r'https?://'           # 协议
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
    r'localhost|'          # localhost
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
    r'(?::\d+)?'           # 端口
    r'(?:/?|[/?]\S+)',     # 路径
    re.IGNORECASE
)


def detect_urls(text: str) -> List[str]:
    """从文本中提取所有 URL"""
    return URL_PATTERN.findall(text)


def should_handle_url(url: str) -> bool:
    """判断是否应该处理该 URL"""
    # 支持的域名列表
    supported_domains = [
        'github.com', 'medium.com', 'x.com', 'twitter.com',
        'zhihu.com', 'xiaohongshu.com', 'weibo.com',
        'mp.weixin.qq.com', 'bilibili.com', 'douyin.com',
        'youtube.com', 'reddit.com', 'stackoverflow.com',
    ]

    url_lower = url.lower()
    return any(domain in url_lower for domain in supported_domains)


def on_url_detected(urls: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    URL 检测回调函数

    Args:
        urls: 检测到的 URL 列表
        context: 上下文信息

    Returns:
        处理结果
    """
    context = context or {}

    # 过滤出支持的 URL
    supported_urls = [url for url in urls if should_handle_url(url)]

    if not supported_urls:
        return {
            "action": "ignore",
            "reason": "no_supported_urls",
            "urls": urls
        }

    # 返回建议的操作
    return {
        "action": "fetch",
        "urls": supported_urls,
        "suggested_command": f"fetchrouter fetch {supported_urls[0]}",
        "message": f"检测到 {len(supported_urls)} 个可抓取的链接"
    }


if __name__ == "__main__":
    # 测试
    test_text = """
    请分析这个链接 https://github.com/anthropics/claude-code
    还有这个 https://x.com/elonmusk/status/123456
    以及一个普通链接 https://example.com
    """

    urls = detect_urls(test_text)
    print(f"检测到的 URL: {urls}")

    result = on_url_detected(urls)
    print(f"处理结果: {result}")
