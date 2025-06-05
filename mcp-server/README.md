# 🤖 MCP Server for Conversation System

Claude Desktop用の完全統合MCPサーバーです。会話の自動記録、履歴管理、検索、分析機能を提供します。

## 🎯 実装済み機能

### 📝 利用可能なMCPツール（5個完全実装）

#### 1. `record_current_conversation` ⭐

**現在の会話交換を自動記録**:

```text
Claude Desktop: "この会話を記録して"
```

- ユーザーメッセージとアシスタントメッセージを一括保存
- トピック・キーワードの自動抽出対応
- 会話IDの自動生成と返却

#### 2. `save_conversation_message` 📝

**単一メッセージの個別保存**:

```text
Claude Desktop: "このメッセージを保存して、トピックは技術討論で"
```

- ユーザーまたはアシスタントメッセージの個別保存
- カスタムトピック・キーワード指定可能
- role検証機能付き

#### 3. `get_conversation_context` 📊

**会話履歴とコンテキストの取得**:

```text
Claude Desktop: "最近の会話履歴を見せて"
Claude Desktop: "過去50件の会話を構造化形式で表示して"
```

- narrative（物語形式）またはstructured（構造化）形式
- 取得件数の指定可能（デフォルト: 50件）
- AI用コンテキスト生成最適化

#### 4. `search_conversation_history` 🔍

**会話履歴の高度検索**:

```text
Claude Desktop: "Dockerについての過去の会話を検索して"
Claude Desktop: "Redis、MCP、Pythonに関する議論を探して"
```

- 複数キーワードでの検索対応
- トピック・内容・キーワードでの横断検索
- 検索結果件数制限（デフォルト: 20件）
- タイムスタンプ・トピック情報付きの詳細表示

#### 5. `get_conversation_analytics` 📈

**会話統計とパターン分析**:

```text
Claude Desktop: "会話の統計情報を表示して"
Claude Desktop: "どんなトピックをよく話している？"
```

- 総メッセージ数・総インサイト数
- 上位トピックランキング（頻度付き）
- メッセージ分布（ユーザー/アシスタント別）
- 最終更新日時

## 🚀 セットアップ

### 前提条件

- **Python 3.11以上**
- **動作中の会話システム**（`http://localhost:8000`）
- **Claude Desktop最新版**
- **MCP Python SDK 1.9.2以上**

### 自動セットアップ

```bash
# MCPサーバーをワンクリックセットアップ
cd mcp-server  # プロジェクトルートから
chmod +x setup.sh
./setup.sh
```

### 手動設定

#### 1. 依存関係インストール

```bash
cd mcp-server  # プロジェクトルートから
pip install -r requirements.txt
```

