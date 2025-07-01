#!/usr/bin/env bash
set -e

# 🎯 Cursor MCP Server 启动脚本
# 专用于Cursor调用的MCP Server启动器

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MCP_DIR="$PROJECT_DIR/mcp-server"

# 设置环境变量
export PYTHONPATH="$MCP_DIR"
export CONVERSATION_API_URL="${CONVERSATION_API_URL:-http://localhost:9000}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

# 切换到MCP目录
cd "$MCP_DIR"

# 检查主API是否运行
echo "🔍 检查API服务..." >&2
if ! curl -s "$CONVERSATION_API_URL/health" > /dev/null 2>&1; then
    echo "❌ 主API服务未运行，请先启动: make start-all" >&2
    exit 1
fi
echo "✅ API服务正常" >&2

# 启动MCP Server
echo "🚀 启动MCP Server for Cursor..." >&2
exec python main.py 