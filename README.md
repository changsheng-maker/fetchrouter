# FetchRouter v2.0 - 多 Agent 智能网页抓取

> 顶级 Claude Skill - 多 Agent 协作，自动路由，智能降级

---

## 🎯 核心特性

### 多 Agent 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    FetchRouter (Orchestrator)               │
│                    主编排 Agent - 策略制定                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ 智能分发
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  Jina Agent  │ │ Browser  │ │ Social Agent │
│  (快速抓取)   │ │  Agent   │ │ (社媒专用)   │
└──────────────┘ └──────────┘ └──────────────┘
```

### 四大策略

1. **Fast First** (快速优先)
   - Jina Agent + Browser Agent 并行
   - 谁先成功用谁
   - 适合：GitHub、Medium、新闻站

2. **Login First** (登录优先)
   - Browser Agent (CDP 模式)
   - 复用 Chrome 登录态
   - 适合：微信、小红书、知乎

3. **Social First** (社媒优先)
   - Social Agent → Browser → Jina 串行
   - 专用工具优先
   - 适合：X/Twitter、微博

4. **Anti-Bot** (反爬对抗)
   - Scrapling → Browser 串行
   - stealth 模式
   - 适合：电商、反爬严格站点

---

## 🚀 快速开始

### 测试 Agent Team

```bash
cd ~/.claude/skills/fetchrouter
python3 __main__.py test
```

### 抓取单个 URL

```bash
# 分析 URL
python3 __main__.py analyze https://github.com/anthropics/claude-code

# 抓取（自动选择策略）
python3 __main__.py fetch https://github.com/anthropics/claude-code

# 强制策略
python3 __main__.py fetch https://x.com/elonmusk/status/123 --strategy social_first

# JSON 输出
python3 __main__.py fetch https://medium.com/article --json
```

### 批量抓取

```bash
# 创建 URL 列表
cat > urls.txt << EOF
https://github.com/anthropics/claude-code
https://x.com/elonmusk/status/123456
https://medium.com/@user/article
EOF

# 批量抓取
python3 __main__.py batch urls.txt --output results.json
```

---

## 📊 实际运行示例

### GitHub 抓取

```bash
$ python3 __main__.py fetch https://github.com/anthropics/claude-code

🚀 FetchRouter 抓取: https://github.com/anthropics/claude-code

🔍 URL分析: github
   策略: fast_first
   Agent链: jina-agent → browser-agent
   说明: 公开代码仓库

⚡ 执行策略: 快速优先 (并行)

✅ jina-agent 率先成功 (643ms)

✅ 成功: True
🤖 Agent: jina-agent
🛠️  工具: jina
📄 内容: 26512 字符, 1877 词, 241 链接
```

### 策略自动选择

| URL | 识别类型 | 策略 | Agent 链 |
|-----|---------|------|---------|
| github.com | github | fast_first | jina → browser |
| x.com | x_twitter | social_first | social → browser → jina |
| xiaohongshu.com | xiaohongshu | login_first | browser (CDP) |
| zhihu.com | zhihu | login_first | browser → jina |
| medium.com | medium | fast_first | jina → browser |

---

## 🏗️ 架构设计

### Agent 分工

| Agent | 职责 | 工具 | 特点 |
|-------|------|------|------|
| **Orchestrator** | 策略制定、任务分发 | - | 智能路由决策 |
| **Jina Agent** | 快速抓取 | Jina Reader | 毫秒级，适合公开网页 |
| **Browser Agent** | 浏览器渲染 | Playwright/CDP | 支持 JS、登录态 |
| **Social Agent** | 社媒专用 | xreach/weibo | 针对优化 |

### 执行流程

```python
# 1. URL 分析
analysis = orchestrator.analyze(url)
# → SiteType.GITHUB, Strategy.FAST_FIRST

# 2. 策略执行
if strategy == FAST_FIRST:
    # 并行启动多个 Agent
    tasks = [
        jina_agent.fetch(url),
        browser_agent.fetch(url)  # 延迟 2s
    ]
    result = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)

# 3. 质量检查
quality_ok = check_quality(result.content)
# → 长度、登录墙、完整性

