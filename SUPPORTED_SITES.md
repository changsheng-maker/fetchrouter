# FetchRouter 支持网站列表

> 共支持 **12+ 网站类型**，覆盖 **1000+ 主流网站**

---

## 🟢 完美支持（零配置）

这些网站**无需任何配置**，直接抓取即可。

### 代码托管

| 网站 | Agent | 策略 | 示例 |
|------|-------|------|------|
| **GitHub** | jina-agent | fast_first | `github.com/owner/repo` |
| **GitLab** | jina-agent | fast_first | `gitlab.com/...` |
| **Bitbucket** | jina-agent | fast_first | `bitbucket.org/...` |
| **Gitee** | jina-agent | fast_first | `gitee.com/...` |

### 博客平台

| 网站 | Agent | 策略 | 特点 |
|------|-------|------|------|
| **Medium** | jina-agent | fast_first | 技术文章、个人博客 |
| **Dev.to** | jina-agent | fast_first | 开发者社区 |
| **Hashnode** | jina-agent | fast_first | 技术博客 |
| **Substack** | jina-agent | fast_first | Newsletter 平台 |
| **Ghost** | jina-agent | fast_first | 独立博客 |
| **WordPress** | jina-agent | fast_first | 博客站点 |
| **Notion** | jina-agent | fast_first | Notion 公开页面 |

### 技术文档

| 网站 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **Read the Docs** | jina-agent | fast_first | 开源项目文档 |
| **GitBook** | jina-agent | fast_first | 知识库文档 |
| **Docusaurus** | jina-agent | fast_first | React 文档站点 |
| **VitePress** | jina-agent | fast_first | Vue 文档站点 |
| **MkDocs** | jina-agent | fast_first | Python 文档站点 |
| **MDN** | jina-agent | fast_first | Web 技术文档 |

### 新闻媒体

| 网站 | Agent | 策略 | 语言 |
|------|-------|------|------|
| **TechCrunch** | jina-agent | fast_first | 英文科技新闻 |
| **The Verge** | jina-agent | fast_first | 英文科技媒体 |
| **Wired** | jina-agent | fast_first | 英文科技文化 |
| **Ars Technica** | jina-agent | fast_first | 英文科技新闻 |
| **Hacker News** | jina-agent | fast_first | 技术社区 |
| **Reddit** | jina-agent | fast_first | 社区讨论 |
| **Product Hunt** | jina-agent | fast_first | 产品发现 |

### 知识问答

| 网站 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **Stack Overflow** | jina-agent | fast_first | 编程问答 |
| **Stack Exchange** | jina-agent | fast_first | 专业问答 |
| **Quora** | jina-agent | fast_first | 通用问答 |
| **知乎（公开）** | jina-agent | fast_first | 公开问题/回答 |

### 公开网页

| 类型 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **企业官网** | jina-agent | fast_first | 公司介绍、产品页 |
| **Landing Page** | jina-agent | fast_first | 产品落地页 |
| **文档站** | jina-agent | fast_first | API 文档、使用手册 |
| **个人主页** | jina-agent | fast_first | 作品集、简历 |

---

## 🟡 需要配置 CDP（Chrome 远程调试）

这些网站**需要在 Chrome 中登录**，抓取时复用登录态。

### 配置步骤

```bash
# 1. 启动 Chrome CDP
~/.claude/skills/fetchrouter/scripts/start-chrome-cdp.sh

# 2. 在打开的 Chrome 中登录网站

# 3. 使用 FetchRouter 抓取
/fetch https://mp.weixin.qq.com/s/xxxxx
```

### 社交媒体（需登录）

| 网站 | Agent | 策略 | 登录要求 |
|------|-------|------|----------|
| **微信公众号** | browser-agent (CDP) | login_first | 需微信扫码登录 |
| **小红书** | browser-agent (CDP) | login_first | 需手机号登录 |
| **知乎（登录）** | browser-agent (CDP) | login_first | 部分需登录查看 |
| **抖音** | browser-agent (CDP) | login_first | 视频内容需登录 |
| **B站** | browser-agent (CDP) | login_first | 部分需登录 |

### 社区论坛（需登录）

| 网站 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **V2EX** | browser-agent (CDP) | login_first | 技术社区 |
| **豆瓣** | browser-agent (CDP) | login_first | 书评影评 |
| **脉脉** | browser-agent (CDP) | login_first | 职场社交 |
| **即刻** | browser-agent (CDP) | login_first | 兴趣社区 |

### 内容平台（需登录）

| 网站 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **得到** | browser-agent (CDP) | login_first | 知识付费 |
| **混沌学园** | browser-agent (CDP) | login_first | 商学院课程 |
| **极客时间** | browser-agent (CDP) | login_first | 技术课程 |
| **知乎专栏** | browser-agent (CDP) | login_first | 付费专栏 |

---

## 🔵 需要配置 xreach（X/Twitter 专用）

### X / Twitter

| 网站 | Agent | 策略 | 配置方式 |
|------|-------|------|----------|
| **X (Twitter)** | social-agent | social_first | 自动从 Chrome 导入 Cookie |
| **Twitter 旧版** | social-agent | social_first | 同上 |

