# /fetch-config 命令 - 配置管理

## 用法

```
/fetch-config <key> [value]
/fetch-config --list
/fetch-config --reset
```

## 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `cache-duration` | 300 | 缓存时长（秒） |
| `default-output` | markdown | 默认输出格式 |
| `max-content-length` | 8000 | 显示内容最大长度 |
| `timeout` | 30 | 默认超时（秒） |
| `parallel` | 3 | 批量并行数 |
| `auto-detect-url` | true | 自动检测消息中的 URL |
| `save-directory` | ~/Downloads | 默认保存目录 |

## 命令示例

### 查看配置

```
用户: /fetch-config --list

你:
📋 FetchRouter 配置
━━━━━━━━━━━━━━━━━━━━━━━━━━

cache-duration: 300 (5分钟)
default-output: markdown
max-content-length: 8000
timeout: 30
parallel: 3
auto-detect-url: true
save-directory: /Users/mac/Downloads

💡 修改配置:
   /fetch-config <key> <value>
```

### 修改配置

```
用户: /fetch-config cache-duration 600

你:
✅ cache-duration 已更新
   旧值: 300 (5分钟)
   新值: 600 (10分钟)
```

### 重置配置

```
用户: /fetch-config --reset

你:
⚠️  确定要重置所有配置为默认值吗？
   输入 "yes" 确认重置

用户: yes

你:
✅ 配置已重置为默认值
```

## 配置说明

### cache-duration

缓存抓取结果，避免重复请求。

```
/fetch-config cache-duration 600
```

- 0: 禁用缓存
- 300: 5分钟（默认）
- 3600: 1小时
- 86400: 1天

### default-output

设置默认输出格式。

```
/fetch-config default-output json
```

- markdown: Markdown 格式（默认）
- json: JSON 格式
- text: 纯文本

### max-content-length

控制显示内容的最大长度，超过则截断。

```
/fetch-config max-content-length 10000
```

### timeout

单次抓取的超时时间（秒）。

```
/fetch-config timeout 45
```

### parallel

批量抓取时的并行数。

```
/fetch-config parallel 5
```

### auto-detect-url

自动检测用户消息中的 URL 并提示抓取。

```
/fetch-config auto-detect-url false
```

### save-directory

默认保存抓取结果的目录。

```
/fetch-config save-directory ~/Documents/WebContent
```

## 配置文件位置

```
~/.claude/skills/fetchrouter/config/settings.json
```

## 配置优先级

命令行参数 > 用户配置 > 默认配置

```
/fetch <url> --no-cache  # 命令行覆盖配置
```
