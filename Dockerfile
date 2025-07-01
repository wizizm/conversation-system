FROM docker2.gf.com.cn/library/python:v1.0.0-3.11-ubuntu20.04

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    redis-tools \
    curl \
    cron \
    tar \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ設定
WORKDIR /app

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY app/ ./

# ディレクトリ作成
RUN mkdir -p /app/data /app/logs /app/conversations /app/backups

# 非rootユーザー作成
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser

# ポート公開
EXPOSE 8000 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='${REDIS_HOST:-redis}'); r.ping()"

# 起動コマンド
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--log-level", "info"]
