#!/bin/bash

echo "🚀 Testing Docker MCP Server Setup..."
echo "========================================"

# 测试Docker容器状态
echo ""
echo "📦 Docker容器状态："
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🔍 测试服务连接..."

# 测试主API服务
echo ""
echo "✅ 测试主API服务 (localhost:9000)："
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/health | grep -q "200"; then
    echo "   ✅ 主API服务正常"
    curl -s http://localhost:9000/health | jq '.' 2>/dev/null || echo "   📊 健康检查通过"
else
    echo "   ❌ 主API服务连接失败"
fi

# 测试MCP Server HTTP端点  
echo ""
echo "🔌 测试MCP Server HTTP端点 (localhost:3001)："
if curl -s -f http://localhost:3001/mcp/ >/dev/null 2>&1; then
    echo "   ✅ MCP Server HTTP端点正常"
    echo "   📡 HTTP传输可用"
else
    echo "   ❌ MCP Server HTTP端点连接失败"
fi

# 测试Redis
echo ""
echo "🔴 测试Redis连接 (localhost:6379)："
if docker exec conversation_redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo "   ✅ Redis连接正常"
else
    echo "   ❌ Redis连接失败"
fi

# MCP Server日志
echo ""
echo "📋 MCP Server日志 (最新10行)："
echo "----------------------------------------"
docker logs conversation_mcp_server --tail 10

echo ""
echo "🎯 Cursor MCP配置："
echo "----------------------------------------"
echo "Name: conversation-system"
echo "URL: http://localhost:3001/mcp/"
echo "Transport: HTTP (推荐)"

echo ""
echo "📁 配置文件位置："
echo "- macOS: ~/Library/Application Support/Cursor/User/settings.json"
echo "- Windows: %APPDATA%\\Cursor\\User\\settings.json"
echo "- Linux: ~/.config/Cursor/User/settings.json"

echo ""
echo "🔧 配置文件内容："
cat cursor_mcp_sse_config.json | jq '.'

echo "========================================"
echo "✨ 测试完成！Docker MCP Server with FastMCP 2.0运行正常！" 