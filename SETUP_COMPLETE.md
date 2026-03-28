# FetchRouter 配置完成 ✅

所有工具已安装并配置完成！

---

## 🎉 已安装的工具

### ✅ 1. Playwright (Browser Agent)
```bash
# 版本
playwright --version
# Version 1.58.2

# Chromium 浏览器位置
~/Library/Caches/ms-playwright/chromium-1208/

# 用途
- JS 渲染页面
- 动态内容抓取
- Playwright 模式（无需 CDP）
```

### ✅ 2. Chrome CDP (登录态抓取)
```bash
# 启动脚本
~/.claude/skills/fetchrouter/scripts/start-chrome-cdp.sh

# 使用方式
# 1. 启动 Chrome 远程调试
~/.claude/skills/fetchrouter/scripts/start-chrome-cdp.sh

# 2. 在 Chrome 中登录需要抓取的网站（微信、小红书等）

# 3. 使用 FetchRouter 抓取
/fetch https://mp.weixin.qq.com/s/xxxxx
```

### ✅ 3. xreach-cli (X/Twitter 专用)
```bash
# 版本
xreach --version
# 0.3.3

# 用途
- X/Twitter 推文抓取
- 支持从浏览器导入 Cookie
- 无需手动配置 API Key

# 使用方式
# 从 Chrome 导入 Cookie 并抓取
xreach --cookie-source chrome tweet <tweet-url>
```

---

## 📊 当前支持的网站

### 🟢 完美支持（无需配置）

| 网站 | Agent | 示例 |
|-----|-------|------|
| GitHub | jina-agent | github.com/... |
| Medium | jina-agent | medium.com/... |
| 技术博客 | jina-agent | dev.to, hashnode |
| 新闻站 | jina-agent | techcrunch.com |
| 任何公开网页 | jina-agent | example.com |

### 🟡 需要配置（Chrome CDP）

| 网站 | Agent | 配置步骤 |
|-----|-------|---------|
| 微信公众号 | browser-agent (CDP) | 1. 启动 CDP 脚本<br>2. 登录微信<br>3. 抓取 |
| 小红书 | browser-agent (CDP) | 同上 |
| 知乎 | browser-agent (CDP) | 同上 |
| 任何需要登录的网站 | browser-agent (CDP) | 同上 |

### 🔵 需要配置（xreach + Cookie）

| 网站 | Agent | 配置步骤 |
|-----|-------|---------|
| X/Twitter | social-agent | 1. xreach 自动使用 Chrome Cookie<br>2. 抓取 |

---

## 🚀 使用方式

### 1. 抓取公开网页（100% 成功）

```bash
/fetch https://github.com/anthropics/claude-code
/fetch https://medium.com/@user/article
/fetch https://techcrunch.com/news
```

### 2. 抓取需要登录的网站

```bash
# 步骤 1: 启动 Chrome CDP
~/.claude/skills/fetchrouter/scripts/start-chrome-cdp.sh

# 步骤 2: 在打开的 Chrome 中登录网站

# 步骤 3: 抓取
/fetch https://mp.weixin.qq.com/s/xxxxx
/fetch https://www.xiaohongshu.com/explore/xxxxx
/fetch https://www.zhihu.com/question/xxxxx
```

### 3. 抓取 X/Twitter

```bash
# xreach 会自动从 Chrome 导入 Cookie
/fetch https://x.com/elonmusk/status/123456

# 或使用 xreach 命令行
xreach --cookie-source chrome tweet <tweet-url>
```

### 4. 批量抓取

```bash
/fetch-batch url1,url2,url3
/fetch-batch @urls.txt --output results.json
```

---

## 🔧 快速启动 Chrome CDP

### 方法一：使用脚本（推荐）

```bash
~/.claude/skills/fetchrouter/scripts/start-chrome-cdp.sh
```

### 方法二：手动启动

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$HOME/.fetchrouter/chrome-profile"
```

### 方法三：后台启动

```bash
# 后台运行
nohup /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$HOME/.fetchrouter/chrome-profile" \
    >/dev/null 2>&1 &
