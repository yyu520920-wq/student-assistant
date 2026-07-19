#!/usr/bin/env python3
"""
大学日程计划 v1.3 — 一键启动脚本
功能：自动初始化数据 + 启动 Web 服务 + 显示手机访问地址
用法：python start.py
"""

import sys, os
from pathlib import Path

# 确保能找到 scripts 和 web 模块
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "web"))

# 第一步：初始化数据（如果还没有）
from engine import BASE, _cs, init

if not BASE.exists() or not (BASE / "current.json").exists():
    print("📦 首次使用，正在初始化示例数据...")
    init()
    print()
else:
    sem = _cs()
    print(f"📚 当前学期：{sem}")
    print()

# 第二步：启动 Web 服务
from server import run

if __name__ == "__main__":
    port = 5000
    # 支持命令行指定端口：python start.py 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port=port, open_browser=True)
