# ~/.bashrc または ~/.zshrc に追加するエイリアス設定
# 注意: 実際のプロジェクトパスに合わせて PROJECT_ROOT を設定してください

# プロジェクトルートを設定（各自の環境に合わせて変更）
PROJECT_ROOT="${HOME}/conversation-system"  # デフォルト例
# PROJECT_ROOT="/path/to/your/conversation-system"  # カスタムパス例

# 知識管理システムのエイリアス
alias km="${PROJECT_ROOT}/scripts/knowledge_manager.sh"
alias km-morning="km morning"
alias km-weekly="km weekly"
alias km-monthly="km monthly"
alias km-stats="km stats"
alias km-help="km help"

# よく使う検索のエイリアス  
alias km-search-docker="km search Docker"
alias km-search-python="km search Python"
alias km-search-mcp="km search MCP"

# ドメイン分析のエイリアス
alias km-prog="km domain プログラミング"
alias km-business="km domain ビジネス戦略"
alias km-ai="km domain AI・機械学習"

# 会話システム管理
alias conversation-start="cd ${PROJECT_ROOT} && ./scripts/start.sh"
alias conversation-stop="cd ${PROJECT_ROOT} && ./scripts/stop.sh"
alias conversation-logs="cd ${PROJECT_ROOT} && docker-compose logs -f"

# 使用例:
# km-morning          # 朝のブリーフィング
# km search "Redis"   # Redisについて検索
# km-prog            # プログラミング分野の分析

echo "🎉 エイリアス設定完了！"
echo "PROJECT_ROOT が正しく設定されていることを確認してください: ${PROJECT_ROOT}"
echo "source ~/.bashrc (または ~/.zshrc) を実行して設定を有効化してください"