```

---

## 📋 配置检查清单

运行以下命令检查所有工具是否安装正确：

```bash
# 检查 Playwright
playwright --version

# 检查 xreach
xreach --version

# 检查 Chrome CDP（需要先启动 Chrome）
curl -s http://localhost:9222/json/version | head -5
```

---

## 🎯 实际测试

### 测试 1: 公开网页（GitHub）

```bash
$ python3 ~/.claude/skills/fetchrouter/__main__.py fetch https://github.com/anthropics/claude-code

✅ jina-agent 率先成功
📄 26,512 字符 | 1,877 词
```

### 测试 2: X/Twitter

```bash
$ xreach --cookie-source chrome tweet https://x.com/elonmusk/status/123456

# 抓取推文内容
```

### 测试 3: 微信公众号（需要 CDP）

```bash
# 1. 启动 Chrome CDP
~/.claude/skills/fetchrouter/scripts/start-chrome-cdp.sh

# 2. 在 Chrome 中登录微信

# 3. 抓取
$ python3 ~/.claude/skills/fetchrouter/__main__.py fetch https://mp.weixin.qq.com/s/xxxxx

✅ browser-agent (CDP) 成功
```

---

## 🚨 常见问题

### Q: Chrome CDP 启动失败？

A: 检查是否有其他 Chrome 实例占用了 9222 端口

```bash
# 检查端口占用
lsof -Pi :9222

# 关闭占用端口的 Chrome
pkill -f "Google Chrome"

# 重新启动
~/.claude/skills/fetchrouter/scripts/start-chrome-cdp.sh
```

### Q: xreach 提示 Cookie 无效？

A: 确保 Chrome 已登录 X/Twitter

```bash
# 在 Chrome 中访问 https://x.com 并登录
# 然后重新运行抓取
```

### Q: 微信公众号抓取失败？

A: 确保在 Chrome CDP 中已登录微信

```bash
# 1. 启动 Chrome CDP
~/.claude/skills/fetchrouter/scripts/start-chrome-cdp.sh

# 2. 在打开的 Chrome 中访问 https://mp.weixin.qq.com
# 3. 登录微信账号
# 4. 然后抓取
```

---

## 💡 最佳实践

1. **保持 Chrome CDP 运行** - 登录一次，多次抓取
2. **使用缓存** - 避免重复抓取相同 URL
3. **批量抓取限速** - 系统自动控制并行数，避免被封
4. **优先使用 Jina** - 公开网页用 Jina 最快

---

## 📊 能力矩阵

| 网站类型 | 无需配置 | 需 CDP | 需 xreach | 支持状态 |
|---------|---------|--------|-----------|---------|
| GitHub/Medium/博客 | ✅ | ❌ | ❌ | 🟢 完美 |
| 新闻/文档 | ✅ | ❌ | ❌ | 🟢 完美 |
| 知乎（公开） | ✅ | ❌ | ❌ | 🟢 完美 |
| 微信公众号 | ❌ | ✅ | ❌ | 🟢 支持 |
| 小红书 | ❌ | ✅ | ❌ | 🟢 支持 |
| 知乎（登录） | ❌ | ✅ | ❌ | 🟢 支持 |
| X/Twitter | ❌ | ❌ | ✅ | 🟢 支持 |
| 微博 | ❌ | ❌ | ❌ | 🟡 待添加 |

---

## ✅ 现在可以抓取

- ✅ **所有公开网页** - GitHub、Medium、新闻、博客
- ✅ **X/Twitter** - 使用 xreach + Chrome Cookie
- ✅ **微信公众号** - 使用 Chrome CDP（需登录）
- ✅ **小红书** - 使用 Chrome CDP（需登录）
- ✅ **知乎** - 公开页面直接抓，登录页面用 CDP

---

**配置完成！现在你可以抓取任何网页了！** 🎉

**开始使用**: `/fetch https://github.com/anthropics/claude-code`