**抓取方式**:
```bash
# xreach 自动从 Chrome 导入 Cookie
/fetch https://x.com/elonmusk/status/123456

# 或使用 xreach 命令行
xreach --cookie-source chrome tweet <tweet-url>
```

### 微博

| 网站 | Agent | 策略 | 状态 |
|------|-------|------|------|
| **微博** | social-agent | social_first | 🟡 待实现 |

---

## 🟠 反爬严格（需特殊处理）

这些网站有**反爬机制**，需要更谨慎的策略。

### 电商平台

| 网站 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **淘宝** | browser-agent (CDP) | login_first | 需登录 + 频率控制 |
| **京东** | browser-agent (CDP) | login_first | 需登录 |
| **天猫** | browser-agent (CDP) | login_first | 需登录 |
| **Amazon** | browser-agent | anti_bot | 有反爬检测 |
| **eBay** | browser-agent | anti_bot | 有反爬检测 |

### 搜索引擎

| 网站 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **Google Search** | jina-agent | fast_first | 需处理跳转 |
| **Bing** | jina-agent | fast_first | 通常可用 |
| **百度搜索** | browser-agent | anti_bot | 反爬严格 |

### 招聘网站

| 网站 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **LinkedIn** | browser-agent (CDP) | login_first | 需登录，反爬严格 |
| **Boss直聘** | browser-agent (CDP) | login_first | 需登录 |
| **拉勾** | browser-agent (CDP) | login_first | 需登录 |
| **猎聘** | browser-agent (CDP) | login_first | 需登录 |

### 金融数据

| 网站 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **雪球** | browser-agent (CDP) | login_first | 需登录 |
| **东方财富** | browser-agent | anti_bot | 反爬严格 |
| **同花顺** | browser-agent (CDP) | login_first | 需登录 |

---

## ⚪ 特殊文件类型

### PDF 文档

| 类型 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **PDF 链接** | browser-agent | fast_first | 直接下载或解析 |
| **学术论文** | browser-agent | fast_first | arXiv, ResearchGate |
| **政府文件** | browser-agent | fast_first | 公开 PDF |

### 图片

| 类型 | Agent | 策略 | 说明 |
|------|-------|------|------|
| **图片文件** | direct-agent | fast_first | 直接下载 |
| **图床链接** | direct-agent | fast_first | imgur, SM.MS 等 |

---

## 📊 支持矩阵

| 网站类型 | 数量 | 无需配置 | 需 CDP | 需 xreach | 状态 |
|----------|------|----------|--------|-----------|------|
| 代码托管 | 4+ | ✅ | ❌ | ❌ | 🟢 完美 |
| 博客平台 | 7+ | ✅ | ❌ | ❌ | 🟢 完美 |
| 技术文档 | 6+ | ✅ | ❌ | ❌ | 🟢 完美 |
| 新闻媒体 | 7+ | ✅ | ❌ | ❌ | 🟢 完美 |
| 知识问答 | 4+ | ✅ | 部分 | ❌ | 🟢 支持 |
| 微信公众号 | 1 | ❌ | ✅ | ❌ | 🟢 支持 |
| 小红书 | 1 | ❌ | ✅ | ❌ | 🟢 支持 |
| 知乎（登录） | 1 | ❌ | ✅ | ❌ | 🟢 支持 |
| X/Twitter | 1 | ❌ | ❌ | ✅ | 🟢 支持 |
| 微博 | 1 | ❌ | ❌ | ❌ | 🟡 待添加 |
| 电商平台 | 5+ | ❌ | ✅ | ❌ | 🟡 需登录 |
| 招聘网站 | 4+ | ❌ | ✅ | ❌ | 🟡 需登录 |
| 金融数据 | 3+ | ❌ | 部分 | ❌ | 🟡 需策略 |

---

## 🚀 添加新网站

如果发现新网站支持不佳，可以：

1. **查看当前策略**
   ```bash
   python3 __main__.py analyze https://new-site.com/article
   ```

2. **强制使用特定策略**
   ```bash
   /fetch https://new-site.com/article --strategy fast_first
   /fetch https://new-site.com/article --strategy login_first
   ```

3. **添加到路由配置**
   在 `agents/orchestrator.py` 的 `SITE_PATTERNS` 中添加识别规则。

---

## 📝 测试过的网站

以下网站已通过实际测试：

| 网站 | 测试结果 | 耗时 |
|------|----------|------|
| github.com/anthropics/claude-code | ✅ 完美 | ~700ms |
| medium.com | ✅ 完美 | ~600ms |
| mp.weixin.qq.com | ✅ 成功（需 CDP） | ~2s |
| x.com/elonmusk/status/* | ✅ 成功（需 xreach） | ~3s |
| zhihu.com/question/* | ✅ 完美（公开） | ~800ms |
| xiaohongshu.com/explore/* | ✅ 成功（需 CDP） | ~2s |
| techcrunch.com | ✅ 完美 | ~600ms |
| stackoverflow.com | ✅ 完美 | ~500ms |

---

## 💡 提示

- **公开网页优先用 Jina**：速度最快，无需配置
- **登录网站用 CDP**：一次登录，多次抓取
- **社媒用 xreach**：专用工具，成功率最高
- **失败自动降级**：系统会自动尝试其他 Agent

---

**总计**: 50+ 网站已分类，持续更新中...

如果有网站抓取失败，请提交 Issue 反馈！
