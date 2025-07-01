# Cursor MCP Setup Guide for Conversation System

本指南将帮助你在Cursor中配置并使用conversation-system的MCP Server（修正版本）。

## 🚀 快速开始

### 1. 启动Docker服务（仅API和Redis）

```bash
# 启动API和Redis服务
docker-compose up -d conversation_app conversation_redis

# 检查服务状态
docker ps
```

### 2. 验证服务运行

```bash
# 检查主API服务
curl http://localhost:9000/health

# 检查Redis连接
docker exec conversation_redis redis-cli ping
```

## 📱 Cursor配置

### 最终正确配置
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

### 配置文件位置
- **macOS**: `~/Library/Application Support/Cursor/User/settings.json`
- **Windows**: `%APPDATA%\\Cursor\\User\\settings.json`
- **Linux**: `~/.config/Cursor/User/settings.json`

## 🏗️ 架构说明

### 最终架构（稳定版本）
```
Cursor (MCP Client)
    ↓ STDIO
MCP Server (本地运行)
    ↓ HTTP API
Docker Services:
  - API Server (端口9000)
  - Redis (端口6379)
```

### 为什么选择这种架构？
1. **STDIO传输稳定**：MCP的原生传输方式，与Cursor完美兼容
2. **Docker服务隔离**：API和Redis在容器中，便于管理
3. **本地MCP响应快**：避免了容器间通信的复杂性
4. **易于调试**：MCP Server日志直接可见

## 🛠️ 依赖安装

### 本地环境依赖
```bash
cd /Users/linwenjie/workspace/conversation-system
pip install fastmcp httpx structlog redis python-dotenv requests click
```

## 🔧 故障排除

### 常见问题

1. **MCP Server无法启动**
   ```bash
   # 检查依赖是否安装
   pip list | grep fastmcp
   
   # 手动测试MCP Server
   cd mcp-server && python main.py
   ```

2. **API连接失败**
   ```bash
   # 检查Docker服务
   docker ps | grep conversation
   
   # 测试API连接
   curl http://localhost:9000/health
   ```

3. **Cursor连接问题**
   - 确保路径正确指向本地文件
   - 重启Cursor使配置生效
   - 检查Python环境是否可访问

### 验证步骤

```bash
# 1. 启动Docker服务
docker-compose up -d conversation_app conversation_redis

# 2. 测试本地MCP Server
cd mcp-server && echo '{"jsonrpc":"2.0","id":"test","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python main.py

# 3. 验证API连接
curl http://localhost:9000/health
```

## 🎯 使用示例

配置完成后，在Cursor中可以使用：

1. **记录对话**: `record_current_conversation`
2. **搜索历史**: `search_conversation_history`
3. **分析上下文**: `get_conversation_context`
4. **智能压缩**: `analyze_text_compression`

## 📋 部署总结

### ✅ 解决的问题
- Docker STDIO传输问题
- FastMCP HTTP兼容性问题
- 容器间网络复杂性
- 依赖管理问题

### 🏆 最终优势
- 稳定的STDIO传输
- 简化的架构
- 更好的调试体验
- 保持Docker的便利性

---

**🚀 现在您可以在Cursor中使用稳定的conversation-system MCP功能了！**
