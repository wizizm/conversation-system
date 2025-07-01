# 🐳 Docker化的 Enhanced Conversation System v2.0 - MCP Server设置指南

## 🎯 概述

本指南介绍如何在Docker环境中运行Enhanced Conversation System的MCP Server，实现自动备份和数据持久化。

## 🐳 Docker环境特性

- **容器化运行**：隔离环境，稳定可靠
- **自动备份**：每小时执行，保留最近3份
- **数据持久化**：data和backups目录挂载到宿主机
- **健康监控**：内置健康检查和服务监控

## 📁 挂载目录结构

```
项目目录/
├── data/           -> /app/data (与主应用共享数据)
├── backups/        -> /app/backups (备份文件存储)
└── conversations/  -> /app/data/conversations (会话文件)
```

## 🚀 启动方式

### 1. 启动完整系统（推荐）
```bash
./scripts/start_with_mcp.sh
```

### 2. 单独启动MCP Server
```bash
docker-compose up -d mcp_server
```

## 🔧 管理命令

### 基本操作
```bash
# 查看服务状态
docker-compose ps mcp_server

# 查看实时日志
docker-compose logs -f mcp_server

# 重启服务
docker-compose restart mcp_server

# 停止服务
docker-compose down
```

### 备份操作
```bash
# 手动执行备份
docker-compose exec mcp_server /app/docker_backup.sh

# 查看备份文件
ls -la backups/

# 备份监控器
./scripts/mcp_backup_monitor.sh
```

## 📋 Claude Desktop配置

### 1. 配置文件位置
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. 配置内容
复制以下内容到Claude Desktop配置文件：

```json
{
  "mcpServers": {
    "conversation-system-docker": {
      "command": "docker",
      "args": [
        "exec", 
        "-i", 
        "conversation_mcp_server", 
        "python", 
        "/app/main.py"
      ],
      "env": {
        "CONVERSATION_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### 3. 配置步骤
1. 确保Docker服务运行：`./scripts/start_with_mcp.sh`
2. 复制上述配置到Claude Desktop配置文件
3. 重启Claude Desktop
4. 测试命令：`"记录这个对话"`

## 🧪 测试连接

在Claude Desktop中输入以下命令进行测试：

```
显示我的对话统计
```

**预期结果**：显示系统版本和统计信息

## ⚠️ 注意事项

- 确保容器名称为 `conversation_mcp_server`
- 确保主应用API在 `localhost:8000` 运行
- 如果遇到权限问题，检查Docker用户权限
- 备份文件自动保留最近3份，旧文件自动清理

## 🔍 故障排除

### 1. 检查容器状态
```bash
docker ps | grep mcp_server
```

### 2. 查看容器日志
```bash
docker logs conversation_mcp_server
```

### 3. 测试API连接
```bash
curl http://localhost:8000/health
```

### 4. 重启完整服务
```bash
./scripts/start_with_mcp.sh
```

### 5. 常见问题

#### 问题：容器无法启动
**解决方案**：
```bash
# 检查Docker服务状态
docker --version
docker-compose --version

# 清理并重新构建
docker-compose down
docker-compose up -d --build
```

#### 问题：Claude Desktop无法连接
**解决方案**：
```bash
# 确认容器运行状态
docker ps | grep mcp_server

# 确认容器名称正确
docker rename old_name conversation_mcp_server
```

#### 问题：备份功能异常
**解决方案**：
```bash
# 使用备份监控器
./scripts/mcp_backup_monitor.sh

# 手动测试备份
docker-compose exec mcp_server /app/docker_backup.sh
```

## 📊 监控与维护

### 自动备份监控
```bash
# 运行备份监控器
./scripts/mcp_backup_monitor.sh
```

### 日志监控
```bash
# 查看备份日志
docker-compose exec mcp_server tail -f /app/logs/backup.log

# 查看系统日志
docker-compose logs --follow mcp_server
```

### 磁盘空间监控
```bash
# 检查备份目录大小
du -sh backups/

# 检查容器磁盘使用
docker exec conversation_mcp_server df -h
```

## 🎯 最佳实践

1. **定期检查服务状态**：使用 `docker-compose ps` 检查服务运行状态
2. **监控备份文件**：定期运行 `./scripts/mcp_backup_monitor.sh`
3. **日志轮转**：定期清理过期的日志文件
4. **资源监控**：监控容器的CPU和内存使用情况
5. **安全更新**：定期更新Docker镜像和依赖包

## 🔗 相关文档

- [备份指南](../BACKUP_GUIDE.md)
- [变更日志](../CHANGE_LOG.md)
- [命令日志](../COMMAND_LOG.md)
- [使用说明](../USAGE.md) 