#!/usr/bin/env bash
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "💾 手動バックアップを実行中..."

# Redis RDB バックアップ
echo "📊 Redisデータのバックアップ中..."
docker exec conversation_redis redis-cli BGSAVE

# データディレクトリのバックアップ
echo "📁 アプリケーションデータのバックアップ中..."
tar -czf "$BACKUP_DIR/manual_backup_$TIMESTAMP.tar.gz" \
    -C ./data . \
    --exclude="*.tmp" \
    --exclude="*.log"

# RDBファイルのコピー
sleep 5  # BGSAVE完了待機
docker cp conversation_redis:/data/dump.rdb "$BACKUP_DIR/redis_manual_$TIMESTAMP.rdb"

echo "✅ バックアップ完了:"
echo "   - アプリデータ: $BACKUP_DIR/manual_backup_$TIMESTAMP.tar.gz"
echo "   - Redisデータ: $BACKUP_DIR/redis_manual_$TIMESTAMP.rdb"
