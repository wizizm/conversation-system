# Enhanced Conversation System - Makefile
# 简化MCP Server和备份管理操作

.PHONY: help start-all start-mcp start-docker stop backup backup-monitor sync-data status logs clean

# 默认目标
help:
	@echo "🎯 Enhanced Conversation System 管理命令"
	@echo "=========================================="
	@echo ""
	@echo "🚀 启动服务:"
	@echo "  make start-all     - 启动完整系统（本地模式）"
	@echo "  make start-docker  - 启动Docker化系统"
	@echo "  make start-mcp     - 仅启动MCP Server（本地）"
	@echo ""
	@echo "🛑 停止服务:"
	@echo "  make stop          - 停止所有服务"
	@echo "  make stop-docker   - 停止Docker服务"
	@echo ""
	@echo "💾 备份管理:"
	@echo "  make backup        - 执行手动备份"
	@echo "  make backup-monitor - 打开备份监控器"
	@echo "  make backup-auto   - 设置自动备份"
	@echo "  make sync-data     - 数据同步工具"
	@echo ""
	@echo "📊 监控与状态:"
	@echo "  make status        - 查看服务状态"
	@echo "  make logs          - 查看日志"
	@echo "  make logs-mcp      - 查看MCP日志"
	@echo ""
	@echo "🧪 测试验证:"
	@echo "  make test          - 测试基础服务"
	@echo "  make test-mcp      - 测试MCP功能"
	@echo "  make test-all      - 运行完整测试"
	@echo ""
	@echo "🧹 清理维护:"
	@echo "  make clean         - 清理临时文件"
	@echo "  make clean-backups - 清理旧备份文件"
	@echo ""

# 启动完整系统（本地模式）
start-all:
	@echo "🚀 启动Enhanced Conversation System（本地模式）..."
	@./scripts/start_local_mcp.sh

# 启动Docker化系统
start-docker:
	@echo "🐳 启动Docker化系统..."
	@./scripts/start_with_mcp.sh

# 仅启动MCP Server（本地）
start-mcp:
	@echo "🤖 启动MCP Server（本地模式）..."
	@mkdir -p logs
	@cd mcp-server && python main.py > ../logs/mcp.log 2>&1 &
	@echo "✅ MCP Server已启动，日志: logs/mcp.log"

# 停止所有服务
stop:
	@echo "🛑 停止所有服务..."
	@pkill -f "main.py" || true
	@pkill -f "uvicorn" || true
	@pkill -f "redis-server" || true
	@echo "✅ 本地服务已停止"

# 停止Docker服务
stop-docker:
	@echo "🛑 停止Docker服务..."
	@docker-compose down
	@echo "✅ Docker服务已停止"

# 手动备份
backup:
	@echo "💾 执行手动备份..."
	@./scripts/complete_backup.sh

# 备份监控器
backup-monitor:
	@echo "🔍 打开备份监控器..."
	@if [ -f scripts/mcp_backup_monitor.sh ]; then \
		./scripts/mcp_backup_monitor.sh; \
	else \
		echo "❌ 监控器脚本不存在，请先启动Docker版本"; \
	fi

# 设置自动备份
backup-auto:
	@echo "⏰ 设置自动备份..."
	@./scripts/setup_auto_backup.sh

# 数据同步工具
sync-data:
	@echo "🔄 启动数据同步工具..."
	@./scripts/sync_data_to_knowledge_base.sh

# 查看服务状态
status:
	@echo "📊 服务状态检查:"
	@echo "=================="
	@echo ""
	@echo "🐳 Docker状态:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "Docker未运行"
	@echo ""
	@echo "🖥️ 本地进程:"
	@ps aux | grep -E "(main\.py|uvicorn|redis)" | grep -v grep || echo "无相关进程运行"
	@echo ""
	@echo "🌐 端口占用:"
	@lsof -i :8000 || echo "端口8000未占用"
	@lsof -i :6379 || echo "端口6379未占用"

# 查看日志
logs:
	@echo "📄 查看系统日志..."
	@if [ -f logs/app.log ]; then \
		tail -20 logs/app.log; \
	else \
		echo "无应用日志文件"; \
	fi

# 查看MCP日志
logs-mcp:
	@echo "📄 查看MCP Server日志..."
	@if docker ps | grep -q mcp_server; then \
		docker-compose logs -f mcp_server; \
	elif [ -f logs/mcp.log ]; then \
		tail -20 logs/mcp.log; \
	else \
		echo "无MCP日志文件"; \
	fi

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	@find . -name "*.tmp" -delete
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

# 清理旧备份文件
clean-backups:
	@echo "🗑️ 清理旧备份文件..."
	@KNOWLEDGE_BASE_DIR="/Users/linwenjie/Documents/知识库/conversations"; \
	if [ -d "$$KNOWLEDGE_BASE_DIR/backups" ]; then \
		find "$$KNOWLEDGE_BASE_DIR/backups" -name "*.tar.gz" -mtime +7 -delete; \
		find "$$KNOWLEDGE_BASE_DIR/backups" -name "*.txt" -mtime +7 -delete; \
		echo "✅ 已清理7天前的备份文件"; \
	else \
		echo "备份目录不存在"; \
	fi

# 安装依赖
install:
	@echo "📦 安装依赖..."
	@pip install -r requirements.txt
	@cd mcp-server && pip install -r requirements.txt
	@echo "✅ 依赖安装完成"

# 环境检查
check:
	@echo "🔍 环境检查..."
	@echo "Python版本: $(shell python --version)"
	@echo "Docker版本: $(shell docker --version 2>/dev/null || echo '未安装')"
	@echo "Redis状态: $(shell redis-cli ping 2>/dev/null || echo '未运行')"
	@echo "项目目录: $(shell pwd)"

# 初始化项目
init:
	@echo "🏗️ 初始化项目..."
	@KNOWLEDGE_BASE_DIR="/Users/linwenjie/Documents/知识库/conversations"; \
	mkdir -p "$$KNOWLEDGE_BASE_DIR/data/redis" "$$KNOWLEDGE_BASE_DIR/data/app" "$$KNOWLEDGE_BASE_DIR/logs" "$$KNOWLEDGE_BASE_DIR/backups" "$$KNOWLEDGE_BASE_DIR"; \
	for dir in data logs backups conversations; do \
		if [ ! -e "$$dir" ]; then \
			case $$dir in \
				conversations) ln -sf "$$KNOWLEDGE_BASE_DIR" "$$dir" ;; \
				data) ln -sf "$$KNOWLEDGE_BASE_DIR/data" "$$dir" ;; \
				logs) ln -sf "$$KNOWLEDGE_BASE_DIR/logs" "$$dir" ;; \
				backups) ln -sf "$$KNOWLEDGE_BASE_DIR/backups" "$$dir" ;; \
			esac; \
		fi; \
	done; \
	chmod +x scripts/*.sh
	@echo "✅ 项目初始化完成"

# 测试系统
test:
	@echo "🧪 测试系统..."
	@curl -s http://localhost:9000/health || echo "❌ API服务未响应"
	@redis-cli ping || echo "❌ Redis服务未响应"
	@echo "✅ 测试完成"

# 测试MCP功能
test-mcp:
	@echo "🧪 测试MCP Server功能..."
	@cd mcp-server && python test_mcp.py

# 测试所有功能
test-all:
	@echo "🧪 运行完整测试套件..."
	@make test
	@make test-mcp
	@echo "✅ 所有测试完成" 