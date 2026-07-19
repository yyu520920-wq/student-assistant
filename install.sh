#!/bin/bash
# 学生助手 v1.1 — 一键安装脚本
set -e

echo "🎓 学生助手 v1.1 安装"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3.11+"
    exit 1
fi

echo "✅ Python $(python3 --version)"

# 安装 Flask（Web 界面依赖，可选）
echo ""
read -p "是否安装 Web 界面依赖 (Flask)? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    pip3 install flask 2>/dev/null || echo "⚠️ Flask 安装失败，Web 界面不可用，CLI 不受影响"
fi

# 初始化数据
echo ""
python3 scripts/engine.py init

echo ""
echo "🎉 安装完成！"
echo ""
echo "使用方法："
echo "  CLI:  python3 scripts/engine.py today"
echo "  Web:  python3 web/server.py"
echo ""
echo "更多命令请查看 README.md"
