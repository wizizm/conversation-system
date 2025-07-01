#!/usr/bin/env bash
set -e

echo "🚀 Enhanced Conversation System (本地模式) + MCP Server 启动中..."

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

# 检查Python环境
echo "🐍 检查Python环境..."
if ! command -v python &> /dev/null; then
    echo "❌ 未找到Python，请先安装Python"
    exit 1
fi

echo "✅ Python版本: $(python --version)"

# 检查Redis
echo "🔴 检查Redis..."
if ! command -v redis-server &> /dev/null; then
    echo "❌ 未找到Redis，请先安装Redis"
    exit 1
fi

# 启动Redis (如果未运行)
if ! redis-cli ping > /dev/null 2>&1; then
    echo "🔄 启动Redis服务..."
    
    # 创建临时Redis配置文件，使用正确的数据目录
    cat > redis_local.conf << EOF
# Redis Local Configuration
bind 127.0.0.1
port 6379
timeout 0
tcp-keepalive 300
daemonize yes
supervised no
pidfile ./data/redis/redis.pid
loglevel notice
logfile ./logs/redis.log
databases 16
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./data/redis
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
EOF
    
    redis-server redis_local.conf
    sleep 3
    
    # 验证Redis启动
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis服务启动成功"
    else
        echo "❌ Redis服务启动失败"
        echo "📄 查看Redis日志:"
        tail -10 logs/redis.log 2>/dev/null || echo "无Redis日志"
        exit 1
    fi
else
    echo "✅ Redis服务已运行"
fi

# 启动主应用 (如果未运行)
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "🚀 启动主应用..."
    cd app
    python main.py > ../logs/app.log 2>&1 &
    APP_PID=$!
    cd ..
    
    echo "⏳ 等待主应用启动..."
    sleep 10
    
    # 验证主应用启动
    max_attempts=15
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ 主应用启动成功 (PID: $APP_PID)"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            echo "❌ 主应用启动失败"
            echo "📄 查看应用日志:"
            tail -20 logs/app.log 2>/dev/null || echo "无应用日志"
            kill $APP_PID 2>/dev/null || true
            exit 1
        fi
        
        echo "⏳ 主应用启动中... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
else
    echo "✅ 主应用已运行"
    APP_PID=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}' | head -1)
fi

# 启动MCP Server
echo "🤖 启动MCP Server..."
cd mcp-server

# 检查MCP依赖
if ! python -c "import fastmcp" > /dev/null 2>&1; then
    echo "📦 安装MCP依赖..."
    pip install -r requirements.txt
fi

# 启动MCP Server
echo "🔄 启动MCP Server进程..."
python main.py > ../logs/mcp.log 2>&1 &
MCP_PID=$!
cd ..

echo "⏳ 等待MCP Server启动..."
sleep 5

# 验证MCP Server启动
if ps -p $MCP_PID > /dev/null 2>&1; then
    echo "✅ MCP Server启动成功 (PID: $MCP_PID)"
else
    echo "❌ MCP Server启动失败"
    echo "📄 查看MCP日志:"
    tail -20 logs/mcp.log 2>/dev/null || echo "无MCP日志文件"
    exit 1
fi

# 创建PID文件记录
echo $APP_PID > logs/app.pid 2>/dev/null || true
echo $MCP_PID > logs/mcp.pid 2>/dev/null || true

# 显示启动完成信息
echo ""
echo "🎉 Enhanced Conversation System (本地模式) 启动完成！"
echo ""
echo "📊 服务状态:"
echo "   Redis: ✅ 运行中"
echo "   主应用: ✅ 运行中 (PID: $APP_PID)"
echo "   MCP Server: ✅ 运行中 (PID: $MCP_PID)"
echo ""
echo "📡 访问信息:"
echo "   主应用API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo "   Redis: localhost:6379"
echo ""
echo "🤖 MCP Server信息:"
echo "   状态: 运行中"
echo "   配置文件: mcp-server/config.json"
echo "   Claude配置: mcp-server/claude_desktop_config.json"
echo "   日志文件: logs/mcp.log"
echo ""
echo "📋 便利命令:"
echo "   查看MCP日志: tail -f logs/mcp.log"
echo "   查看应用日志: tail -f logs/app.log"
echo "   查看Redis日志: tail -f logs/redis.log"
echo "   停止服务: make stop"
echo "   查看状态: make status"
echo "   执行备份: make backup"
echo ""

# 测试备份功能（如果存在备份脚本）
if [ -f scripts/complete_backup.sh ]; then
    echo "🧪 测试备份功能..."
    if ./scripts/complete_backup.sh > /dev/null 2>&1; then
        echo "✅ 备份功能测试成功"
        
        # 显示最新备份信息
        latest_backup=$(ls -t "$KNOWLEDGE_BASE_DIR/backups"/backup_info_*.txt 2>/dev/null | head -1)
        if [ -n "$latest_backup" ]; then
            echo ""
            echo "📋 最新备份信息:"
            head -8 "$latest_backup"
        fi
    else
        echo "⚠️ 备份功能测试失败，请检查备份脚本"
    fi
fi

echo ""
echo "✅ 系统启动完成！你现在可以："
echo "   1. 配置Claude Desktop使用MCP Server"
echo "   2. 使用 'make backup' 进行数据备份"
echo "   3. 使用 'make status' 检查服务状态"
echo "   4. 查看完整文档: mcp-server/DOCKER_SETUP_GUIDE.md"

# 清理临时配置文件
trap "rm -f redis_local.conf" EXIT 