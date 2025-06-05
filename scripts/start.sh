#!/usr/bin/env bash
set -e

echo "🚀 会話システムを起動中..."

# ディレクトリ存在確認
for dir in data/redis data/app logs; do
    if [ ! -d "$dir" ]; then
        echo "📁 $dir ディレクトリを作成"
        mkdir -p "$dir"
    fi
done

# Docker Compose起動
echo "🐳 Dockerコンテナを起動中..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

# サービス起動待機
echo "⏳ サービスの起動を待機中..."
sleep 10

# ヘルスチェック
echo "🏥 ヘルスチェック実行中..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ サービスが正常に起動しました"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ サービス起動に失敗しました"
        echo "ログを確認してください:"
        if command -v docker-compose &> /dev/null; then
            docker-compose logs
        else
            docker compose logs
        fi
        exit 1
    fi
    
    echo "⏳ 起動待機中... ($attempt/$max_attempts)"
    sleep 2
    ((attempt++))
done

echo ""
echo "🎉 システム起動完了！"
echo ""
echo "📡 アクセス情報:"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Redis: localhost:6379"
echo ""
echo "📋 便利なコマンド:"
echo "   ログ確認: docker-compose logs -f"
echo "   停止: docker-compose down"
echo "   再起動: docker-compose restart"
echo ""