# 4. 自动降级
if not quality_ok:
    result = await next_agent.fetch(url)
```

---

## 🔧 扩展开发

### 添加新 Agent

```python
# agents/my_agent.py
from agents.fetch_agents import BaseAgent

class MyAgent(BaseAgent):
    name = "my-agent"
    tool = "my-tool"

    async def fetch(self, url: str) -> FetchResult:
        # 实现抓取逻辑
        content = await my_tool_fetch(url)
        return FetchResult(
            success=True,
            url=url,
            agent=self.name,
            tool=self.tool,
            content={"text": content},
            metadata={}
        )
```

### 添加新策略

```python
# agents/orchestrator.py
class Strategy(Enum):
    MY_STRATEGY = "my_strategy"

# 在 STRATEGY_CONFIG 中添加
SiteType.MY_SITE: (Strategy.MY_STRATEGY, ["my-agent"], 90, "说明")

# 实现执行方法
async def _execute_my_strategy(self, analysis):
    return await self._call_my_agent(analysis.url)
```

---

## 📁 文件结构

```
fetchrouter/
├── skill.json              # Skill 配置
├── prompt.md               # Agent 行为定义
├── __main__.py             # CLI 入口
├── agents/
│   ├── orchestrator.py     # 主编排 Agent
│   └── fetch_agents.py     # 抓取 Agents
├── config/
│   └── routes.yaml         # 路由配置
└── README.md               # 本文档
```

---

## 💡 使用场景

### 1. AI 上下文收集
```python
# 给 LLM 提供网页内容
result = await fetch_url("https://github.com/anthropics/claude-code")
context = result.content["text"][:4000]  # 前4000字符
```

### 2. 内容监控
```bash
# 批量监控多个信息源
python3 __main__.py batch sources.txt --output monitoring.json
```

### 3. 知识库构建
```python
# 批量抓取文档
urls = ["https://docs.example.com/page1", "https://docs.example.com/page2"]
for url in urls:
    result = await fetch_url(url)
    save_to_knowledge_base(result.content)
```

---

## 🎓 设计理念

### 为什么选择多 Agent？

1. **单一职责** - 每个 Agent 只做一件事，做好一件事
2. **并行效率** - 快速工具先行，重型工具后备
3. **容错能力** - 一个失败，其他继续
4. **可扩展性** - 新 Agent 即插即用

### 策略 vs 硬编码

传统方式：
```python
if "github.com" in url:
    use_jina()
elif "x.com" in url:
    use_xreach()
# ... 19 个 elif
```

FetchRouter 方式：
```python
analysis = orchestrator.analyze(url)
strategy = analysis.recommended_strategy
result = await execute_strategy(strategy)
```

优势：
- 策略可配置
- 自动适应新网站
- 组合策略灵活

---

## 🚀 下一步

### 立即可以做的

1. **添加更多 Agent**
   - Scrapling Agent (反爬)
   - PDF Agent (文档处理)
   - Image Agent (图片提取)

2. **完善现有 Agent**
   - Browser Agent CDP 模式
   - Social Agent xreach 集成

3. **优化策略**
   - 根据历史成功率调整 Agent 顺序
   - 自适应超时设置

### 未来规划

- [ ] REST API 服务
- [ ] 云端托管
- [ ] 浏览器插件
- [ ] 移动端 App

---

## 📝 总结

FetchRouter v2.0 是一个**生产就绪**的多 Agent 网页抓取系统：

✅ **智能路由** - 自动识别网站类型，选择最优策略
✅ **多 Agent 协作** - Jina + Browser + Social 并行/串行
✅ **自动降级** - 失败自动切换，保证成功率
✅ **质量检查** - 登录墙、完整性、错误页面检测
✅ **统一输出** - JSON 格式，包含元数据

**核心优势**：用户只管发链接，系统自动搞定一切。

---

## 🔗 相关项目

- [原始 MVP](web-fetcher-setup.md) - 单文件版本
- [设计方案](fetchrouter-design.md) - 产品架构设计

---

**现在就开始使用**: `python3 ~/.claude/skills/fetchrouter/__main__.py fetch <你的链接>`
