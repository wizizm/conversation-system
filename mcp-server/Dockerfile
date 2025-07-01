FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    tar \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制MCP server文件
COPY main.py .
COPY config.json .

# 创建必要的目录
RUN mkdir -p /app/data /app/backups /app/logs

# 创建备份脚本
COPY docker_backup.sh /app/docker_backup.sh
RUN chmod +x /app/docker_backup.sh

# 设置定时任务
RUN echo "0 * * * * cd /app && /app/docker_backup.sh >> /app/logs/backup.log 2>&1" | crontab -

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 启动cron服务\n\
service cron start\n\
\n\
# 启动MCP server\n\
exec python main.py' > /app/start.sh && chmod +x /app/start.sh

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# 暴露端口（如果需要）
# EXPOSE 8080

# 启动命令
CMD ["/app/start.sh"] 