# Enhanced MCP Server Dockerfile with Auto Backup
FROM docker2.gf.com.cn/library/python:v1.0.0-3.11-ubuntu20.04

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    tar \
    gzip \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY . .

# 创建必要目录
RUN mkdir -p /app/data /app/logs /app/backups

# 复制并设置备份脚本权限
COPY docker_backup.sh /app/docker_backup.sh
RUN chmod +x /app/docker_backup.sh

# 设置cron任务（每小时运行备份）
RUN echo "0 * * * * cd /app && /app/docker_backup.sh >> /app/logs/backup.log 2>&1" > /etc/cron.d/backup-cron
RUN chmod 0644 /etc/cron.d/backup-cron
RUN crontab /etc/cron.d/backup-cron

# 启动cron服务并运行MCP Server
COPY <<EOF /app/start.sh
#!/bin/bash
# 启动cron服务
cron

# 启动MCP Server
python main.py
EOF

RUN chmod +x /app/start.sh

# 暴露MCP Server端口（修正为3001）
EXPOSE 3001

# 健康检查 - 检查端口3001
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD nc -z localhost 3001 || exit 1

# 运行启动脚本
CMD ["/app/start.sh"] 