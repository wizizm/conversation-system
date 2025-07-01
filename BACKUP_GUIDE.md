# 📦 Enhanced Conversation System - 备份与恢复指南 v2.0

## 📍 会话数据存储位置

### 🗂️ 主要数据目录

| 目录 | 内容说明 | 重要性 | 备份频率 |
|-----|----------|--------|----------|
| `./data/redis/` | Redis数据库文件（dump.rdb, appendonly.aof） | ⭐⭐⭐⭐⭐ | 每天 |
| `./data/app/` | 应用程序数据、缓存、临时文件 | ⭐⭐⭐⭐ | 每天 |
| `./conversations/` | 会话JSON文件（文件存储模式） | ⭐⭐⭐⭐ | 每天 |
| `./logs/` | 系统运行日志 | ⭐⭐⭐ | 每周 |
| `./mcp-server/` | MCP服务器配置和脚本 | ⭐⭐⭐⭐ | 配置变更时 |

### 📊 数据存储架构

```text
📁 /Users/linwenjie/workspace/conversation-system/
├── 💾 data/
│   ├── 🔴 redis/          # Redis持久化文件
│   │   ├── dump.rdb       # 数据快照（主要备份目标）
│   │   └── appendonly.aof # 操作日志（事务恢复）
│   └── 📊 app/            # FastAPI应用数据
├── 💬 conversations/      # 会话文件存储
├── 📝 logs/              # 系统日志
├── 💿 backups/           # 备份文件存储
└── 🤖 mcp-server/        # MCP服务器
```

## 🚀 快速备份操作

### **方案1：一键完整备份**（推荐）

```bash
# 智能备份（自动检测Docker环境）
./scripts/complete_backup.sh

# 备份文件会保存到 ./backups/ 目录
# 格式：backup_YYYYMMDD_HHMMSS
```

**输出示例：**
```text
✅ 备份完成！
📁 备份文件位置: ./backups/
📋 备份清单:
-rw-r--r--@ 1 user staff 583B app_data_20250701_093620.tar.gz
-rw-r--r--@ 1 user staff 815B backup_info_20250701_093620.txt  
-rw-r--r--@ 1 user staff 30K  config_20250701_093620.tar.gz

💡 恢复方法: ./scripts/restore_backup.sh 20250701_093620
```

### **方案2：Docker环境备份**

```bash
# 启动完整系统（包含自动备份）
./scripts/start.sh

# 手动触发备份
./scripts/backup.sh
```

### **方案3：手动文件备份**

```bash
# 手动备份关键数据
tar -czf "backup_manual_$(date +%Y%m%d).tar.gz" \
    data/ conversations/ mcp-server/ \
    redis.conf compose.yml requirements.txt
```

## 🔄 自动备份设置

### **设置定时自动备份**

```bash
# 交互式设置自动备份
./scripts/setup_auto_backup.sh

# 选项：
# 1. 每天凌晨2点备份 (推荐)
# 2. 每12小时备份一次
# 3. 每周日凌晨2点备份
# 4. 自定义备份时间
# 5. 清除自动备份
```

### **手动设置定时任务**

```bash
# 编辑定时任务
crontab -e

# 添加每天凌晨2点自动备份
0 2 * * * cd /Users/linwenjie/workspace/conversation-system && ./scripts/complete_backup.sh >> logs/backup.log 2>&1

# 查看定时任务
crontab -l
```

### **监控自动备份**

```bash
# 查看备份日志
tail -f logs/backup.log

# 查看最近的备份文件
ls -lt backups/ | head -5

# 检查备份大小
du -sh backups/*
```

## 🔄 数据恢复操作

### **完整恢复流程**

```bash
# 1. 查看可用备份
ls -la backups/backup_info_*.txt

# 2. 选择备份时间戳恢复（交互式）
./scripts/restore_backup.sh 20250701_093620

# 恢复过程会：
# - 停止运行中的服务
# - 备份当前数据（安全措施）
# - 恢复Redis数据
# - 恢复应用数据
# - 恢复会话文件
# - 可选恢复配置文件
```

