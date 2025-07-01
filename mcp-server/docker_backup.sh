#!/bin/bash
set -e

# 🐳 Docker MCP Server - 自动备份脚本
# 每小时运行，只保留最近3份备份数据

BACKUP_DIR="/app/backups"
DATA_DIR="/app/data"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
HOUR_MARK=$(date +%Y%m%d_%H)

echo "💾 [$(date)] Docker MCP Server 自动备份开始..."

# 确保备份目录存在
mkdir -p "$BACKUP_DIR"

# === 数据备份 ===
echo "📊 备份应用数据..."
if [ -d "$DATA_DIR" ] && [ "$(ls -A $DATA_DIR 2>/dev/null)" ]; then
    tar -czf "$BACKUP_DIR/mcp_data_${TIMESTAMP}.tar.gz" \
        -C "$DATA_DIR" . \
        --exclude="*.tmp" \
        --exclude="*.log" \
        2>/dev/null || echo "⚠️ 数据目录为空"
    echo "✅ 数据备份完成: mcp_data_${TIMESTAMP}.tar.gz"
else
    echo "⚠️ 数据目录不存在或为空"
fi

# === 生成备份信息 ===
echo "📋 生成备份信息..."
cat > "$BACKUP_DIR/backup_info_${TIMESTAMP}.txt" << EOF
Docker MCP Server 备份信息
==========================
备份时间: $(date)
容器ID: $(hostname)
备份类型: 自动定时备份
数据目录: $DATA_DIR

备份文件:
$(ls -lh "$BACKUP_DIR"/*${TIMESTAMP}* 2>/dev/null || echo "无备份文件")

容器信息:
- Python版本: $(python --version 2>&1)
- 磁盘使用: $(df -h /app | tail -1)
- 内存使用: $(free -h | grep Mem: || echo "N/A")

备份统计:
- 当前备份: ${TIMESTAMP}
- 备份大小: $(du -sh "$BACKUP_DIR"/*${TIMESTAMP}* 2>/dev/null | awk '{print $1}' | tr '\n' ' ')
EOF

# === 清理旧备份（只保留最近3份）===
echo "🗑️ 清理旧备份数据（保留最近3份）..."

# 按时间排序，获取所有备份文件（排除信息文件）
BACKUP_FILES=$(ls -t "$BACKUP_DIR"/mcp_data_*.tar.gz 2>/dev/null || true)

if [ -n "$BACKUP_FILES" ]; then
    BACKUP_COUNT=$(echo "$BACKUP_FILES" | wc -l)
    echo "📊 当前备份文件数量: $BACKUP_COUNT"
    
    if [ "$BACKUP_COUNT" -gt 3 ]; then
        # 保留最新的3个，删除其余的
        OLD_BACKUPS=$(echo "$BACKUP_FILES" | tail -n +4)
        
        for backup in $OLD_BACKUPS; do
            # 提取时间戳
            backup_timestamp=$(basename "$backup" | sed 's/mcp_data_\(.*\)\.tar\.gz/\1/')
            
            echo "🗑️ 删除旧备份: $backup (时间戳: $backup_timestamp)"
            rm -f "$backup"
            
            # 同时删除对应的信息文件
            info_file="$BACKUP_DIR/backup_info_${backup_timestamp}.txt"
            if [ -f "$info_file" ]; then
                echo "🗑️ 删除旧备份信息: $info_file"
                rm -f "$info_file"
            fi
        done
        
        REMAINING_COUNT=$(ls -1 "$BACKUP_DIR"/mcp_data_*.tar.gz 2>/dev/null | wc -l)
        echo "✅ 清理完成，剩余备份数量: $REMAINING_COUNT"
    else
        echo "✅ 备份数量未超过3个，无需清理"
    fi
else
    echo "⚠️ 未找到备份文件"
fi

# === 备份状态报告 ===
echo ""
echo "📋 备份状态报告:"
echo "================="
echo "✅ 备份时间: $(date)"
echo "📁 备份目录: $BACKUP_DIR"
echo "📊 当前备份文件:"
ls -lht "$BACKUP_DIR"/mcp_data_*.tar.gz 2>/dev/null | head -3 || echo "  无备份文件"

echo ""
echo "💾 磁盘使用情况:"
du -sh "$BACKUP_DIR" 2>/dev/null || echo "  无法获取磁盘使用信息"

echo ""
echo "🎯 备份保留策略: 最近3份数据"
echo "⏰ 下次备份时间: $(date -d '+1 hour' '+%Y-%m-%d %H:00:00')"
echo ""
echo "✅ [$(date)] Docker MCP Server 自动备份完成！"

# === 记录到系统日志 ===
logger "Docker MCP Server: 自动备份完成 - 备份ID: $TIMESTAMP" 