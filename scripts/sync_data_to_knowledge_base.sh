#!/usr/bin/env bash
set -e

# 🔄 数据同步脚本：项目目录 ⇄ 知识库目录
# 用于在项目本地目录和知识库目录之间同步数据

KNOWLEDGE_BASE_DIR="/Users/linwenjie/Documents/知识库/conversations"
PROJECT_DIR="/Users/linwenjie/workspace/conversation-system"

echo "🔄 数据同步工具"
echo "=================="
echo ""

# 检查目录是否存在
if [ ! -d "$KNOWLEDGE_BASE_DIR" ]; then
    echo "📁 创建知识库目录..."
    mkdir -p "$KNOWLEDGE_BASE_DIR"/{data/{redis,app},logs,backups}
fi

echo "📊 当前状态:"
echo "项目目录: $PROJECT_DIR"
echo "知识库目录: $KNOWLEDGE_BASE_DIR"
echo ""

# 选择同步方向
echo "请选择操作:"
echo "1. 项目 → 知识库 (将项目数据备份到知识库)"
echo "2. 知识库 → 项目 (从知识库恢复数据到项目)"
echo "3. 双向同步 (智能合并最新数据)"
echo "4. 查看状态对比"
echo ""

read -p "输入选择 (1-4): " choice

case $choice in
    1)
        echo "📤 同步：项目 → 知识库..."
        rsync -av --delete "$PROJECT_DIR/data/" "$KNOWLEDGE_BASE_DIR/data/" || true
        rsync -av --delete "$PROJECT_DIR/logs/" "$KNOWLEDGE_BASE_DIR/logs/" || true
        rsync -av --delete "$PROJECT_DIR/backups/" "$KNOWLEDGE_BASE_DIR/backups/" || true
        rsync -av --delete "$PROJECT_DIR/conversations/" "$KNOWLEDGE_BASE_DIR/" || true
        echo "✅ 同步完成：项目 → 知识库"
        ;;
    2)
        echo "📥 同步：知识库 → 项目..."
        rsync -av --delete "$KNOWLEDGE_BASE_DIR/data/" "$PROJECT_DIR/data/" || true
        rsync -av --delete "$KNOWLEDGE_BASE_DIR/logs/" "$PROJECT_DIR/logs/" || true
        rsync -av --delete "$KNOWLEDGE_BASE_DIR/backups/" "$PROJECT_DIR/backups/" || true
        rsync -av --delete "$KNOWLEDGE_BASE_DIR/" "$PROJECT_DIR/conversations/" --exclude='data' --exclude='logs' --exclude='backups' || true
        echo "✅ 同步完成：知识库 → 项目"
        ;;
    3)
        echo "🔄 双向智能同步..."
        rsync -av "$PROJECT_DIR/data/" "$KNOWLEDGE_BASE_DIR/data/" || true
        rsync -av "$PROJECT_DIR/logs/" "$KNOWLEDGE_BASE_DIR/logs/" || true
        rsync -av "$PROJECT_DIR/backups/" "$KNOWLEDGE_BASE_DIR/backups/" || true
        rsync -av "$PROJECT_DIR/conversations/" "$KNOWLEDGE_BASE_DIR/" || true
        
        rsync -av "$KNOWLEDGE_BASE_DIR/data/" "$PROJECT_DIR/data/" || true
        rsync -av "$KNOWLEDGE_BASE_DIR/logs/" "$PROJECT_DIR/logs/" || true
        rsync -av "$KNOWLEDGE_BASE_DIR/backups/" "$PROJECT_DIR/backups/" || true
        rsync -av "$KNOWLEDGE_BASE_DIR/" "$PROJECT_DIR/conversations/" --exclude='data' --exclude='logs' --exclude='backups' || true
        echo "✅ 双向同步完成"
        ;;
    4)
        echo "📊 状态对比:"
        echo ""
        echo "📁 Data目录:"
        echo "  项目: $(du -sh "$PROJECT_DIR/data" 2>/dev/null | cut -f1 || echo "0B")"
        echo "  知识库: $(du -sh "$KNOWLEDGE_BASE_DIR/data" 2>/dev/null | cut -f1 || echo "0B")"
        echo ""
        echo "📄 Logs目录:"
        echo "  项目: $(du -sh "$PROJECT_DIR/logs" 2>/dev/null | cut -f1 || echo "0B")"
        echo "  知识库: $(du -sh "$KNOWLEDGE_BASE_DIR/logs" 2>/dev/null | cut -f1 || echo "0B")"
        echo ""
        echo "💾 Backups目录:"
        echo "  项目: $(du -sh "$PROJECT_DIR/backups" 2>/dev/null | cut -f1 || echo "0B")"
        echo "  知识库: $(du -sh "$KNOWLEDGE_BASE_DIR/backups" 2>/dev/null | cut -f1 || echo "0B")"
        echo ""
        echo "💬 Conversations目录:"
        echo "  项目: $(du -sh "$PROJECT_DIR/conversations" 2>/dev/null | cut -f1 || echo "0B")"
        echo "  知识库: $(du -sh "$KNOWLEDGE_BASE_DIR" 2>/dev/null | cut -f1 || echo "0B")"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎯 操作完成！" 