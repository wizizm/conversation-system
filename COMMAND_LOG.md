# 🖥️ Enhanced Conversation System - 命令执行日志

## 2025-07-01 - Docker化MCP Server系统测试与验证

### 🔧 系统状态检查命令
```bash
# 查看整体服务状态
make status

# 检查Redis连接
redis-cli ping

# 检查API健康状态
curl http://localhost:9000/health

# 详细检查API连接
curl -v http://localhost:9000/health

# 检查进程状态
ps aux | grep uvicorn
ps aux | grep redis

# 检查端口占用
lsof -i :8000
lsof -i :6379
lsof -i :9000
```

### 🚀 系统启动和重启命令
```bash
# 启动完整系统（本地模式）
make start-all

# 重启主应用服务
kill 78255
cd app && python -m uvicorn main:app --host 127.0.0.1 --port 9000 &

# 等待服务启动并测试
sleep 3 && curl http://localhost:9000/health
```

### 🧪 系统测试命令
```bash
# 运行完整MCP测试套件
cd mcp-server && python test_mcp.py

# 查看应用日志
tail -20 logs/app.log

# 检查FastAPI文档
curl http://localhost:9000/docs
```

### 📊 测试结果总结
```
✅ Enhanced API连接测试 - 成功
✅ Enhanced消息功能测试 - 成功（36%压缩率）
✅ 适应性上下文获取测试 - 成功
✅ 技术用语搜索功能测试 - 成功
✅ 压缩分析功能测试 - 成功
✅ 扩展分析功能测试 - 成功
✅ Enhanced MCP服务器启动测试 - 成功
```

### 🔄 配置修正命令
```bash
# 修改测试配置文件端口
vim mcp-server/test_mcp.py
# 修改: "api_base_url": "http://localhost:9000"

# 更新API配置文件
vim mcp-server/config.json
# 修改: "api_url": "http://localhost:9000"
```

### 💾 数据管理命令
```bash
# 手动备份
make backup

# 备份监控
make backup-monitor

# 查看备份文件
ls -la backups/

# 清理旧备份
make clean-backups
```

---

## 2025-07-01 - MCP服务器配置和备份系统设置

### 📋 环境检查命令

```bash
# 检查Python版本
python3 --version
# Output: Python 3.11.11

# 检查项目目录结构  
pwd && ls -la
# /Users/linwenjie/workspace/conversation-system

# 查看数据目录结构
ls -la data/
ls -la data/redis/
ls -la conversations/ 2>/dev/null || echo "会话文件目录不存在"
```

### 🔧 MCP服务器安装和配置

```bash
# 进入MCP服务器目录
cd mcp-server && ls -la

# 安装MCP服务器依赖
pip3 install -r requirements.txt
# 成功安装: mcp-1.10.1, pydantic-2.11.7, httpx-0.28.1 等

# 验证MCP库安装
python3 -c "import mcp; print('✅ MCP library imported successfully')"

# 设置脚本执行权限
chmod +x scripts/backup.sh
chmod +x scripts/complete_backup.sh 
chmod +x scripts/restore_backup.sh
chmod +x scripts/setup_auto_backup.sh
```

### 💾 备份系统测试

```bash
# 创建备份目录
mkdir -p backups && ls -la backups/

# 执行完整备份
./scripts/complete_backup.sh
# 生成备份文件:
# - app_data_20250701_093620.tar.gz (583B)
# - backup_info_20250701_093620.txt (815B)
# - config_20250701_093620.tar.gz (30K)

# 查看备份结果
ls -la backups/
cat backups/backup_info_20250701_093620.txt
```

### 📊 系统状态检查

```bash
# 检查Docker状态
docker ps -q --filter "name=conversation_redis"
docker images | grep redis

# 检查运行中的进程
ps aux | grep "main.py" | grep -v grep
# 发现MCP服务器进程: PID 14015

# 检查磁盘使用情况
du -sh backups/*
df -h . | tail -1
```

