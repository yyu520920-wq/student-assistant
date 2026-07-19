#!/usr/bin/env bash
# 大学生助手 - 一键安装/测试脚本
# 用法: bash install.sh

set -e

echo "🎓 大学生助手 v1.0 安装"
echo "========================"
echo ""

# 检查 Python
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1)
    echo "✅ $PY_VERSION"
else
    echo "❌ 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查 Python 版本 >= 3.8
PY_MAJOR=$(python3 -c "import sys; print(sys.version_info[0])")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info[1])")
if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]); then
    echo "❌ 需要 Python 3.8+，当前版本: $PY_MAJOR.$PY_MINOR"
    exit 1
fi

# 初始化
echo ""
echo "📦 初始化数据..."
python3 scripts/student_engine.py init

echo ""
echo "========================"
echo "✅ 安装完成！"
echo ""
echo "快速上手:"
echo "  python3 scripts/student_engine.py schedule show    # 查看课表"
echo "  python3 scripts/student_engine.py schedule today   # 今日课程"
echo "  python3 scripts/student_engine.py homework list    # 查看作业"
echo "  python3 scripts/student_engine.py exam countdown   # 考试倒计时"
echo "  python3 scripts/student_engine.py remind           # 每日提醒"
echo ""
echo "运行测试:"
echo "  python3 scripts/test.py"
echo ""
echo "查看帮助:"
echo "  python3 scripts/student_engine.py --help"
