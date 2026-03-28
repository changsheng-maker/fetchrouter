#!/bin/bash
# 启动 Chrome 并开启远程调试端口（用于 FetchRouter CDP 模式）

CHROME_APP="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
REMOTE_DEBUGGING_PORT=9222

# 检查 Chrome 是否已在运行远程调试
if lsof -Pi :$REMOTE_DEBUGGING_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome 远程调试已在端口 $REMOTE_DEBUGGING_PORT 运行"
    echo "📝 访问 http://localhost:$REMOTE_DEBUGGING_PORT/json 查看可连接的页面"
    exit 0
fi

# 启动 Chrome 并开启远程调试
echo "🚀 正在启动 Chrome 远程调试..."
echo "📍 端口: $REMOTE_DEBUGGING_PORT"
echo ""

"$CHROME_APP" \
    --remote-debugging-port=$REMOTE_DEBUGGING_PORT \
    --no-first-run \
    --no-default-browser-check \
    --user-data-dir="$HOME/.fetchrouter/chrome-profile" \
    >/dev/null 2>&1 &

sleep 2

# 检查是否启动成功
if lsof -Pi :$REMOTE_DEBUGGING_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Chrome 远程调试启动成功"
    echo "📍 端口: $REMOTE_DEBUGGING_PORT"
    echo ""
    echo "💡 使用 FetchRouter 抓取需要登录的网站："
    echo "   /fetch https://mp.weixin.qq.com/s/xxxxx"
    echo "   /fetch https://xiaohongshu.com/explore/xxxxx"
    echo ""
    echo "⚠️  注意：请在 Chrome 中先登录相关网站"
else
    echo "❌ Chrome 启动失败"
    exit 1
fi
