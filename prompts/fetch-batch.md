# /fetch-batch 命令 - 批量抓取

## 用法

```
/fetch-batch <urls> [选项]
```

## 参数

- `urls` - URL 列表，支持以下格式：
  - 逗号分隔: `url1,url2,url3`
  - 文件路径: `@urls.txt`
  - 多行文本

## 选项

- `--parallel <n>` - 并行数（默认 3）
- `--output <path>` - 保存结果到文件
- `--format <format>` - 输出格式 (markdown/json/csv)
- `--filter <type>` - 只抓取特定类型 (github,medium,news...)

## 执行流程

1. **解析 URL 列表**
   - 检测输入格式
   - 去重和验证

2. **URL 分组**
   - 按域名分组
   - 同域名串行（防封）
   - 不同域名并行

3. **批量执行**
   - 显示进度条
   - 实时显示结果
   - 失败自动跳过

4. **汇总报告**
   - 统计成功率
   - 列出失败项
   - 导出结果

## 输出示例

### 标准输出

```
🔄 批量抓取 5 个 URL
并行数: 3 | 输出格式: markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/5] 🔗 github.com/anthropics/claude-code
      📋 fast_first → jina-agent
      ✅ 成功 (643ms) | 26,512 字符

[2/5] 🔗 x.com/elonmusk/status/123
      📋 social_first → social-agent
      ❌ 失败: xreach 未安装
      ⏭️  降级 → browser-agent
      ✅ 成功 (2.1s) | 1,234 字符

[3/5] 🔗 medium.com/article
      📋 fast_first → jina-agent
      ✅ 成功 (412ms) | 5,678 字符

[4/5] 🔗 mp.weixin.qq.com/s/xx
      📋 login_first → browser-agent
      ❌ 失败: 需要登录
      💡 跳过（登录失败）

[5/5] 🔗 techcrunch.com/news
      📋 fast_first → jina-agent
      ✅ 成功 (523ms) | 3,456 字符

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 汇总报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计: 5 个 URL
成功: 3 个 (60%)
失败: 2 个

⏱️  总耗时: 8.5s
平均耗时: 1.7s

按 Agent 统计:
  • jina-agent: 3 成功, 0 失败
  • browser-agent: 0 成功, 1 失败
  • social-agent: 0 成功, 1 失败 (降级后成功)

按网站类型统计:
  • github: 1/1 成功
  • x_twitter: 1/1 成功 (降级后)
  • medium: 1/1 成功
  • wechat: 0/1 失败 (需登录)

失败详情:
  1. mp.weixin.qq.com/s/xx
     原因: 需要登录
     建议: 使用 CDP 模式或手动复制内容

💾 结果已保存: /Users/mac/Downloads/fetch-results-20260328-143022.json
```

### 文件输出 (JSON)

```json
{
  "meta": {
    "total": 5,
    "success": 3,
    "failed": 2,
    "duration_ms": 8500,
    "timestamp": "2026-03-28T14:30:22+08:00"
  },
  "results": [
    {
      "url": "https://github.com/anthropics/claude-code",
      "success": true,
      "agent": "jina-agent",
      "duration_ms": 643,
      "content": {...}
    },
    {...}
  ],
  "failures": [
    {
      "url": "https://mp.weixin.qq.com/s/xx",
      "error": "需要登录",
      "suggestion": "使用 CDP 模式"
    }
  ]
}
```

## 特殊场景

### 大列表优化

如果 URL 数量 > 20：

```
🔄 批量抓取 50 个 URL
⚠️  大列表优化: 将分 5 批处理（每批 10 个）

第 1/5 批...
[1/10] ✅ ...
...

第 2/5 批...
...

💡 提示: 大量抓取建议保存到文件 --output results.json
```

### 重复 URL 检测

```
🔄 批量抓取 10 个 URL
⚠️  检测到 3 个重复 URL，已自动去重
实际抓取: 7 个唯一 URL
```

### 中断恢复

```
🔄 批量抓取 100 个 URL
⏸️  用户中断 (Ctrl+C)

💾 已保存进度: 23/100 完成
📁 进度文件: ~/.fetchrouter/batch-progress-xxx.json

💡 恢复抓取:
   /fetch-batch @~/.fetchrouter/batch-progress-xxx.json --resume
```

## 技术实现

```python
async def fetch_batch(urls: List[str], options: dict):
    # 去重
    unique_urls = list(set(urls))

    # 分组（同域名放一起）
    groups = group_by_domain(unique_urls)

    results = []
    semaphore = asyncio.Semaphore(options.get("parallel", 3))

    async def fetch_one(url):
        async with semaphore:
            result = await fetch_url(url)
            # 实时显示进度
            print_progress(result)
            return result

    # 执行（同域名串行，不同域名并行）
    for group in groups:
        if len(group) == 1:
            # 单 URL，并行执行
            results.append(await fetch_one(group[0]))
        else:
            # 同域名，串行执行
            for url in group:
                results.append(await fetch_one(url))

    # 生成报告
    return generate_report(results)
```

## 最佳实践

1. **控制并行数** - 默认 3，根据网络情况调整
2. **同域名限速** - 自动串行，避免被封
3. **分批处理** - >20 个 URL 自动分批
4. **保存结果** - 使用 `--output` 保存到文件
5. **过滤类型** - 使用 `--filter` 只抓取特定类型

## 常见用法

```bash
# 从逗号分隔的列表
/fetch-batch url1,url2,url3

# 从文件
/fetch-batch @~/urls.txt

# 并行 5 个，JSON 输出
/fetch-batch @urls.txt --parallel 5 --format json --output results.json

# 只抓取 GitHub 链接
/fetch-batch @mixed-urls.txt --filter github

# 恢复中断的任务
/fetch-batch @progress.json --resume
```
