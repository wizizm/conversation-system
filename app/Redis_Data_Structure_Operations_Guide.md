# Redis データ構造・運用ガイド

## Conversation System Redis Architecture

---

## 📋 目次

1. [概要](#概要)
2. [データ構造の全体像](#データ構造の全体像)
3. [メッセージデータの保存構造](#メッセージデータの保存構造)
4. [知見データの保存構造](#知見データの保存構造)
5. [データ取得方法](#データ取得方法)
6. [Redis Insight での確認方法](#redis-insight-での確認方法)
7. [運用コマンド集](#運用コマンド集)
8. [パフォーマンス最適化](#パフォーマンス最適化)
9. [トラブルシューティング](#トラブルシューティング)

---

## 概要

このConversation Systemでは、**会話履歴と知見の蓄積**を目的として、Redisに構造化されたデータを保存しています。効率的な検索と分析を可能にするため、複数のインデックス構造を採用しています。

### 主要な特徴

- 多角度インデックス: 時系列、トピック、キーワード、セッション別の検索
- スコアベース順序付け: 重要度や時刻による自動ソート
- パイプライン処理: 高性能な一括操作
- JSON統合: 構造化データの柔軟な保存

---

## データ構造の全体像

```text
Redis Database (DB: 0)
├── Messages (会話メッセージ)
│   ├── message:{message_id} (Hash)
│   ├── messages:timeline (Sorted Set)
│   ├── session:{session_id}:messages (Set)
│   ├── topic:{topic_name} (Set)
│   ├── keyword:{keyword_name} (Set)
│   └── role:{user|assistant} (Set)
│
├── Insights (抽出知見)
│   ├── insight:{insight_id} (Hash)
│   ├── insights:by_relevance (Sorted Set)
│   ├── insights:{insight_type} (Set)
│   └── business_area:{area_name} (Set)
│
└── Analytics (分析データ)
    ├── analytics:total_messages (String)
    ├── analytics:daily:{YYYY-MM-DD} (String)
    └── analytics:word_counts (List)
```

---

## メッセージデータの保存構造

### 1. 個別メッセージ（Hash構造）

**キー**: `message:{message_id}`

| フィールド | データ型 | 説明 | 例 |
|-----------|---------|------|-----|
| `id` | String | メッセージの一意ID | `770fa214-3750-47fa-82ff-c3e25697299b` |
| `timestamp` | String | ISO形式の作成時刻 | `2024-01-15T10:30:45.123456` |
| `role` | String | メッセージの送信者 | `user` / `assistant` |
| `content` | String | メッセージ本文 | `あなたとの会話をローカルで動作するRedisに保存する方法はあるでしょうか？` |
| `topics` | JSON String | トピック配列 | `["Redis", "会話履歴", "データ保存"]` |
| `keywords` | JSON String | キーワード配列 | `["Redis", "ローカル", "保存", "会話"]` |
| `context_hash` | String | コンテンツのMD5ハッシュ | `a1b2c3d4e5f6...` |
| `session_id` | String | セッション識別子 | `df2092f0-ee59-4170-afb5-1b20fd72e01c` |

### 2. インデックス構造

#### 時系列インデックス（Sorted Set）

```redis
messages:timeline → {message_id: timestamp_numeric}
# 例: {"770fa214-...": 1640678445.123}
```

#### セッション別インデックス（Set）

```redis
session:{session_id}:messages → {message_id1, message_id2, ...}
# 例: session:df2092f0-...:messages → {"770fa214-...", "881gb325-..."}
```

#### トピック別インデックス（Set）

```redis
topic:{topic_name} → {message_id1, message_id2, ...}
# 例: topic:redis → {"770fa214-...", "992hc436-..."}
```

#### キーワード別インデックス（Set）

```redis
keyword:{keyword_name} → {message_id1, message_id2, ...}
# 例: keyword:保存 → {"770fa214-...", "aa3id547-..."}
```

#### ロール別インデックス（Set）

```redis
role:{user|assistant} → {message_id1, message_id2, ...}
# 例: role:user → {"770fa214-...", "bb4je658-..."}
```

---

## 知見データの保存構造

### 1. 個別知見（Hash構造）

**キー**: `insight:{insight_id}`

| フィールド | データ型 | 説明 | 例 |
|-----------|---------|------|-----|
| `id` | String | 知見の一意ID | `insight-uuid-here` |
| `timestamp` | String | ISO形式の作成時刻 | `2024-01-15T10:35:22.456789` |
| `insight_type` | String | 知見の種類 | `pattern` / `solution` / `framework` / `blind_spot` |
| `content` | String | 知見の内容 | `Redis-based conversation storage enables...` |
| `source_messages` | JSON String | 元となったメッセージID配列 | `["770fa214-...", "881gb325-..."]` |
| `relevance_score` | Float | 重要度スコア（0-1） | `0.9` |
| `business_area` | String | ビジネス領域 | `AI/データ管理` |

### 2. 知見インデックス構造

#### 重要度順インデックス（Sorted Set）

```redis
insights:by_relevance → {insight_id: relevance_score}
# 例: {"insight-123": 0.9, "insight-456": 0.8}
```

#### タイプ別インデックス（Set）

```redis
insights:{insight_type} → {insight_id1, insight_id2, ...}
# 例: insights:solution → {"insight-123", "insight-456"}
```

#### ビジネス領域別インデックス（Set）

```redis
business_area:{area_name} → {insight_id1, insight_id2, ...}
# 例: business_area:AI/データ管理 → {"insight-123", "insight-789"}
```

---

## データ取得方法

### 1. 最新会話履歴の取得

```python
# 最新50件のメッセージIDを時系列順で取得
recent_message_ids = redis.zrevrange("messages:timeline", 0, 49)

# 各メッセージの詳細情報を取得
messages = []
for msg_id in recent_message_ids:
    msg_data = redis.hgetall(f"message:{msg_id}")
    messages.append(msg_data)
```

**Redis CLI**:

```bash
# 最新10件のメッセージID取得
ZREVRANGE messages:timeline 0 9

# 特定メッセージの詳細取得
HGETALL message:770fa214-3750-47fa-82ff-c3e25697299b
```

### 2. トピック・キーワード検索

```python
# 特定トピックのメッセージを検索
topic_messages = redis.smembers("topic:redis")

# 複数条件での検索（和集合）
matching_ids = set()
for term in ["redis", "データベース"]:
    matching_ids.update(redis.smembers(f"topic:{term}"))
    matching_ids.update(redis.smembers(f"keyword:{term}"))
```

**Redis CLI**:

```bash
# 特定トピックの全メッセージID
SMEMBERS topic:redis

# 複数条件検索（和集合）
SUNION topic:redis topic:データベース keyword:保存
```

### 3. セッション履歴の取得

```python
# 特定セッションの全メッセージ
session_messages = redis.smembers(f"session:{session_id}:messages")
```

**Redis CLI**:

```bash
# セッション内の全メッセージID
SMEMBERS session:df2092f0-ee59-4170-afb5-1b20fd72e01c:messages
```

### 4. 知見の取得

```python
# 重要度上位10件の知見を取得
top_insights = redis.zrevrange("insights:by_relevance", 0, 9)

# 特定タイプの知見を取得
solutions = redis.smembers("insights:solution")
```

**Redis CLI**:

```bash
# 重要度上位10件の知見ID
ZREVRANGE insights:by_relevance 0 9 WITHSCORES

# 特定タイプの知見
SMEMBERS insights:solution
```

---

## Redis Insight での確認方法

### 1. メッセージ内容の確認

#### Browser画面での確認

1. **Browser**タブを開く
2. 検索バーに `message:770fa214-3750-47fa-82ff-c3e25697299b` を入力
3. 該当するHashキーをクリック
4. 詳細情報を確認

#### Workbenchでのコマンド実行

```redis
-- 全フィールド取得
HGETALL message:770fa214-3750-47fa-82ff-c3e25697299b

-- 特定フィールドのみ取得
HMGET message:770fa214-3750-47fa-82ff-c3e25697299b content role timestamp
```

### 2. 日本語の正しい表示

#### Redis CLI（推奨）

```bash
# UTF-8をそのまま出力
redis-cli --raw HGET message:770fa214-3750-47fa-82ff-c3e25697299b content

# 全データを正しく表示
redis-cli --raw HGETALL message:770fa214-3750-47fa-82ff-c3e25697299b
```

#### Redis Insight設定

1. workbench画面で「Raw mode」をクリックして有効化すると、日本語文字列がユニコードエスケープされずに表示されます。

---

## 運用コマンド集

### データ確認コマンド

```bash
# 総メッセージ数確認
ZCARD messages:timeline

# 今日のメッセージ数
GET analytics:daily:2024-01-15

# 全トピック一覧
KEYS topic:*

# 特定トピックのメッセージ数
SCARD topic:redis

# メモリ使用量確認
INFO memory

# 接続数確認
INFO clients
```

### 検索・分析コマンド

```bash
# 最新のメッセージ内容を5件表示
EVAL "
local ids = redis.call('ZREVRANGE', 'messages:timeline', 0, 4)
local results = {}
for i, id in ipairs(ids) do
    local content = redis.call('HGET', 'message:' .. id, 'content')
    table.insert(results, id .. ': ' .. (content or 'N/A'))
end
return results
" 0

# トピック別メッセージ数ランキング
EVAL "
local topics = redis.call('KEYS', 'topic:*')
local results = {}
for i, topic in ipairs(topics) do
    local count = redis.call('SCARD', topic)
    local name = string.sub(topic, 7)  -- 'topic:' を除去
    table.insert(results, name .. ': ' .. count)
end
return results
" 0
```

### メンテナンスコマンド

```bash
# データベースサイズ確認
DBSIZE

# 全キー確認（本番環境では注意）
KEYS *

# 特定パターンのキー削除（危険！）
# EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 "analytics:daily:*"

# バックアップ実行
BGSAVE

# Redis設定確認
CONFIG GET save
CONFIG GET maxmemory
```

---

## パフォーマンス最適化

### 1. パイプライン処理の活用

```python
# 効率的な一括処理
pipe = redis_client.pipeline()
pipe.hset(f"message:{msg_id}", mapping=message_data)
pipe.zadd("messages:timeline", {msg_id: timestamp_numeric})
pipe.sadd(f"topic:{topic}", msg_id)
pipe.sadd(f"keyword:{keyword}", msg_id)
pipe.execute()  # 一括実行
```

### 2. メモリ最適化設定

**redis.conf** での推奨設定:

```conf
# メモリ制限とLRU設定
maxmemory 256mb
maxmemory-policy allkeys-lru

# ハッシュテーブル最適化
hash-max-ziplist-entries 512
hash-max-ziplist-value 64

# セット最適化
set-max-intset-entries 512

# ソートセット最適化
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
```

### 3. インデックス戦略

- 複合検索: 複数のSetを`SUNION`で結合
- 範囲検索: Sorted Setの`ZRANGEBYSCORE`を活用
- 頻度分析: 定期的な統計情報更新

---

## トラブルシューティング

### よくある問題と解決方法

#### 1. 日本語文字化け

**症状**: `\xe3\x81\x82...` のような表示
**解決方法**:

```bash
# Redis CLI使用時
redis-cli --raw

# Python使用時
redis.Redis(decode_responses=True)
```

#### 2. メモリ不足

**症状**: `OOM command not allowed when used memory > 'maxmemory'`
**解決方法**:

```bash
# メモリ使用量確認
INFO memory

# 設定確認・変更
CONFIG GET maxmemory
CONFIG SET maxmemory 512mb

# 不要データ削除
FLUSHDB  # 注意: 全データ削除
```

#### 3. インデックス不整合

**症状**: 検索結果にないメッセージIDが表示
**解決方法**:

```python
# インデックス再構築スクリプト
def rebuild_indexes(redis_client):
    # 全メッセージIDを取得
    all_message_ids = redis_client.zrange("messages:timeline", 0, -1)
    
    for msg_id in all_message_ids:
        msg_data = redis_client.hgetall(f"message:{msg_id}")
        
        # トピックインデックス再構築
        topics = json.loads(msg_data.get('topics', '[]'))
        for topic in topics:
            redis_client.sadd(f"topic:{topic.lower()}", msg_id)
        
        # キーワードインデックス再構築
        keywords = json.loads(msg_data.get('keywords', '[]'))
        for keyword in keywords:
            redis_client.sadd(f"keyword:{keyword.lower()}", msg_id)
```

#### 4. 接続エラー

**症状**: `ConnectionError: Error 111 connecting to localhost:6379`
**解決方法**:

```bash
# Redis起動確認
redis-server --version
systemctl status redis

# Docker使用時
docker-compose up redis
docker logs conversation_redis
```

---

## 監視・保守

### 定期監視項目

```bash
# 1. システム状態
INFO server
INFO clients
INFO memory

# 2. パフォーマンス
INFO stats
SLOWLOG GET 10

# 3. データ整合性
DBSIZE
ZCARD messages:timeline
ZCARD insights:by_relevance
```

### バックアップ戦略

```bash
# 1. RDB スナップショット
BGSAVE

# 2. AOF ログ
CONFIG SET appendonly yes

# 3. 定期バックアップ（cron）
0 2 * * * redis-cli BGSAVE
0 3 * * 0 cp /data/dump.rdb /backup/dump_$(date +\%Y\%m\%d).rdb
```

---

## 参考資料

- [Redis公式ドキュメント](https://redis.io/documentation)
- [Redis Insight ダウンロード](https://redis.com/redis-enterprise/redis-insight/)
- [Redis データ型リファレンス](https://redis.io/topics/data-types)

---
