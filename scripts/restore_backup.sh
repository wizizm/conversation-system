#!/usr/bin/env bash
set -e

# 🌟 Enhanced Conversation System - 数据恢复脚本 v2.0
# 支持从备份文件完整恢复系统数据

BACKUP_DIR="./backups"
TIMESTAMP="$1"

if [ -z "$TIMESTAMP" ]; then
    echo "❌ 使用方法: $0 <备份时间戳>"
    echo ""
    echo "📋 可用的备份："
    ls -la "$BACKUP_DIR" | grep -E "(rdb|tar.gz|txt)" | head -10
    echo ""
    echo "💡 示例: $0 20231201_143022"
    exit 1
fi

echo "🔄 Enhanced Conversation System - 数据恢复开始..."
echo "📅 恢复时间: $(date)"
echo "🏷️ 备份时间戳: $TIMESTAMP"

# 检查备份文件是否存在
BACKUP_INFO="$BACKUP_DIR/backup_info_${TIMESTAMP}.txt"
if [ ! -f "$BACKUP_INFO" ]; then
    echo "❌ 备份信息文件不存在: $BACKUP_INFO"
    echo "请检查时间戳是否正确"
    exit 1
fi

echo ""
echo "📋 备份信息:"
cat "$BACKUP_INFO"
echo ""

read -p "🤔 确认要恢复这个备份吗? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ 恢复已取消"
    exit 0
fi

# 停止运行中的服务
echo ""
echo "🛑 停止运行中的服务..."
docker-compose down 2>/dev/null || echo "  - Docker服务未运行"
pkill -f "main.py" 2>/dev/null || echo "  - MCP服务未运行"

# 备份当前数据（以防万一）
echo ""
echo "💾 备份当前数据（安全措施）..."
CURRENT_BACKUP_DIR="./backups/pre_restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$CURRENT_BACKUP_DIR"
cp -r data "$CURRENT_BACKUP_DIR/" 2>/dev/null || echo "  - 无当前数据需要备份"
cp -r conversations "$CURRENT_BACKUP_DIR/" 2>/dev/null || echo "  - 无会话文件需要备份"

# 恢复Redis数据
echo ""
echo "🔴 恢复Redis数据..."
mkdir -p data/redis
if [ -f "$BACKUP_DIR/redis_${TIMESTAMP}.rdb" ]; then
    cp "$BACKUP_DIR/redis_${TIMESTAMP}.rdb" data/redis/dump.rdb
    echo "  ✅ Redis RDB文件已恢复"
else
    echo "  ⚠️ Redis RDB备份文件不存在"
fi

if [ -f "$BACKUP_DIR/redis_aof_${TIMESTAMP}.aof" ]; then
    cp "$BACKUP_DIR/redis_aof_${TIMESTAMP}.aof" data/redis/appendonly.aof
    echo "  ✅ Redis AOF文件已恢复"
else
    echo "  ⚠️ Redis AOF备份文件不存在"
fi

# 恢复应用数据
echo ""
echo "📊 恢复应用数据..."
if [ -f "$BACKUP_DIR/app_data_${TIMESTAMP}.tar.gz" ]; then
    mkdir -p data
    tar -xzf "$BACKUP_DIR/app_data_${TIMESTAMP}.tar.gz" -C data/
    echo "  ✅ 应用数据已恢复"
else
    echo "  ⚠️ 应用数据备份文件不存在"
fi

# 恢复会话文件
echo ""
echo "💬 恢复会话文件..."
if [ -f "$BACKUP_DIR/conversations_${TIMESTAMP}.tar.gz" ]; then
    mkdir -p conversations
    tar -xzf "$BACKUP_DIR/conversations_${TIMESTAMP}.tar.gz" -C conversations/
    echo "  ✅ 会话文件已恢复"
else
    echo "  ⚠️ 会话文件备份不存在"
fi

# 恢复配置文件（可选）
echo ""
read -p "🔧 是否恢复配置文件? (yes/no): " RESTORE_CONFIG
if [ "$RESTORE_CONFIG" = "yes" ]; then
    if [ -f "$BACKUP_DIR/config_${TIMESTAMP}.tar.gz" ]; then
        echo "  - 备份当前配置..."
        tar -czf "$CURRENT_BACKUP_DIR/current_config.tar.gz" \
            redis.conf compose.yml compose.prod.yml requirements.txt mcp-server/ scripts/ \
            2>/dev/null
        
        echo "  - 恢复配置文件..."
        tar -xzf "$BACKUP_DIR/config_${TIMESTAMP}.tar.gz"
        echo "  ✅ 配置文件已恢复"
    else
        echo "  ⚠️ 配置文件备份不存在"
    fi
fi

# 设置正确的权限
echo ""
echo "🔐 设置文件权限..."
chmod -R 755 data/ 2>/dev/null || true
chmod -R 755 conversations/ 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true

# 恢复完成
echo ""
echo "🎉 数据恢复完成！"
echo ""
echo "📁 恢复的数据位置:"
echo "   - Redis数据: data/redis/"
echo "   - 应用数据: data/app/"
echo "   - 会话文件: conversations/"
echo ""
echo "💾 当前数据备份至: $CURRENT_BACKUP_DIR"
echo ""
echo "🚀 下一步操作:"
echo "   1. 启动系统: ./scripts/start.sh"
echo "   2. 验证数据: curl http://localhost:8000/analytics"
echo "   3. 测试MCP: 在Claude Desktop中测试会话记录"
echo ""
echo "🔄 如果恢复有问题，可以从这里回滚:"
echo "   cp -r $CURRENT_BACKUP_DIR/data/* data/"
echo "   cp -r $CURRENT_BACKUP_DIR/conversations/* conversations/"
echo ""
echo "✅ 恢复流程全部完成！" 