#### 2. Claude Desktop設定

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "conversation-system": {
      "command": "python3",
      "args": ["[実際のプロジェクトパス]/mcp-server/main.py"],
      "env": {
        "CONVERSATION_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

⚠️ **重要**: `[実際のプロジェクトパス]` を環境に合わせた正確なパスに変更してください。

**設定例**:

```json
{
  "mcpServers": {
    "conversation-system": {
      "command": "python3",
      "args": ["/home/username/conversation-system/mcp-server/main.py"],
      "env": {
        "CONVERSATION_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

#### 3. 動作確認

```bash
# API接続テスト
curl http://localhost:8000/health

# MCPサーバーテスト
cd mcp-server  # プロジェクトルートから
python3 test_all_tools.py
```

## 💬 使用方法

### 📝 基本的な会話記録

**全会話を一括記録:**

```text
この会話を記録して
```

**トピック・キーワード指定記録:**

```text
この技術討論を記録して、トピックはDocker・Redis・MCP、キーワードは統合、自動化、最適化で
```

**単一メッセージ保存:**

```text
「MCPサーバーが完全実装されました」というメッセージを保存して
```

### 📊 コンテキスト活用

**基本的な履歴取得:**

```text
最近の会話履歴を見せて
```

**詳細なコンテキスト取得:**

```text
過去30件の会話を物語形式で表示して
```

**構造化データ取得:**

```text
最近10件の会話を構造化フォーマットで見せて
```

### 🔍 高度な検索機能

**単一キーワード検索:**

```text
Dockerについての過去の会話を検索して
```

**複数キーワード検索:**

```text
Redis、MCP、Python、自動化に関する議論を検索して
```

**技術トピック横断検索:**

```text
データベース設計やAPI開発について話した内容を探して
```

### 📈 分析・統計機能

**基本統計表示:**

```text
会話の統計情報を表示して
```

**トピック分析:**

```text
どんなトピックをよく話しているか教えて
```

**使用パターン分析:**

```text
私の会話パターンを分析して
```

## 🛠️ 高度な使用例

### 複合的な活用

```text
「先週のDocker環境構築の議論を検索して、その内容を今日のコンテキストとして取得、さらに関連する統計情報も表示して」
```

### プロジェクト別管理

```text
「このプロジェクト討論を記録して、トピックは会話システム・MCP統合・生産性向上、キーワードはDocker、Redis、自動化、FastAPI、Claude Desktopで」
```

### 学習進捗追跡

```text
「機械学習について話した過去の会話をすべて検索して、学習の進歩を確認したい」
```

## 🔧 トラブルシューティング

### よくある問題と解決策

#### 1. MCPサーバーが認識されない

**症状**: Claude DesktopでMCPツールが表示されない

**診断手順**:

```bash
# 1. Claude Desktop設定確認
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 2. MCPサーバー単体テスト
cd mcp-server  # プロジェクトルートから
python3 -c "import main; print('✅ Import successful')"

# 3. 全ツールテスト
python3 test_all_tools.py
```

**解決策**:

- Claude Desktopの完全再起動
- パス設定の確認（実際のプロジェクトパスに変更）
- 依存関係の再インストール

#### 2. API接続エラー

**症状**: `❌ Error calling /messages: Connection refused`

**診断**:

```bash
# 会話システム状態確認
curl http://localhost:8000/health
curl http://localhost:8000/analytics
```

**解決策**:

```bash
# システム起動
cd ..  # プロジェクトルートに移動
./scripts/start.sh

# Docker状態確認
docker-compose ps
```

#### 3. 依存関係エラー

**症状**: `ModuleNotFoundError: No module named 'mcp'`

**解決策**:

```bash
cd mcp-server  # プロジェクトルートから
pip install --upgrade -r requirements.txt

# MCP SDK確認
python3 -c "import mcp; print(f'MCP version: {mcp.__version__}')"
```

#### 4. 検索結果が空

**症状**: `🔍 No conversations found`

**確認事項**:

```bash
# データ存在確認
curl http://localhost:8000/analytics

# Redis接続確認
docker exec conversation_redis redis-cli ping
```

#### 5. パフォーマンス低下

**診断**:

```bash
# システムリソース確認
docker stats

# Redis メモリ使用量
docker exec conversation_redis redis-cli info memory
```

### パス関連の問題

#### Claude Desktop設定のパス間違い

**症状**: MCPサーバーが起動しない

**解決策**:

1. **プロジェクトの実際のパスを確認**

   ```bash
   cd conversation-system  # プロジェクトディレクトリ
   pwd  # 実際のパスを表示
   ```

2. **Claude Desktop設定を実際のパスに更新**

   ```json
   {
     "mcpServers": {
       "conversation-system": {
         "command": "python3",
         "args": ["[ここに手順1で確認したパス]/mcp-server/main.py"],
         "env": {
           "CONVERSATION_API_URL": "http://localhost:8000"
         }
       }
     }
   }
   ```

3. **Claude Desktopを再起動**

### ログ確認とデバッグ

```bash
# MCPサーバー直接実行（デバッグモード）
cd mcp-server  # プロジェクトルートから
CONVERSATION_API_URL=http://localhost:8000 python3 main.py

# 会話システムログ
cd ..  # プロジェクトルートに戻る
docker-compose logs -f conversation_app

# Redis ログ
docker-compose logs redis
```

## 📊 パフォーマンス最適化

### 推奨設定

| 項目 | 推奨値 | 説明 |
|------|--------|------|
| **最大会話長** | 1000メッセージ | コンテキスト取得の上限 |
| **検索制限** | 20件 | 検索結果の表示件数 |
| **コンテキスト制限** | 50件 | デフォルトコンテキスト件数 |
| **タイムアウト** | 10秒 | API通信タイムアウト |

### 最適化テクニック

#### 1. データ管理

```bash
# 定期的なメモリ最適化
docker exec conversation_redis redis-cli MEMORY PURGE

# データ容量確認
curl http://localhost:8000/analytics | jq '.total_messages'
```

#### 2. 検索最適化

- 具体的なキーワードの使用
- 検索範囲の限定（limit指定）
- 頻繁な検索キーワードの記録

#### 3. コンテキスト最適化

- 必要最小限の件数指定
- narrative形式の活用（軽量）
- structured形式は必要時のみ

## 🔒 セキュリティ

### データプライバシー保護

- ✅ **完全ローカル保存**: すべてのデータはローカルに保存
- ✅ **外部送信なし**: インターネット経由の送信一切なし
- ✅ **暗号化対応**: Redis暗号化オプション利用可能
- ✅ **アクセス制御**: ローカルAPIアクセスのみ

### セキュリティ設定

#### 1. Redis認証設定

```bash
# パスワード設定
echo "requirepass your_secure_password" >> redis.conf
```

#### 2. API認証（オプション）

```bash
# 環境変数設定
export API_SECRET_KEY="your_secret_key"
```

#### 3. ファイアウォール設定

- ポート8000のローカルアクセスのみ許可
- 外部ネットワークからのアクセス遮断

## 📈 監視とメトリクス

### リアルタイム監視

#### ヘルスチェック

```bash
# システム全体のヘルスチェック
curl http://localhost:8000/health

# Redis接続確認
docker exec conversation_redis redis-cli ping

# MCP機能テスト
cd mcp-server  # プロジェクトルートから
python3 test_all_tools.py
```

#### パフォーマンス監視

```bash
# 会話統計の監視
curl http://localhost:8000/analytics | jq '{
  total_messages: .total_messages,
  total_topics: (.top_topics | length),
  last_updated: .last_updated
}'

# システムリソース監視
docker stats --no-stream | grep conversation
```

### メトリクス収集

#### 使用状況分析

```bash
# 日次メトリクス
echo "📊 $(date): $(curl -s http://localhost:8000/analytics | jq '.total_messages') messages" >> metrics.log

# 週次レポート
cd ..  # プロジェクトルートに移動
./scripts/knowledge_manager.sh weekly
```

## 🔄 アップグレードとメンテナンス

### アップグレード手順

```bash
# 1. システム停止
cd ..  # プロジェクトルートに移動
./scripts/stop.sh

# 2. コード更新
git pull origin main

# 3. 依存関係更新
cd mcp-server
pip install --upgrade -r requirements.txt

# 4. システム再起動
cd ..
./scripts/start.sh

# 5. Claude Desktop再起動
```

### 定期メンテナンス

#### 週次メンテナンス

```bash
# データバックアップ
cd ..  # プロジェクトルートに移動
./scripts/backup.sh

# 統計レポート生成
./scripts/knowledge_manager.sh weekly
```

#### 月次メンテナンス

```bash
# 包括的な分析
./scripts/knowledge_manager.sh monthly

# パフォーマンス最適化
docker exec conversation_redis redis-cli MEMORY PURGE
```

## 🤝 サポートとトラブルシューティング

### 問題報告時の情報収集

#### 1. 基本情報

```bash
# システム情報
echo "Python: $(python3 --version)"
echo "Docker: $(docker --version)"
echo "Claude Desktop: 最新版確認"

# プロジェクトパス確認
cd ..  # プロジェクトルートに移動
echo "Project Path: $(pwd)"

# 設定確認
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### 2. ログ収集

```bash
# エラーログ抽出
docker-compose logs conversation_app | grep ERROR
docker-compose logs redis | grep ERROR

# MCP通信ログ
# Claude Desktopの開発者ツールで確認
```

#### 3. MCPサーバー動作確認

```bash
# 全機能テスト
cd mcp-server  # プロジェクトルートから
python3 test_all_tools.py > test_results.log 2>&1
```

### よくある質問（FAQ）

#### Q1: MCPツールが5個すべて表示されない

**A**: Claude Desktopの再起動、設定ファイルの確認（実際のパスに変更）、MCPサーバーの単体テストを実行

#### Q2: 検索結果が期待と違う

**A**: キーワードの具体化、検索対象データの確認、インデックス再構築

#### Q3: パフォーマンスが遅い

**A**: Redis最適化、検索件数制限、システムリソース確認

#### Q4: データが消失した

**A**: バックアップからの復元、Redisデータ整合性確認

#### Q5: パス設定がわからない

**A**: プロジェクトディレクトリで `pwd` コマンドを実行して実際のパスを確認し、Claude Desktop設定ファイルを更新

---

## 📋 技術仕様

**Version**: 1.1.0  
**Compatibility**: Claude Desktop, Python 3.11+, MCP SDK 1.9.2+  
**Last Updated**: 2025-06-05  
**Status**: ✅ 5 Tools Fully Implemented & Tested  

**Architecture**:
    - **MCP Server**: FastMCP (Python)
    - **Backend API**: FastAPI + Redis
    - **Transport**: stdio (Claude Desktop)
    - **Storage**: Redis 7.2-alpine (Persistent)

**Performance**:
    - **Response Time**: < 500ms (local)
    - **Concurrent Users**: Single user (local)
    - **Data Retention**: Unlimited (local storage)
    - **Search Performance**: O(log n) with Redis indexing

## 📝 設定ファイルサンプル

### Claude Desktop設定サンプル

```json
{
  "mcpServers": {
    "conversation-system": {
      "command": "python3",
      "args": ["/path/to/your/conversation-system/mcp-server/main.py"],
      "env": {
        "CONVERSATION_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

**重要**: `/path/to/your/conversation-system` を実際のプロジェクトパスに変更してください。

### パス確認コマンド

```bash
# プロジェクトの実際のパスを確認
cd conversation-system
pwd

# この結果を上記の設定ファイルで使用
```

これで、環境に依存しない相対パス対応のMCPサーバーシステムが完成しました！
