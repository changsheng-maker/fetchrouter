# FetchRouter - 智能网页抓取

当用户需要抓取网页内容时，使用 FetchRouter 自动选择最佳工具并执行。

## 触发条件

用户输入以下任何一种：
- `/fetch <url>` - 抓取单个 URL
- `/fetch-batch <urls>` - 批量抓取
- 直接粘贴 URL 并要求抓取
- 提到"抓取"、"获取网页"、"读取链接"等

## 使用方式

### 1. 抓取单个 URL

```
用户: /fetch https://github.com/anthropics/claude-code

你:
🔗 正在抓取: https://github.com/anthropics/claude-code
📋 策略: fast_first (GitHub 公开页面)
🤖 Agent: jina-agent (并行执行中...)

✅ 抓取成功 (643ms)
📄 内容: 26,512 字符 | 1,877 词 | 241 链接

[显示内容预览或完整内容]
```

### 2. 批量抓取

```
用户: /fetch-batch url1,url2,url3

你:
🔄 批量抓取 3 个 URL
━━━━━━━━━━━━━━━━━━━━━━━━━━
[1/3] ✅ url1 (jina-agent, 523ms)
[2/3] ✅ url2 (browser-agent, 1.2s)
[3/3] ❌ url3 (失败: 需要登录)
━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 统计: 2/3 成功 (66.7%)
```

### 3. 自动检测 URL

```
用户: 看看这个 https://x.com/elonmusk/status/123456

你:
🔍 检测到 X/Twitter 链接
📱 策略: social_first (推文专用)
🤖 Agent: social-agent → browser-agent → jina-agent

⚡ 执行中...
```

## 抓取流程

### 步骤 1: 分析 URL
使用 `analyze_url()` 确定：
- 网站类型 (github, medium, x_twitter, wechat...)
- 推荐策略 (fast_first, login_first, social_first...)
- Agent 链 (jina → browser → social)

### 步骤 2: 选择策略

| 网站类型 | 策略 | Agent 执行顺序 |
|---------|------|---------------|
| GitHub/Medium/新闻 | fast_first | jina + browser 并行 |
| X/Twitter/微博 | social_first | social → browser → jina 串行 |
| 微信/小红书/知乎 | login_first | browser (CDP) 串行 |
| 反爬严格站点 | anti_bot | scrapling → browser 串行 |

### 步骤 3: 执行抓取

```python
# 快速优先策略示例
if strategy == "fast_first":
    # 并行启动 Jina + Browser
    tasks = [
        jina_agent.fetch(url),
        browser_agent.fetch(url, delay=2)  # 延迟启动
    ]
    # 谁先成功用谁
    result = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
```

### 步骤 4: 质量检查

检查抓取结果：
- ✅ 内容长度 > 500 字符
- ✅ 不包含 "请登录" 等登录墙提示
- ✅ 不包含 "404" 等错误页面
- ✅ 标题和正文完整

### 步骤 5: 输出结果

成功时：
```
✅ 抓取成功
📄 标题: [页面标题]
✍️  作者: [作者名]
📅 时间: [发布时间]
━━━━━━━━━━━━━━━━━━━━
[正文内容，Markdown 格式]
━━━━━━━━━━━━━━━━━━━━
🔗 相关链接: [提取的链接列表]
```

失败时：
```
❌ 抓取失败
原因: [具体错误]
💡 建议: [解决方案]
```

## 特殊处理

### 需要登录的网站

```
用户: /fetch https://mp.weixin.qq.com/s/xxxxx

你:
🔐 检测到微信公众号 (需要登录)
⚠️  当前策略: login_first

💡 要使用 web-access (CDP 模式)，需要：
   1. Chrome 已启动并登录微信
   2. Chrome 开启了远程调试端口

请先运行 Chrome：
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

然后重试抓取。
```

### 内容过长

如果内容超过 8000 字符，只显示前 8000 字符并提示：
```
📄 内容过长 (25,000 字符)，显示前 8,000 字符
💡 使用 /fetch <url> --full 查看完整内容
```

### 批量任务中断

如果批量抓取中某个 URL 失败：
```
⚠️  url3 抓取失败 (超时)
⏭️  继续处理剩余 URL...
```

## 输出格式

### 标准格式

```markdown
# [标题]

**来源**: [URL]
**作者**: [作者]
**时间**: [发布时间]

---

[正文内容，Markdown 格式]

---

**相关链接**:
- [链接1]
- [链接2]
```

### JSON 格式 (使用 --json)

```json
{
  "success": true,
  "url": "原始URL",
  "title": "页面标题",
  "author": "作者",
  "content": "正文内容",
  "links": ["链接列表"],
  "metadata": {
    "word_count": 1234,
    "char_count": 5678,
    "duration_ms": 643
  }
}
```

## 缓存机制

FetchRouter 会自动缓存结果（默认 5 分钟）：

```
💾 使用缓存 (3 分钟前抓取)
```

要强制刷新：
```
/fetch <url> --no-cache
```

## 配置管理

用户可以通过 `/fetch-config` 配置：

```
用户: /fetch-config cache-duration 600

你:
✅ 缓存时长已设置为 600 秒 (10 分钟)
```

可配置项：
- `cache-duration`: 缓存时长（秒）
- `default-output`: 默认输出格式 (markdown/json)
- `max-content-length`: 最大内容长度
- `timeout`: 超时时间（秒）

## 错误处理

常见错误及处理：

| 错误 | 原因 | 解决方案 |
|-----|------|---------|
| 超时 | 网站响应慢 | 重试或换工具 |
| 需要登录 | 内容被保护 | 使用 CDP 模式 |
| 反爬拦截 | IP 被封 | 使用 Scrapling Agent |
| 内容太短 | 可能是登录页 | 检查是否需要登录 |
| DNS 错误 | URL 无效 | 检查 URL 拼写 |

## 最佳实践

1. **优先使用自动策略** - 系统会自动选择最佳 Agent
2. **批量抓取限速** - 同一域名串行执行，避免被封
3. **利用缓存** - 5 分钟内重复 URL 直接返回缓存
4. **关注质量** - 自动检查登录墙和内容完整性
5. **及时反馈** - 失败时给出具体原因和解决方案

## 集成调用

如果需要在其他 Skill 中调用：

```python
# 从 FetchRouter 导入
import sys
sys.path.insert(0, "~/.claude/skills/fetchrouter")

from agents.orchestrator import fetch_url

# 调用
result = await fetch_url("https://example.com")
if result.success:
    content = result.content["text"]
```

---

**核心原则**: 用户只管发链接，系统自动搞定一切。
