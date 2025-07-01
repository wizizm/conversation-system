#!/usr/bin/env bash
set -e

# 🔍 Docker MCP Server 备份监控脚本
# 用于监控、管理和报告MCP Server的自动备份状态

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"

echo "🔍 Docker MCP Server 备份监控器"
echo "=================================="

# 检查Docker Compose命令
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ 未找到Docker Compose"
    exit 1
fi

cd "$PROJECT_DIR"

# 检查MCP Server状态
echo "🤖 MCP Server状态检查:"
if $COMPOSE_CMD ps mcp_server | grep -q "Up"; then
    echo "✅ MCP Server 运行中"
    
    # 获取容器信息
    CONTAINER_INFO=$($COMPOSE_CMD ps mcp_server --format "table {{.State}}\t{{.Status}}")
    echo "📊 容器状态: $CONTAINER_INFO"
else
    echo "❌ MCP Server 未运行"
    echo "💡 启动命令: ./scripts/start_with_mcp.sh"
    exit 1
fi

echo ""

# 检查备份目录
echo "📁 备份目录检查:"
if [ -d "$BACKUP_DIR" ]; then
    echo "✅ 备份目录存在: $BACKUP_DIR"
    
    # 统计备份文件
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/mcp_data_*.tar.gz 2>/dev/null | wc -l)
    INFO_COUNT=$(ls -1 "$BACKUP_DIR"/backup_info_*.txt 2>/dev/null | wc -l)
    
    echo "📊 备份文件统计:"
    echo "   数据备份文件: $BACKUP_COUNT 个"
    echo "   信息文件: $INFO_COUNT 个"
    echo "   目录大小: $(du -sh "$BACKUP_DIR" | awk '{print $1}')"
else
    echo "❌ 备份目录不存在"
    mkdir -p "$BACKUP_DIR"
    echo "✅ 已创建备份目录"
fi

echo ""

# 显示最近备份信息
echo "📋 最近备份信息:"
LATEST_BACKUPS=$(ls -t "$BACKUP_DIR"/mcp_data_*.tar.gz 2>/dev/null | head -3)

if [ -n "$LATEST_BACKUPS" ]; then
    echo "🕒 最近3次备份:"
    for backup in $LATEST_BACKUPS; do
        backup_time=$(basename "$backup" | sed 's/mcp_data_\(.*\)\.tar\.gz/\1/')
        backup_size=$(du -sh "$backup" | awk '{print $1}')
        
        # 转换时间戳为可读格式
        if [[ "$backup_time" =~ ^[0-9]{8}_[0-9]{6}$ ]]; then
            readable_time=$(echo "$backup_time" | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)_\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/')
            echo "   ✅ $readable_time ($backup_size)"
        else
            echo "   ✅ $backup_time ($backup_size)"
        fi
    done
else
    echo "❌ 未找到备份文件"
fi

echo ""

# 检查备份日志
echo "📝 备份日志检查:"
if $COMPOSE_CMD exec -T mcp_server test -f /app/logs/backup.log 2>/dev/null; then
    echo "✅ 备份日志存在"
    
    # 显示最近的日志条目
    echo "📄 最近的备份日志（最后10行）:"
    $COMPOSE_CMD exec -T mcp_server tail -10 /app/logs/backup.log 2>/dev/null || echo "无法读取日志"
else
    echo "⚠️ 备份日志不存在或无法访问"
fi

echo ""

# 检查定时任务
echo "⏰ 定时任务检查:"
if $COMPOSE_CMD exec -T mcp_server crontab -l 2>/dev/null | grep -q "docker_backup.sh"; then
    echo "✅ 备份定时任务已配置"
    echo "📅 任务配置:"
    $COMPOSE_CMD exec -T mcp_server crontab -l 2>/dev/null | grep "docker_backup.sh"
else
    echo "❌ 备份定时任务未配置"
fi

echo ""

# 显示操作菜单
echo "🛠️ 可用操作:"
echo "1. 手动执行备份"
echo "2. 查看备份详情"
echo "3. 清理旧备份"
echo "4. 查看实时日志"
echo "5. 重启MCP Server"
echo "6. 退出"

echo ""
read -p "请选择操作 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🔄 执行手动备份..."
        if $COMPOSE_CMD exec -T mcp_server /app/docker_backup.sh; then
            echo "✅ 手动备份完成"
            echo "📁 查看备份: ls -la $BACKUP_DIR"
        else
            echo "❌ 手动备份失败"
        fi
        ;;
    2)
        echo ""
        echo "📊 备份详细信息:"
        echo "=================="
        ls -lah "$BACKUP_DIR"/ 2>/dev/null || echo "备份目录为空"
        
        echo ""
        echo "📋 最新备份信息文件:"
        latest_info=$(ls -t "$BACKUP_DIR"/backup_info_*.txt 2>/dev/null | head -1)
        if [ -n "$latest_info" ]; then
            cat "$latest_info"
        else
            echo "未找到备份信息文件"
        fi
        ;;
    3)
        echo ""
        echo "🗑️ 清理旧备份..."
        echo "当前备份数量: $(ls -1 "$BACKUP_DIR"/mcp_data_*.tar.gz 2>/dev/null | wc -l)"
        
        read -p "确认清理超过3个的旧备份? (y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            $COMPOSE_CMD exec -T mcp_server /app/docker_backup.sh >/dev/null
            echo "✅ 备份清理完成"
        else
            echo "❌ 清理已取消"
        fi
        ;;
    4)
        echo ""
        echo "📄 实时查看备份日志 (Ctrl+C 退出):"
        $COMPOSE_CMD exec mcp_server tail -f /app/logs/backup.log
        ;;
    5)
        echo ""
        echo "🔄 重启MCP Server..."
        $COMPOSE_CMD restart mcp_server
        
        echo "⏳ 等待服务启动..."
        sleep 10
        
        if $COMPOSE_CMD ps mcp_server | grep -q "Up"; then
            echo "✅ MCP Server重启成功"
        else
            echo "❌ MCP Server重启失败"
            $COMPOSE_CMD logs mcp_server | tail -20
        fi
        ;;
    6)
        echo "👋 退出监控器"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 操作完成" 