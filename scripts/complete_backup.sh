#!/usr/bin/env bash
set -e

# 🌟 Enhanced Conversation System - 完整备份脚本 v2.0
# 支持Docker和非Docker环境的智能备份

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR=$(pwd)

echo "💾 Enhanced Conversation System - 完整备份开始..."
echo "📅 备份时间: $(date)"
echo "📁 项目目录: $PROJECT_DIR"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 检查Docker状态
DOCKER_RUNNING=false
if docker ps -q --filter "name=conversation_redis" | grep -q .; then
    DOCKER_RUNNING=true
    echo "🐳 Docker环境检测: 运行中"
else
    echo "📦 Docker环境检测: 未运行（使用文件系统备份）"
fi

# === Redis数据备份 ===
echo ""
echo "🔴 Redis数据备份中..."
if [ "$DOCKER_RUNNING" = true ]; then
    # Docker环境下的Redis备份
    echo "  - 触发Redis后台保存..."
    docker exec conversation_redis redis-cli BGSAVE
    
    echo "  - 等待保存完成..."
    sleep 3
    
    echo "  - 复制Redis数据文件..."
    docker cp conversation_redis:/data/dump.rdb "$BACKUP_DIR/redis_${TIMESTAMP}.rdb" 2>/dev/null || echo "    ⚠️ dump.rdb不存在"
    docker cp conversation_redis:/data/appendonly.aof "$BACKUP_DIR/redis_aof_${TIMESTAMP}.aof" 2>/dev/null || echo "    ⚠️ appendonly.aof不存在"
    
    echo "  ✅ Docker Redis备份完成"
else
    # 文件系统备份
    if [ -d "data/redis" ]; then
        echo "  - 备份Redis数据文件..."
        cp data/redis/dump.rdb "$BACKUP_DIR/redis_${TIMESTAMP}.rdb" 2>/dev/null || echo "    ⚠️ dump.rdb不存在"
        cp data/redis/appendonly.aof "$BACKUP_DIR/redis_aof_${TIMESTAMP}.aof" 2>/dev/null || echo "    ⚠️ appendonly.aof不存在"
        echo "  ✅ 文件系统Redis备份完成"
    else
        echo "  ⚠️ Redis数据目录不存在"
    fi
fi

# === 应用数据备份 ===
echo ""
echo "📊 应用数据备份中..."
if [ -d "data" ]; then
    tar -czf "$BACKUP_DIR/app_data_${TIMESTAMP}.tar.gz" \
        -C data . \
        --exclude="*.tmp" \
        --exclude="*.log" \
        2>/dev/null || echo "  ⚠️ 应用数据目录为空"
    echo "  ✅ 应用数据备份完成"
else
    echo "  ⚠️ 应用数据目录不存在"
fi

# === 会话文件备份 ===
echo ""
echo "💬 会话文件备份中..."
if [ -d "conversations" ]; then
    tar -czf "$BACKUP_DIR/conversations_${TIMESTAMP}.tar.gz" \
        -C conversations . \
        2>/dev/null || echo "  ⚠️ 会话目录为空"
    echo "  ✅ 会话文件备份完成"  
else
    echo "  ⚠️ 会话文件目录不存在（将自动创建）"
    mkdir -p conversations
fi

# === 配置文件备份 ===
echo ""
echo "⚙️ 配置文件备份中..."
tar -czf "$BACKUP_DIR/config_${TIMESTAMP}.tar.gz" \
    redis.conf \
    compose.yml \
    compose.prod.yml \
    requirements.txt \
    mcp-server/ \
    scripts/ \
    2>/dev/null
echo "  ✅ 配置文件备份完成"

# === 生成备份信息 ===
echo ""
echo "📋 生成备份信息..."
cat > "$BACKUP_DIR/backup_info_${TIMESTAMP}.txt" << EOF
Enhanced Conversation System - 备份信息
========================================
备份时间: $(date)
备份版本: v2.0
项目路径: $PROJECT_DIR
Docker状态: $DOCKER_RUNNING

备份文件清单:
$(ls -lh "$BACKUP_DIR"/*${TIMESTAMP}* 2>/dev/null || echo "无备份文件")

系统信息:
- Python版本: $(python3 --version 2>/dev/null || echo "未安装")
- Docker版本: $(docker --version 2>/dev/null || echo "未安装")
- 磁盘空间: $(df -h . | tail -1)

使用恢复脚本恢复:
./scripts/restore_backup.sh $TIMESTAMP
EOF

# === 备份完成报告 ===
echo ""
echo "🎉 备份完成！"
echo ""
echo "📁 备份文件位置: $BACKUP_DIR/"
echo "📋 备份清单:"
ls -lh "$BACKUP_DIR"/*${TIMESTAMP}* 2>/dev/null || echo "  无备份文件生成"
echo ""
echo "💡 恢复方法:"
echo "   ./scripts/restore_backup.sh $TIMESTAMP"
echo ""
echo "🗑️ 清理旧备份:"
echo "   find $BACKUP_DIR -name '*.rdb' -mtime +7 -delete"
echo "   find $BACKUP_DIR -name '*.tar.gz' -mtime +30 -delete"
echo ""

# === 自动清理旧备份 ===
if [ "$(find "$BACKUP_DIR" -name '*.rdb' -mtime +7 | wc -l)" -gt 0 ]; then
    echo "🧹 清理7天前的Redis备份..."
    find "$BACKUP_DIR" -name '*.rdb' -mtime +7 -delete
    find "$BACKUP_DIR" -name '*.aof' -mtime +7 -delete
fi

if [ "$(find "$BACKUP_DIR" -name '*.tar.gz' -mtime +30 | wc -l)" -gt 0 ]; then
    echo "🧹 清理30天前的应用备份..."
    find "$BACKUP_DIR" -name 'app_data_*.tar.gz' -mtime +30 -delete
    find "$BACKUP_DIR" -name 'conversations_*.tar.gz' -mtime +30 -delete
    find "$BACKUP_DIR" -name 'config_*.tar.gz' -mtime +30 -delete
fi

echo "✅ 备份流程全部完成！" 