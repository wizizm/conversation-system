# Cursor MCP Server 配置指南

## 🎯 系统状态

✅ **Docker服务运行状态**: 本地模式运行 (推荐)
✅ **MCP Server**: 完全正常 (7/7 核心功能通过测试)
✅ **API服务**: http://localhost:9000 正常响应
✅ **Redis**: localhost:6379 正常运行
✅ **数据挂载**: `/Users/linwenjie/Documents/知识库/conversations`

## 🔧 Cursor MCP 配置

### 方法1: 直接运行配置 (推荐)

将以下配置添加到 Cursor 的 MCP 配置文件中：

```json
{
  "mcpServers": {
    "conversation-system": {
      "command": "python",
      "args": [
        "/Users/linwenjie/workspace/conversation-system/mcp-server/main.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/linwenjie/workspace/conversation-system/mcp-server",
        "CONVERSATION_API_URL": "http://localhost:9000",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 方法2: 脚本启动配置

如果需要通过脚本启动，使用：

```json
{
  "mcpServers": {
    "conversation-system": {
      "command": "bash",
      "args": [
        "/Users/linwenjie/workspace/conversation-system/scripts/start_mcp_for_cursor.sh"
      ],
      "env": {
        "CONVERSATION_API_URL": "http://localhost:9000"
      }
    }
  }
}
```

## 🚀 启动步骤

### 1. 启动系统服务
```bash
cd /Users/linwenjie/workspace/conversation-system
make start-all
```

### 2. 验证服务状态
```bash
make status
```

### 3. 测试MCP功能
```bash
make test-mcp
```

### 4. 应用Cursor配置
将上述JSON配置添加到Cursor的MCP配置文件中。

## 📊 系统功能

### ✅ 核心功能 (7/7 通过测试)
1. **Enhanced API连接** - 成功连接v2.0 API
2. **Enhanced消息功能** - 智能压缩(36%节约率) + 技术用语提取
3. **适应性上下文获取** - 4个详细级别的上下文管理
4. **技术用语搜索** - 智能搜索和分类
5. **压缩分析** - 自动内容压缩和要点提取
6. **扩展分析** - 统计和见解生成
7. **Enhanced MCP启动** - 完整的MCP服务器功能

### 💾 数据管理
- **数据目录**: `/Users/linwenjie/Documents/知识库/conversations/data`
- **日志目录**: `/Users/linwenjie/Documents/知识库/conversations/logs`
- **备份目录**: `/Users/linwenjie/Documents/知识库/conversations/backups`
- **会话文件**: `/Users/linwenjie/Documents/知识库/conversations`

### 🔄 自动备份
- **频率**: 每小时自动备份
- **保留**: 最近3份备份
- **监控**: `make backup-monitor`

## 🛠️ 常用命令

```bash
# 启动系统
make start-all

# 查看状态
make status

# 查看日志
make logs-mcp

# 测试功能
make test-all

# 备份管理
make backup
make backup-monitor

# 停止服务
make stop
```

## 🔍 故障排除

### MCP Server无响应
```bash
# 重启MCP Server
pkill -f "main.py"
cd mcp-server && python main.py &
```

### API服务异常
```bash
# 检查API健康状态
curl http://localhost:9000/health
```

### Redis连接问题
```bash
# 检查Redis状态
redis-cli ping
```

## 📈 性能指标

当前系统性能：
- **压缩效率**: 36% 存储节约
- **技术识别**: 12个术语自动提取  
- **响应时间**: < 3秒
- **数据统计**: 444 bytes总计节约
- **消息存储**: 实时压缩存储
- **上下文管理**: 4级自适应获取

## ⚡ 快速验证

运行完整测试确保系统正常：
```bash
make test-all
```

预期结果: `7成功, 0警告, 0错误`

## 🎯 下一步

1. 将配置文件内容复制到Cursor的MCP配置中
2. 重启Cursor使配置生效
3. 在Cursor中测试MCP连接
4. 开始使用Enhanced Conversation System功能

---
**系统版本**: v2.0.0  
**最后更新**: $(date)  
**状态**: 生产就绪 🚀 