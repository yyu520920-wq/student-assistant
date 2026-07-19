#!/usr/bin/env python3
"""
大学生助手 - 自动化测试脚本
测试所有功能模块，确保每个命令都能正常运行

用法：
  python3 test.py
"""

import subprocess
import sys
import os
import json
import tempfile
from pathlib import Path

ENGINE = os.path.join(os.path.dirname(__file__), "student_engine.py")
PASS = 0
FAIL = 0

def run(cmd: str, expected_in_output: str = None):
    """运行命令并检查结果"""
    global PASS, FAIL
    full_cmd = f"python3 {ENGINE} {cmd}"
    print(f"\n{'─'*60}")
    print(f"🔧 测试: {cmd}")

    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr

        if expected_in_output:
            if expected_in_output in output:
                print(f"✅ 通过 — 找到预期内容: '{expected_in_output[:50]}...'")
                PASS += 1
            else:
                print(f"❌ 失败 — 未找到: '{expected_in_output[:50]}...'")
                print(f"   输出片段: {output[:200]}")
                FAIL += 1
        else:
            if result.returncode == 0:
                print(f"✅ 通过 (exit 0)")
                PASS += 1
            else:
                print(f"❌ 失败 (exit {result.returncode})")
                FAIL += 1
        return output
    except subprocess.TimeoutExpired:
        print(f"❌ 超时")
        FAIL += 1
        return ""
    except Exception as e:
        print(f"❌ 异常: {e}")
        FAIL += 1
        return ""


def main():
    global PASS, FAIL
    print("=" * 60)
    print("🎓 大学生助手 v1.0 — 自动化测试")
    print("=" * 60)

    # ── 清理环境 ──
    data_dir = Path.home() / ".student-assistant"
    if data_dir.exists():
        import shutil
        shutil.rmtree(data_dir)
    print("\n🧹 已清理测试环境")

    # ── 1. init ──
    print("\n\n📦 模块 1: 初始化")
    output = run("init", "数据目录")
    # 验证 init 输出包含所有预期内容
    assert "已创建示例课表" in output, "init 未创建课表"
    assert "已创建示例作业" in output, "init 未创建作业"
    assert "已创建示例考试" in output, "init 未创建考试"
    print("✅ init 输出验证通过")

    # 验证文件存在
    assert (data_dir / "schedule.json").exists(), "schedule.json 未创建"
    assert (data_dir / "homework.json").exists(), "homework.json 未创建"
    assert (data_dir / "exam.json").exists(), "exam.json 未创建"
    print("✅ 数据文件验证通过")

    # ── 2. 课表 ──
    print("\n\n📅 模块 2: 课表管理")
    run("schedule show", "高等数学")
    run("schedule show", "大学英语")
    run("schedule today", "今天")  # 任何一天都能输出

    # 测试 JSON 导入
    test_schedule = [
        {"day": 1, "time": "08:00-09:40", "course": "测试课程A", "teacher": "测试老师", "location": "测试教室", "weeks": "1-16"},
        {"day": 3, "time": "14:00-15:40", "course": "测试课程B", "teacher": "测试老师2", "location": "测试教室2", "weeks": "1-8"},
    ]
    tmp_json = "/tmp/test_schedule.json"
    with open(tmp_json, "w", encoding="utf-8") as f:
        json.dump(test_schedule, f, ensure_ascii=False)
    run(f"schedule import {tmp_json}", "已导入 2 门课程")
    run("schedule show", "测试课程A")
    run("schedule show", "测试课程B")

    # 测试 CSV 导入
    tmp_csv = "/tmp/test_schedule.csv"
    with open(tmp_csv, "w", encoding="utf-8") as f:
        f.write("day,time,course,teacher,location,weeks\n")
        f.write("5,10:00-11:40,CSV测试课,CSV老师,CSV教室,1-16\n")
    run(f"schedule import {tmp_csv}", "已导入 1 门课程")
    run("schedule show", "CSV测试课")

    # 测试错误格式
    run(f"schedule import /tmp/nonexistent.json", "文件不存在")

    # ── 3. 作业 ──
    print("\n\n📝 模块 3: 作业管理")
    # 重新 init 恢复示例数据
    import shutil
    shutil.rmtree(data_dir)
    run("init", "已创建示例作业")

    run("homework list", "高等数学")
    run("homework list", "习题")
    run("homework list --all", "待完成")
    run("homework done 1", "已完成")
    run("homework list --all", "已完成")
    run("homework delete 2", "已删除")

    # ── 4. 考试 ──
    print("\n\n⏰ 模块 4: 考试管理")
    shutil.rmtree(data_dir)
    run("init", "已创建示例考试")

    run("exam list", "高等数学")
    run("exam list", "期中考试")
    run("exam countdown", "倒计时")
    run("exam countdown", "▓")
    run("exam delete 1", "已删除")

    # ── 5. 提醒 ──
    print("\n\n🔔 模块 5: 每日提醒")
    shutil.rmtree(data_dir)
    run("init", "已创建示例课表")

    run("remind", "今日提醒")
    run("remind", "今日课程")
    run("remind", "即将到期作业")
    run("remind", "临近考试")

    # ── 6. 边界情况 ──
    print("\n\n🧪 模块 6: 边界情况")
    shutil.rmtree(data_dir)
    # 空数据
    os.makedirs(data_dir, exist_ok=True)
    run("schedule show", "课表为空")
    run("homework list", "暂无作业")
    run("exam list", "暂无考试")
    run("exam countdown", "暂无考试")

    # ── 结果 ──
    print("\n\n" + "=" * 60)
    print(f"📊 测试结果: {PASS} 通过, {FAIL} 失败, 共 {PASS+FAIL} 项")
    print("=" * 60)

    if FAIL > 0:
        print("\n❌ 部分测试失败，请检查！")
        sys.exit(1)
    else:
        print("\n🎉 全部测试通过！")

    # 清理
    if data_dir.exists():
        shutil.rmtree(data_dir)


if __name__ == "__main__":
    main()