### **单独恢复组件**

```bash
# 只恢复Redis数据
cp backups/redis_20250701_093620.rdb data/redis/dump.rdb
cp backups/redis_aof_20250701_093620.aof data/redis/appendonly.aof

# 只恢复应用数据
tar -xzf backups/app_data_20250701_093620.tar.gz -C data/

# 只恢复会话文件
tar -xzf backups/conversations_20250701_093620.tar.gz -C conversations/

# 只恢复配置
tar -xzf backups/config_20250701_093620.tar.gz
```

### **紧急恢复（系统崩溃）**

```bash
# 1. 重新克隆项目
git clone <repository-url> conversation-system-recovery
cd conversation-system-recovery

# 2. 复制备份文件
cp -r /path/to/backups ./

# 3. 恢复数据
./scripts/restore_backup.sh <timestamp>

# 4. 重启系统
./scripts/start.sh
```

## 💾 备份文件说明

### **备份文件类型**

| 文件类型 | 命名格式 | 内容 | 保留期 |
|---------|----------|------|-------|
| `redis_*.rdb` | `redis_YYYYMMDD_HHMMSS.rdb` | Redis数据快照 | 7天 |
| `redis_aof_*.aof` | `redis_aof_YYYYMMDD_HHMMSS.aof` | Redis事务日志 | 7天 |
| `app_data_*.tar.gz` | `app_data_YYYYMMDD_HHMMSS.tar.gz` | 应用程序数据 | 30天 |
| `conversations_*.tar.gz` | `conversations_YYYYMMDD_HHMMSS.tar.gz` | 会话文件 | 30天 |
| `config_*.tar.gz` | `config_YYYYMMDD_HHMMSS.tar.gz` | 配置文件 | 30天 |
| `backup_info_*.txt` | `backup_info_YYYYMMDD_HHMMSS.txt` | 备份信息 | 永久 |

### **备份信息文件内容**

```text
Enhanced Conversation System - 备份信息
========================================
备份时间: 2025年 7月 1日 星期二 09时36分21秒 CST
备份版本: v2.0
项目路径: /Users/linwenjie/workspace/conversation-system
Docker状态: false

备份文件清单:
-rw-r--r--@ 1 user staff 583B app_data_20250701_093620.tar.gz
-rw-r--r--@ 1 user staff 30K  config_20250701_093620.tar.gz

系统信息:
- Python版本: Python 3.11.11
- Docker版本: Docker version 25.0.5
- 磁盘空间: 162Gi available

使用恢复脚本恢复:
./scripts/restore_backup.sh 20250701_093620
```

## 🗑️ 备份清理策略

### **自动清理规则**

- **Redis文件**：保留7天，自动删除较旧的 `.rdb` 和 `.aof` 文件
- **应用数据**：保留30天，自动删除较旧的 `.tar.gz` 文件
- **备份信息**：永久保留，用于追踪备份历史

### **手动清理备份**

```bash
# 清理7天前的Redis备份
find backups/ -name "redis_*.rdb" -mtime +7 -delete
find backups/ -name "redis_aof_*.aof" -mtime +7 -delete

# 清理30天前的应用备份
find backups/ -name "app_data_*.tar.gz" -mtime +30 -delete
find backups/ -name "conversations_*.tar.gz" -mtime +30 -delete
find backups/ -name "config_*.tar.gz" -mtime +30 -delete

# 查看磁盘使用情况
du -sh backups/
```

## 🔒 安全备份最佳实践

### **1. 本地备份安全**

```bash
# 设置备份目录权限
chmod 700 backups/
chmod 600 backups/*

# 加密重要备份
tar -czf - data/redis/ | gpg --symmetric --cipher-algo AES256 -o backups/redis_encrypted.tar.gz.gpg
```

