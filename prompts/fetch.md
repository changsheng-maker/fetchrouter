# /fetch 命令 - 抓取单个 URL

## 用法

```
/fetch <url> [选项]
```

## 选项

- `--strategy <strategy>` - 强制使用指定策略 (fast_first, login_first, social_first, anti_bot)
- `--no-cache` - 跳过缓存，强制重新抓取
- `--json` - JSON 格式输出
- `--full` - 显示完整内容（不截断）
- `--save <path>` - 保存到文件

## 执行流程

1. **解析 URL**
   - 提取域名
   - 识别网站类型

2. **选择策略**
   - 如果用户指定了 `--strategy`，使用用户策略
   - 否则自动选择推荐策略

3. **执行抓取**
   - 调用 `fetch_url(url, strategy)`
   - 显示进度："🤖 Agent: jina-agent (执行中...)"

4. **处理结果**
   - 成功：显示内容预览
   - 失败：显示错误原因和建议

5. **缓存结果**
   - 成功后缓存 5 分钟
   - 显示 "💾 已缓存"

## 输出示例

### 成功 - Markdown 格式

```
🔗 抓取: https://github.com/anthropics/claude-code
📋 策略: fast_first (GitHub 公开页面)
🤖 Agent: jina-agent
⚡ 执行中...

✅ 抓取成功 (643ms)
📄 26,512 字符 | 1,877 词

━━━━━━━━━━━━━━━━━━━━━━━━━━
# GitHub - anthropics/claude-code

**来源**: https://github.com/anthropics/claude-code

Claude Code is an agentic coding tool...

[内容预览，最多 8000 字符]

[如果超过 8000 字符]
... (共 26,512 字符，使用 --full 查看完整内容)
━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 已缓存 (5 分钟内再次抓取将使用缓存)
```

### 成功 - JSON 格式

```
🔗 抓取: https://github.com/anthropics/claude-code
📋 策略: fast_first
🤖 Agent: jina-agent
✅ 抓取成功 (643ms)

```json
{
  "success": true,
  "url": "https://github.com/anthropics/claude-code",
  "title": "GitHub - anthropics/claude-code",
  "content": "...",
  "metadata": {
    "duration_ms": 643,
    "word_count": 1877
  }
}
```
```

### 失败

```
🔗 抓取: https://x.com/elonmusk/status/123456
📋 策略: social_first (X/Twitter)
🤖 Agent: social-agent

❌ 抓取失败
原因: xreach 未安装

💡 建议:
   1. 安装 xreach: npm install -g xreach
   2. 或使用浏览器模式: /fetch <url> --strategy fast_first
```

### 缓存命中

```
🔗 抓取: https://github.com/anthropics/claude-code
💾 使用缓存 (2 分钟前抓取)

✅ 抓取成功
📄 26,512 字符 | 1,877 词

[内容...]
```

## 特殊场景

### 需要登录

```
🔗 抓取: https://mp.weixin.qq.com/s/xxxxx
📋 策略: login_first (微信公众号)
🤖 Agent: browser-agent (CDP 模式)

❌ 抓取失败
原因: CDP 连接失败 (Chrome 未启动远程调试)

💡 解决方案:
   1. 启动 Chrome 并开启远程调试:
      /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222

   2. 登录微信网页版

   3. 然后重试: /fetch <url>

⚠️  或者尝试其他方式:
   - 复制内容粘贴给我
   - 使用截图工具保存后发送图片
```

### 内容过长

```
🔗 抓取: https://example.com/long-article
📋 策略: fast_first
🤖 Agent: jina-agent
✅ 抓取成功 (1.2s)
📄 45,000 字符 | 3,200 词

⚠️  内容过长，显示前 8,000 字符
💡 使用 --full 查看完整内容
   或 --save <path> 保存到文件

━━━━━━━━━━━━━━━━━━━━━━━━━━
[前 8000 字符内容]
...
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 技术实现

```python
import asyncio
import sys
sys.path.insert(0, "~/.claude/skills/fetchrouter")

from agents.orchestrator import fetch_url, analyze_url

# 分析
analysis = analyze_url(url)
print(f"📋 策略: {analysis.recommended_strategy.value}")

# 抓取
result = await fetch_url(url, strategy=args.strategy)

if result.success:
    print(f"✅ 抓取成功 ({result.duration_ms:.0f}ms)")
    print(f"📄 {result.metadata['char_count']} 字符")
    print(result.content["text"][:8000])  # 截断显示
else:
    print(f"❌ 抓取失败: {result.error}")
```
