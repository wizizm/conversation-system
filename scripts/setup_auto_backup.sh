#!/usr/bin/env bash
set -e

# 🌟 Enhanced Conversation System - 自动备份设置脚本
# 配置cron定时任务实现自动备份

PROJECT_DIR=$(pwd)
SCRIPT_PATH="$PROJECT_DIR/scripts/complete_backup.sh"

echo "⏰ Enhanced Conversation System - 自动备份设置..."
echo "📁 项目目录: $PROJECT_DIR"

# 检查备份脚本是否存在
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ 备份脚本不存在: $SCRIPT_PATH"
    exit 1
fi

# 显示当前定时任务
echo ""
echo "📋 当前用户的定时任务:"
crontab -l 2>/dev/null || echo "  - 无定时任务"

echo ""
echo "⚙️ 自动备份选项:"
echo "  1. 每天凌晨2点备份 (推荐)"
echo "  2. 每12小时备份一次"
echo "  3. 每周日凌晨2点备份"
echo "  4. 自定义备份时间"
echo "  5. 清除自动备份"
echo ""

read -p "🤔 请选择选项 (1-5): " CHOICE

case $CHOICE in
    1)
        CRON_SCHEDULE="0 2 * * *"
        DESCRIPTION="每天凌晨2点"
        ;;
    2)
        CRON_SCHEDULE="0 */12 * * *"
        DESCRIPTION="每12小时"
        ;;
    3)
        CRON_SCHEDULE="0 2 * * 0"
        DESCRIPTION="每周日凌晨2点"
        ;;
    4)
        echo ""
        echo "📝 Cron格式说明:"
        echo "  分钟 小时 日期 月份 星期"
        echo "  0    2    *    *    *     # 每天凌晨2点"
        echo "  0    */6  *    *    *     # 每6小时"
        echo "  30   1    *    *    1     # 每周一凌晨1:30"
        echo ""
        read -p "请输入cron表达式: " CRON_SCHEDULE
        DESCRIPTION="自定义时间"
        ;;
    5)
        echo ""
        echo "🗑️ 清除自动备份定时任务..."
        # 移除包含此脚本的定时任务
        (crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH") | crontab -
        echo "✅ 自动备份已清除"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

# 创建日志目录
mkdir -p logs

# 生成定时任务条目
CRON_ENTRY="$CRON_SCHEDULE cd $PROJECT_DIR && $SCRIPT_PATH >> logs/backup.log 2>&1"

echo ""
echo "📝 将添加的定时任务:"
echo "   时间: $DESCRIPTION"
echo "   命令: $CRON_ENTRY"
echo ""

read -p "🤔 确认添加自动备份? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ 自动备份设置已取消"
    exit 0
fi

# 添加定时任务
echo ""
echo "⏰ 设置定时任务..."

# 备份现有的crontab
crontab -l 2>/dev/null > /tmp/current_crontab || touch /tmp/current_crontab

# 移除旧的备份任务（如果存在）
grep -v "$SCRIPT_PATH" /tmp/current_crontab > /tmp/new_crontab || touch /tmp/new_crontab

# 添加新的备份任务
echo "$CRON_ENTRY" >> /tmp/new_crontab

# 安装新的crontab
crontab /tmp/new_crontab

# 清理临时文件
rm -f /tmp/current_crontab /tmp/new_crontab

echo "✅ 自动备份设置完成！"
echo ""
echo "📋 设置详情:"
echo "   备份频率: $DESCRIPTION"
echo "   备份脚本: $SCRIPT_PATH"
echo "   日志文件: $PROJECT_DIR/logs/backup.log"
echo ""
echo "🔍 验证设置:"
echo "   查看定时任务: crontab -l"
echo "   查看备份日志: tail -f logs/backup.log"
echo "   手动测试: $SCRIPT_PATH"
echo ""
echo "📁 备份文件位置: $PROJECT_DIR/backups/"
echo ""
echo "🎯 重要提醒:"
echo "   - 备份文件会自动清理（RDB文件7天，其他30天）"
echo "   - 定期检查备份日志确保正常运行"
echo "   - 可以随时运行 ./scripts/complete_backup.sh 手动备份"
echo ""
echo "✅ 自动备份配置完成！" 