#!/usr/bin/env bash
# 大学生助手 v1.1 - 一键安装脚本
set -e

echo "🎓 大学生助手 v1.1 安装"
echo "========================"

# 检查 Python
if command -v python3 &>/dev/null; then
    echo "✅ $(python3 --version)"
else
    echo "❌ 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

PY_MINOR=$(python3 -c "import sys; print(sys.version_info[1])")
if [ "$PY_MINOR" -lt 8 ]; then
    echo "❌ 需要 Python 3.8+"
    exit 1
fi

# 安装依赖
echo ""
echo "📦 安装依赖..."
pip3 install -q plyer easyocr Pillow flask 2>/dev/null || pip3 install plyer easyocr Pillow flask
echo "✅ 依赖安装完成"

# 初始化数据
echo ""
python3 scripts/engine.py init

echo ""
echo "========================"
echo "✅ 安装完成！"
echo ""
echo "快速上手："
echo ""
echo "  1. Web 可视化界面（推荐）："
echo "     python3 server.py"
echo "     浏览器打开 http://localhost:5000"
echo ""
echo "  2. 命令行："
echo "     python3 scripts/engine.py remind         # 今日提醒"
echo "     python3 scripts/engine.py schedule show  # 查看课表"
echo "     python3 scripts/engine.py exam countdown # 考试倒计时"
echo ""
echo "  3. 桌面通知："
echo "     python3 scripts/notifier.py              # 后台常驻"
echo "     python3 scripts/notifier.py --once       # 单次检查"
echo ""
echo "  4. OCR 识别课表截图："
echo "     python3 scripts/ocr_schedule.py 课表截图.png --auto-import"
echo ""
echo "  5. 导出日历："
echo "     python3 scripts/engine.py export ical -o 课表.ics"
echo ""
echo "运行测试："
echo "  python3 scripts/test.py"