### 🔄 定时任务相关命令

```bash
# 查看当前用户的定时任务
crontab -l 2>/dev/null || echo "无定时任务"

# 设置定时备份的命令示例（用于文档）
# 0 2 * * * cd /Users/linwenjie/workspace/conversation-system && ./scripts/complete_backup.sh >> logs/backup.log 2>&1
```

### 📁 文件操作命令

```bash
# 创建配置文件
cat > claude_config_manual.json << 'EOF'
{
  "mcpServers": {
    "conversation-system": {
      "command": "python3",
      "args": ["/Users/linwenjie/workspace/conversation-system/mcp-server/main.py"],
      "env": {
        "CONVERSATION_API_URL": "http://localhost:8000"
      }
    }
  }
}
EOF

# 查看Redis配置
head -50 redis.conf

# 查看Docker Compose配置
head -130 compose.yml
```

### 🧪 备份系统验证

```bash
# 检查备份脚本语法
bash -n scripts/complete_backup.sh
bash -n scripts/restore_backup.sh  
bash -n scripts/setup_auto_backup.sh

# 测试备份功能（无Docker环境）
./scripts/complete_backup.sh
# ✅ 成功执行，生成备份文件

# 查看生成的备份信息
cat backups/backup_info_20250701_093620.txt
```

### 📝 日志和监控命令

```bash
# 创建日志目录
mkdir -p logs

# 查看备份日志（如果存在）
tail -f logs/backup.log 2>/dev/null || echo "备份日志不存在"

# 监控文件变化
ls -lt backups/ | head -5

# 检查备份文件大小
du -sh backups/*
```

### 🔍 故障排除命令

```bash
# 检查端口占用
lsof -i :8000 2>/dev/null || echo "端口8000未被占用"
lsof -i :6379 2>/dev/null || echo "端口6379未被占用"

# 检查网络连接
curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "API服务可访问" || echo "API服务不可访问"

# 检查Docker网络问题（如果有）
docker network ls | grep conversation
```

### 📋 常用维护命令

```bash
# 查看系统资源使用
top -l 1 | head -10

# 清理旧备份（示例命令）
find backups/ -name "*.rdb" -mtime +7 -delete
find backups/ -name "*.tar.gz" -mtime +30 -delete

# 备份权限设置
chmod 700 backups/
chmod 600 backups/*

# 验证压缩文件完整性
gzip -t backups/*.tar.gz 2>/dev/null && echo "压缩文件完整" || echo "压缩文件可能损坏"
```

## 🎯 总结：关键命令记录

### 一键操作命令
```bash
# 立即备份
./scripts/complete_backup.sh

# 恢复数据
./scripts/restore_backup.sh <timestamp>

# 设置自动备份
./scripts/setup_auto_backup.sh

# 查看备份状态
ls -la backups/
```

### 环境配置命令
```bash
# MCP服务器依赖安装
pip3 install -r mcp-server/requirements.txt

# 权限设置
chmod +x scripts/*.sh

# 目录创建
mkdir -p {backups,logs,conversations}
```

### 监控和检查命令
```bash
# 服务状态检查
ps aux | grep main.py
docker ps | grep conversation

# 备份完整性检查
cat backups/backup_info_*.txt
du -sh backups/*

# 系统资源检查
df -h .
```

## 💡 备注

- 所有命令在 `/Users/linwenjie/workspace/conversation-system` 目录下执行
- MCP服务器使用Python 3.11.11环境
- 备份系统支持Docker和非Docker环境自动检测
- 备份文件使用时间戳命名格式：YYYYMMDD_HHMMSS 

## 2025-01-07 - Docker化MCP Server实现

