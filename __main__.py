#!/usr/bin/env python3
"""
FetchRouter - 智能网页抓取路由器
使用方式: python -m fetchrouter <command>
"""

import sys
import asyncio
import json
import argparse
from pathlib import Path

# 添加 Skill 路径
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import Orchestrator, analyze_url, fetch_url


def main():
    parser = argparse.ArgumentParser(
        description="FetchRouter - 智能网页抓取路由器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析 URL
  python -m fetchrouter analyze https://github.com/anthropics/claude-code

  # 抓取 URL
  python -m fetchrouter fetch https://x.com/elonmusk/status/123

  # 批量抓取
  python -m fetchrouter batch urls.txt

  # 测试模式
  python -m fetchrouter test
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析 URL")
    analyze_parser.add_argument("url", help="要分析的 URL")

    # fetch 命令
    fetch_parser = subparsers.add_parser("fetch", help="抓取 URL")
    fetch_parser.add_argument("url", help="要抓取的 URL")
    fetch_parser.add_argument("--strategy", "-s", choices=["fast_first", "login_first", "social_first", "anti_bot"],
                              help="强制使用指定策略")
    fetch_parser.add_argument("--json", "-j", action="store_true", help="输出 JSON 格式")

    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量抓取")
    batch_parser.add_argument("file", help="包含 URL 列表的文件")
    batch_parser.add_argument("--output", "-o", help="输出文件路径")

    # test 命令
    test_parser = subparsers.add_parser("test", help="运行测试")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "fetch":
        asyncio.run(cmd_fetch(args))
    elif args.command == "batch":
        asyncio.run(cmd_batch(args))
    elif args.command == "test":
        asyncio.run(cmd_test())


def cmd_analyze(args):
    """分析 URL"""
    print(f"🔍 分析 URL: {args.url}\n")

    analysis = analyze_url(args.url)

    print(f"网站类型: {analysis.site_type.value}")
    print(f"域名: {analysis.domain}")
    print(f"需要登录: {analysis.requires_login}")
    print(f"需要 JS: {analysis.requires_js}")
    print(f"反爬保护: {analysis.anti_bot_protection}")
    print(f"推荐策略: {analysis.recommended_strategy.value}")
    print(f"Agent 链: {' → '.join(analysis.agent_chain)}")
    print(f"优先级: {analysis.priority}")
    print(f"说明: {analysis.note}")


async def cmd_fetch(args):
    """抓取 URL"""
    print(f"🚀 FetchRouter 抓取: {args.url}\n")

    result = await fetch_url(args.url, strategy=args.strategy)

    if args.json:
        output = {
            "success": result.success,
            "url": result.url,
            "agent": result.agent,
            "tool": result.tool,
            "content": result.content,
            "metadata": result.metadata,
            "error": result.error,
            "duration_ms": result.duration_ms
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print("=" * 80)
        print(f"✅ 成功: {result.success}")
        print(f"🤖 Agent: {result.agent}")
        print(f"🛠️  工具: {result.tool}")
        print(f"⏱️  耗时: {result.duration_ms:.0f}ms")

        if result.error:
            print(f"❌ 错误: {result.error}")

        print("=" * 80)

        if result.content:
            print(f"\n📄 内容:")
            print("-" * 80)
            if result.content.get("title"):
                print(f"标题: {result.content['title']}")
            if result.content.get("text"):
                text = result.content["text"]
                print(f"\n正文 ({len(text)} 字符):")
                print(text[:1000])
                if len(text) > 1000:
                    print(f"\n... (共 {len(text)} 字符)")


async def cmd_batch(args):
    """批量抓取"""
    # 读取 URL 列表
    with open(args.file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    print(f"🔄 批量抓取 {len(urls)} 个 URL\n")

    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        result = await fetch_url(url)
        results.append({
            "url": url,
            "success": result.success,
            "agent": result.agent,
            "error": result.error
        })

        status = "✅" if result.success else "❌"
        print(f"    {status} {result.agent}")

    # 统计
    success_count = sum(1 for r in results if r["success"])
    print(f"\n📊 完成: {success_count}/{len(urls)} 成功")

    # 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存: {args.output}")


async def cmd_test():
    """运行测试"""
    test_urls = [
        ("GitHub", "https://github.com/anthropics/claude-code"),
        ("Medium", "https://medium.com"),
        ("X/Twitter", "https://x.com/elonmusk/status/123456"),
        ("知乎", "https://zhihu.com/question/12345"),
        ("小红书", "https://xiaohongshu.com/explore/abc"),
    ]

    print("🧪 FetchRouter Agent Team 测试\n")
    print("=" * 80)

    for name, url in test_urls:
        print(f"\n测试: {name}")
        print(f"URL: {url}")

        analysis = analyze_url(url)
        print(f"策略: {analysis.recommended_strategy.value}")
        print(f"Agent链: {' → '.join(analysis.agent_chain)}")
        print("-" * 80)

    print("\n✅ 测试完成")
    print("\n使用示例:")
    print("  python -m fetchrouter fetch https://github.com/anthropics/claude-code")


if __name__ == "__main__":
    main()
