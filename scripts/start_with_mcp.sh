#!/usr/bin/env bash
set -e

echo "🚀 Enhanced Conversation System with MCP Server 启动中..."

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 项目目录: $PROJECT_DIR"

# 切换到项目目录
cd "$PROJECT_DIR"

# 创建必要的目录
KNOWLEDGE_BASE_DIR="/Users/linwenjie/Documents/知识库/conversations"
for dir in "$KNOWLEDGE_BASE_DIR/data/redis" "$KNOWLEDGE_BASE_DIR/data/app" "$KNOWLEDGE_BASE_DIR/logs" "$KNOWLEDGE_BASE_DIR/backups" "$KNOWLEDGE_BASE_DIR"; do
    if [ ! -d "$dir" ]; then
        echo "📁 创建目录: $dir"
        mkdir -p "$dir"
    fi
done

# 创建项目本地软链接（为了兼容相对路径）
for dir in data logs backups conversations; do
    if [ ! -e "$dir" ]; then
        case $dir in
            "conversations")
                ln -sf "$KNOWLEDGE_BASE_DIR" "$dir"
                ;;
            "data")
                ln -sf "$KNOWLEDGE_BASE_DIR/data" "$dir"
                ;;
            "logs") 
                ln -sf "$KNOWLEDGE_BASE_DIR/logs" "$dir"
                ;;
            "backups")
                ln -sf "$KNOWLEDGE_BASE_DIR/backups" "$dir"
                ;;
        esac
        echo "🔗 创建软链接: $dir -> $KNOWLEDGE_BASE_DIR/$dir"
    fi
done

# 检查Docker Compose版本
echo "🐳 检查Docker环境..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ 未找到Docker Compose，请先安装Docker"
    exit 1
fi

echo "✅ 使用命令: $COMPOSE_CMD"

# 停止现有服务（如果存在）
echo "🛑 停止现有服务..."
$COMPOSE_CMD down 2>/dev/null || true

# 构建并启动所有服务（包括MCP Server）
echo "🏗️ 构建并启动服务..."
$COMPOSE_CMD up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 健康检查
echo "🏥 执行健康检查..."
max_attempts=30
attempt=1

# 检查Redis
while [ $attempt -le $max_attempts ]; do
    if $COMPOSE_CMD exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis服务正常"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Redis服务启动失败"
        $COMPOSE_CMD logs redis
        exit 1
    fi
    
    echo "⏳ Redis启动中... ($attempt/$max_attempts)"
    sleep 2
    ((attempt++))
done

# 检查主应用
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 主应用服务正常"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ 主应用服务启动失败"
        $COMPOSE_CMD logs conversation_app
        exit 1
    fi
    
    echo "⏳ 主应用启动中... ($attempt/$max_attempts)"
    sleep 2
    ((attempt++))
done

# 检查MCP Server
attempt=1
while [ $attempt -le $max_attempts ]; do
    if $COMPOSE_CMD ps mcp_server | grep -q "Up"; then
        echo "✅ MCP Server服务正常"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ MCP Server服务启动失败"
        $COMPOSE_CMD logs mcp_server
        exit 1
    fi
    
    echo "⏳ MCP Server启动中... ($attempt/$max_attempts)"
    sleep 2
    ((attempt++))
done

# 显示服务状态
echo ""
echo "🎉 所有服务启动完成！"
echo ""
echo "📊 服务状态:"
$COMPOSE_CMD ps

echo ""
echo "📡 访问信息:"
echo "   主应用API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs" 
echo "   Redis: localhost:6379"
echo ""
echo "🤖 MCP Server信息:"
echo "   状态: $($COMPOSE_CMD ps mcp_server --format 'table {{.State}}')"
echo "   自动备份: 每小时执行"
echo "   备份保留: 最近3份"
echo "   备份目录: $KNOWLEDGE_BASE_DIR/backups/"
echo ""
echo "📋 便利命令:"
echo "   查看日志: $COMPOSE_CMD logs -f [service_name]"
echo "   查看备份: ls -la \"$KNOWLEDGE_BASE_DIR/backups/\""
echo "   手动备份: $COMPOSE_CMD exec mcp_server /app/docker_backup.sh"
echo "   停止服务: $COMPOSE_CMD down"
echo "   重启服务: $COMPOSE_CMD restart [service_name]"
echo ""
echo "🔍 监控命令:"
echo "   MCP日志: $COMPOSE_CMD logs -f mcp_server"
echo "   备份日志: $COMPOSE_CMD exec mcp_server tail -f /app/logs/backup.log"
echo "   服务状态: $COMPOSE_CMD ps"
echo ""

# 检查MCP备份功能
echo "🧪 测试MCP备份功能..."
if $COMPOSE_CMD exec -T mcp_server /app/docker_backup.sh > /dev/null 2>&1; then
    echo "✅ MCP自动备份功能测试成功"
    echo "📁 备份文件已生成到 $KNOWLEDGE_BASE_DIR/backups/ 目录"
    
    # 显示最新备份信息
    latest_backup=$(ls -t "$KNOWLEDGE_BASE_DIR/backups"/backup_info_*.txt 2>/dev/null | head -1)
    if [ -n "$latest_backup" ]; then
        echo ""
        echo "📋 最新备份信息:"
        cat "$latest_backup" | head -10
    fi
else
    echo "⚠️ MCP备份功能测试失败，请检查日志"
    $COMPOSE_CMD logs mcp_server | tail -20
fi

echo ""
echo "✅ Enhanced Conversation System with MCP Server 启动完成！" 