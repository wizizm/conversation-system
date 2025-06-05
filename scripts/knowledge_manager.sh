#!/usr/bin/env bash

# 知識活用マスタースクリプト
# プロジェクトルートを動的に取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ACTION=$1

case $ACTION in
    "morning")
        echo "🌅 朝の知識準備を開始..."
        $SCRIPT_DIR/morning_briefing.sh
        ;;
    "weekly")
        echo "📊 週次分析を実行..."
        $SCRIPT_DIR/weekly_analysis.sh
        ;;
    "monthly")
        echo "📈 月次戦略レビューを実行..."
        chmod +x $SCRIPT_DIR/monthly_strategy.sh
        $SCRIPT_DIR/monthly_strategy.sh
        ;;
    "domain")
        if [ -z "$2" ]; then
            echo "使用方法: $0 domain <分野名>"
            exit 1
        fi
        echo "🎯 専門分野分析: $2"
        $SCRIPT_DIR/domain_analysis.sh "$2"
        ;;
    "knowledge")
        if [ -z "$2" ]; then
            echo "使用方法: $0 knowledge <トピック>"
            exit 1
        fi
        echo "🧠 知識連想マップ: $2"
        $SCRIPT_DIR/knowledge_map.sh "$2"
        ;;
    "search")
        if [ -z "$2" ]; then
            echo "使用方法: $0 search <検索語>"
            exit 1
        fi
        echo "🔍 知識検索: $2"
        curl -X POST http://localhost:8000/search \
          -H "Content-Type: application/json" \
          -d "{\"query_terms\": [\"$2\"], \"limit\": 10}" | jq
        ;;
    "stats")
        echo "📊 現在の統計情報"
        curl -s http://localhost:8000/analytics | jq
        ;;
    "help")
        echo "📚 === 知識活用システム ヘルプ ==="
        echo ""
        echo "使用可能なコマンド:"
        echo "  morning  - 朝の知識準備ブリーフィング"
        echo "  weekly   - 週次分析レポート"
        echo "  monthly  - 月次戦略レビュー"
        echo "  domain <分野>   - 専門分野別分析"
        echo "  knowledge <トピック> - 知識連想マップ"
        echo "  search <検索語> - 過去の議論検索"
        echo "  stats    - 現在の統計情報"
        echo ""
        echo "例："
        echo "  $0 morning"
        echo "  $0 domain 'プログラミング'"
        echo "  $0 search 'Docker'"
        ;;
    *)
        echo "❌ 無効なアクション: $ACTION"
        echo "ヘルプを表示するには: $0 help"
        exit 1
        ;;
esac