### **2. 远程备份**

```bash
# 同步到外部存储
rsync -avz --delete backups/ user@remote-server:/backup/conversation-system/

# 上传到云存储（示例）
aws s3 sync backups/ s3://your-bucket/conversation-system-backups/
```

### **3. 备份验证**

```bash
# 验证Redis备份文件完整性
redis-check-rdb backups/redis_*.rdb

# 验证压缩文件完整性
gzip -t backups/*.tar.gz

# 测试备份可恢复性
./scripts/restore_backup.sh <timestamp> --dry-run
```

## 🚨 应急恢复场景

### **场景1：Redis数据损坏**

```bash
# 1. 停止Redis服务
docker-compose stop redis

# 2. 恢复最新的Redis备份
cp backups/redis_latest.rdb data/redis/dump.rdb
cp backups/redis_aof_latest.aof data/redis/appendonly.aof

# 3. 重启Redis
docker-compose start redis
```

### **场景2：整个系统重装**

```bash
# 1. 保存备份文件到安全位置
cp -r backups/ /external/storage/

# 2. 重新部署系统
git clone <repo> && cd conversation-system

# 3. 恢复备份
cp -r /external/storage/backups/ ./
./scripts/restore_backup.sh <latest-timestamp>

# 4. 启动系统
./scripts/start.sh
```

### **场景3：配置文件错误**

```bash
# 恢复配置文件（不影响数据）
tar -xzf backups/config_<timestamp>.tar.gz
```

## 📊 备份监控和报告

### **备份状态检查脚本**

```bash
#!/bin/bash
# 创建备份状态检查脚本
cat > scripts/backup_status.sh << 'EOF'
#!/bin/bash
echo "📊 备份状态报告 - $(date)"
echo "=================================="

BACKUP_DIR="./backups"
LATEST_BACKUP=$(ls -t $BACKUP_DIR/backup_info_*.txt 2>/dev/null | head -1)

if [ -n "$LATEST_BACKUP" ]; then
    echo "✅ 最新备份："
    basename "$LATEST_BACKUP" | sed 's/backup_info_//' | sed 's/.txt//'
    echo ""
    echo "📋 备份详情："
    cat "$LATEST_BACKUP"
    echo ""
    echo "💾 备份文件大小："
    du -sh $BACKUP_DIR/* | tail -5
else
    echo "❌ 未找到备份文件"
fi

echo ""
echo "🗑️ 磁盘使用情况："
df -h . | tail -1
EOF

chmod +x scripts/backup_status.sh
```

### **定期备份报告**

```bash
# 添加到定时任务，每周发送备份报告
0 8 * * 1 cd /Users/linwenjie/workspace/conversation-system && ./scripts/backup_status.sh | mail -s "Conversation System Backup Report" your-email@example.com
```

## 🎯 总结：推荐备份策略

### **日常使用**

1. **自动备份**：设置每天凌晨2点自动备份
2. **手动备份**：重要配置更改后立即备份
3. **定期检查**：每周检查备份日志和文件完整性

### **命令速查**

| 操作 | 命令 |
|-----|------|
| 立即备份 | `./scripts/complete_backup.sh` |
| 恢复数据 | `./scripts/restore_backup.sh <timestamp>` |
| 设置自动备份 | `./scripts/setup_auto_backup.sh` |
| 查看备份状态 | `ls -la backups/` |
| 查看备份日志 | `tail -f logs/backup.log` |
| 清理旧备份 | 自动执行（7天/30天规则） |

### **应急联系**

- 备份文件位置：`./backups/`
- 日志文件位置：`./logs/backup.log`
- 恢复脚本：`./scripts/restore_backup.sh`
- 紧急备份：`./scripts/complete_backup.sh`

---

**🔒 重要提醒：**
- 定期测试备份恢复流程
- 保持多个备份副本（本地+远程）
- 关键数据变更前先备份
- 监控备份任务执行状态 