### 🐳 Docker服务管理
```bash
# 启动完整Docker系统（包含MCP Server）
./scripts/start_with_mcp.sh

# 查看服务状态
docker-compose ps

# 查看MCP Server日志
docker-compose logs -f mcp_server

# 重启MCP Server
docker-compose restart mcp_server

# 停止所有服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

### 📦 备份管理命令
```bash
# 手动执行备份（容器内）
docker-compose exec mcp_server /app/docker_backup.sh

# 交互式备份监控器
./scripts/mcp_backup_monitor.sh

# 查看备份文件
ls -la backups/

# 查看备份日志
docker-compose exec mcp_server tail -f /app/logs/backup.log

# 设置脚本执行权限
chmod +x scripts/start_with_mcp.sh scripts/mcp_backup_monitor.sh mcp-server/docker_backup.sh
```

### 🔧 调试和监控
```bash
# 检查容器状态
docker ps | grep mcp_server

# 查看容器详细信息
docker inspect conversation_mcp_server

# 进入容器调试
docker exec -it conversation_mcp_server /bin/bash

# 查看容器资源使用
docker stats conversation_mcp_server

# 查看容器磁盘使用
docker exec conversation_mcp_server df -h
```

### 🧪 测试命令
```bash
# 测试主应用API
curl http://localhost:8000/health

# 测试备份功能
docker-compose exec -T mcp_server /app/docker_backup.sh

# 检查定时任务配置
docker-compose exec -T mcp_server crontab -l

# 验证数据挂载
docker-compose exec mcp_server ls -la /app/data
docker-compose exec mcp_server ls -la /app/backups
```

---

## 2025-01-01 - Enhanced Conversation System MCP服务器分析和备份系统完善

### 环境检查命令
```bash
# Python环境检查
python --version  # Python 3.11.11

# MCP相关包检查  
pip list | grep mcp
pip list | grep fastmcp
pip list | grep pydantic

# 进程检查
ps aux | grep python
ps aux | grep mcp
```

### MCP Server配置
```bash
# 安装FastMCP依赖
pip install fastmcp

# 检查MCP Server运行状态
ps -ef | grep main.py

# 查看MCP Server配置
cat mcp-server/config.json
cat mcp-server/claude_desktop_config.json
```

### 备份系统命令
```bash
# 执行完整备份
./scripts/complete_backup.sh

# 设置自动备份
./scripts/setup_auto_backup.sh

# 恢复备份
./scripts/restore_backup.sh

# 查看备份状态
ls -la backups/

# 测试备份功能
tar -tf backups/app_data_20250701_093620.tar.gz
```

### 系统状态检查
```bash
# 检查磁盘空间
df -h

# 检查内存使用
free -h

# 检查进程状态
top -p $(pgrep -f main.py)

# 检查端口占用
lsof -i :8000
netstat -tlnp | grep :8000
```

### 服务管理
```bash
# 启动Redis服务
redis-server redis.conf

# 启动FastAPI应用
python app/main.py

# 启动MCP Server
cd mcp-server && python main.py

# 检查服务健康状态
curl http://localhost:8000/health
redis-cli ping
```

### Git操作记录
```bash
# 查看文件状态
git status

# 添加新文件
git add BACKUP_GUIDE.md
git add CHANGE_LOG.md  
git add COMMAND_LOG.md
git add claude_config_manual.json
git add scripts/complete_backup.sh
git add scripts/restore_backup.sh
git add scripts/setup_auto_backup.sh

# 提交更改
git commit -m "Add comprehensive backup system and MCP server analysis"
```

### 常用运维命令
```bash
# 创建目录结构
mkdir -p {data/redis,data/app,logs,backups,conversations}

# 设置权限
chmod +x scripts/*.sh

# 查看系统信息
uname -a                    # 系统信息
hostnamectl                 # 主机信息（Linux）
system_profiler SPSoftwareDataType  # 系统信息（macOS）

# 监控日志
tail -f logs/app.log
tail -f logs/backup.log

# 清理临时文件
find . -name "*.tmp" -delete
find . -name "*.pyc" -delete
``` 