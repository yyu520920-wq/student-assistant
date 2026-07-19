#!/usr/bin/env python3
"""大学生助手 v2.0 自动化测试"""
import subprocess, sys, os, json, shutil, tempfile
from pathlib import Path

ENGINE = os.path.join(os.path.dirname(__file__), "engine.py")
PASS = FAIL = 0

def run(cmd, expected=None):
    global PASS, FAIL
    full = f"python3 {ENGINE} {cmd}"
    print(f"\n{'─'*50}\n🔧 {cmd}")
    try:
        r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=30)
        out = r.stdout + r.stderr
        if expected:
            if expected in out:
                print(f"✅ 通过"); PASS += 1
            else:
                print(f"❌ 未找到 '{expected[:40]}'"); print(out[:200]); FAIL += 1
        else:
            if r.returncode == 0: print(f"✅ 通过"); PASS += 1
            else: print(f"❌ exit {r.returncode}"); FAIL += 1
        return out
    except Exception as e:
        print(f"❌ {e}"); FAIL += 1; return ""

def main():
    global PASS, FAIL
    data_dir = Path.home() / ".student-assistant"
    if data_dir.exists(): shutil.rmtree(data_dir)

    print("="*50+"\n🎓 v2.0 自动化测试\n"+"="*50)

    # 1. init + 多学期
    print("\n📦 多学期管理")
    run("init", "已创建示例课表")
    run("semester new 2025-秋季", "已创建学期")
    run("semester list", "2025-秋季")
    run("semester list", "默认学期")
    run("semester switch 默认学期", "已切换到")

    # 2. 课表
    print("\n📅 课表")
    run("schedule show", "高等数学")
    run("schedule today", "今天")

    # 3. 作业
    print("\n📝 作业")
    run("homework list", "习题")
    run("homework done 1", "已完成")
    run("homework delete 2", "已删除")

    # 4. 考试
    print("\n⏰ 考试")
    run("exam list", "期中考试")
    run("exam countdown", "倒计时")
    run("exam countdown", "▓")

    # 5. 提醒
    print("\n🔔 提醒")
    run("remind", "今日提醒")

    # 6. iCal 导出
    print("\n📤 iCal 导出")
    run("export ical -o /tmp/test.ics", "已导出")
    assert Path("/tmp/test.ics").exists(), "ics 文件未生成"
    print("✅ ics 文件验证通过")

    # 7. 边界
    print("\n🧪 边界")
    shutil.rmtree(data_dir)
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    run("schedule show", "课表为空")
    run("exam countdown", "暂无考试")

    print("\n"+"="*50)
    print(f"📊 {PASS} 通过, {FAIL} 失败, 共 {PASS+FAIL}")
    print("="*50)
    if FAIL: print("\n❌ 失败！"); sys.exit(1)
    else: print("\n🎉 全部通过！")
    shutil.rmtree(data_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
