#!/usr/bin/env python3
"""
大学生助手 - 核心引擎 v1.0
功能：课表导入、作业管理、考试倒计时、每日提醒

用法：
  python3 student_engine.py init              # 初始化数据目录
  python3 student_engine.py schedule import <文件>  # 导入课表
  python3 student_engine.py schedule show     # 查看课表
  python3 student_engine.py schedule today    # 今日课程
  python3 student_engine.py homework add      # 添加作业
  python3 student_engine.py homework list     # 查看作业
  python3 student_engine.py homework done <id> # 标记完成
  python3 student_engine.py exam add          # 添加考试
  python3 student_engine.py exam list         # 查看考试
  python3 student_engine.py exam countdown    # 考试倒计时
  python3 student_engine.py remind            # 今日提醒汇总
"""

import json
import os
import sys
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# ── 数据目录 ──────────────────────────────────────────────
DATA_DIR = Path.home() / ".student-assistant"
SCHEDULE_FILE = DATA_DIR / "schedule.json"
HOMEWORK_FILE = DATA_DIR / "homework.json"
EXAM_FILE = DATA_DIR / "exam.json"


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path) -> List[Dict]:
    """安全加载 JSON 文件"""
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_json(filepath: Path, data: List[Dict]):
    """保存 JSON 文件"""
    ensure_data_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── 课表模块 ──────────────────────────────────────────────

WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def init_cmd():
    """初始化：创建数据目录和示例文件"""
    ensure_data_dir()

    # 创建示例课表
    if not SCHEDULE_FILE.exists():
        sample_schedule = [
            {"day": 1, "time": "08:00-09:40", "course": "高等数学", "teacher": "张老师", "location": "教1-301", "weeks": "1-16"},
            {"day": 1, "time": "10:00-11:40", "course": "大学英语", "teacher": "李老师", "location": "教2-205", "weeks": "1-16"},
            {"day": 2, "time": "08:00-09:40", "course": "线性代数", "teacher": "王老师", "location": "教1-201", "weeks": "1-16"},
            {"day": 2, "time": "14:00-15:40", "course": "程序设计基础", "teacher": "赵老师", "location": "机房3", "weeks": "1-16"},
            {"day": 3, "time": "10:00-11:40", "course": "大学物理", "teacher": "刘老师", "location": "教3-102", "weeks": "1-16"},
            {"day": 3, "time": "14:00-15:40", "course": "体育", "teacher": "陈老师", "location": "操场", "weeks": "1-16"},
            {"day": 4, "time": "08:00-09:40", "course": "高等数学", "teacher": "张老师", "location": "教1-301", "weeks": "1-16"},
            {"day": 4, "time": "14:00-15:40", "course": "思想政治", "teacher": "周老师", "location": "教4-101", "weeks": "1-16"},
            {"day": 5, "time": "10:00-11:40", "course": "大学英语", "teacher": "李老师", "location": "教2-205", "weeks": "1-16"},
        ]
        save_json(SCHEDULE_FILE, sample_schedule)
        print("✅ 已创建示例课表（10门课程）")

    # 创建示例作业
    if not HOMEWORK_FILE.exists():
        today = date.today()
        sample_homework = [
            {"id": 1, "course": "高等数学", "title": "习题3.2 第1-10题", "deadline": (today + timedelta(days=3)).isoformat(), "done": False, "note": "交纸质版"},
            {"id": 2, "course": "大学英语", "title": "Unit 5 课后翻译", "deadline": (today + timedelta(days=5)).isoformat(), "done": False, "note": "提交到学习通"},
            {"id": 3, "course": "程序设计基础", "title": "实验报告：排序算法", "deadline": (today + timedelta(days=7)).isoformat(), "done": False, "note": "含代码和运行截图"},
        ]
        save_json(HOMEWORK_FILE, sample_homework)
        print("✅ 已创建示例作业（3项）")

    # 创建示例考试
    if not EXAM_FILE.exists():
        today = date.today()
        sample_exams = [
            {"id": 1, "course": "高等数学", "type": "期中考试", "date": (today + timedelta(days=14)).isoformat(), "location": "教1-301", "note": "第1-4章"},
            {"id": 2, "course": "大学英语", "type": "期末考试", "date": (today + timedelta(days=45)).isoformat(), "location": "待定", "note": "含听力"},
        ]
        save_json(EXAM_FILE, sample_exams)
        print("✅ 已创建示例考试（2场）")

    print(f"\n📁 数据目录: {DATA_DIR}")
    print("💡 你可以直接修改目录下的 JSON 文件来更新数据，")
    print("   也可以使用命令行工具管理。运行 'python3 student_engine.py --help' 查看所有命令。")


def schedule_import(filepath: str):
    """从文件导入课表（支持 JSON 和 CSV）"""
    ensure_data_dir()
    path = Path(filepath)

    if not path.exists():
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    if path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif path.suffix == ".csv":
        import csv
        data = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    "day": int(row.get("day", 1)),
                    "time": row.get("time", ""),
                    "course": row.get("course", ""),
                    "teacher": row.get("teacher", ""),
                    "location": row.get("location", ""),
                    "weeks": row.get("weeks", "1-16"),
                })
    else:
        print("❌ 不支持的文件格式，请使用 .json 或 .csv")
        sys.exit(1)

    # 基础校验
    for i, item in enumerate(data):
        if "day" not in item or "course" not in item:
            print(f"❌ 第 {i+1} 条数据缺少 day 或 course 字段")
            sys.exit(1)

    save_json(SCHEDULE_FILE, data)
    print(f"✅ 已导入 {len(data)} 门课程")


def schedule_show(day_filter: Optional[int] = None):
    """展示课表"""
    data = load_json(SCHEDULE_FILE)
    if not data:
        print("📭 课表为空，请先导入课表")
        return

    days = range(1, 8) if day_filter is None else [day_filter]
    time_slots = sorted(set(item["time"] for item in data), key=lambda t: t.split("-")[0])

    print("\n📅 课表")
    print("=" * 80)

    for day in days:
        day_courses = [c for c in data if c["day"] == day]
        if not day_courses:
            continue
        print(f"\n【{WEEKDAYS_CN[day-1]}】")
        day_courses.sort(key=lambda c: c["time"].split("-")[0])
        for c in day_courses:
            print(f"  {c['time']} │ {c['course']} │ {c['teacher']} │ {c['location']} │ 第{c['weeks']}周")

    print("\n" + "=" * 80)


def schedule_today():
    """展示今日课程"""
    today = date.today()
    day_of_week = today.weekday()  # 0=周一

    data = load_json(SCHEDULE_FILE)
    if not data:
        print("📭 课表为空")
        return

    today_courses = [c for c in data if c["day"] == day_of_week + 1]

    print(f"\n📅 {today.isoformat()} {WEEKDAYS_CN[day_of_week]}")
    print("=" * 60)

    if not today_courses:
        print("🎉 今天没有课！")
        return

    today_courses.sort(key=lambda c: c["time"].split("-")[0])
    for c in today_courses:
        print(f"  {c['time']} │ {c['course']} │ {c['teacher']} │ {c['location']}")

    print("=" * 60)


# ── 作业模块 ──────────────────────────────────────────────

def homework_add():
    """交互式添加作业"""
    ensure_data_dir()
    data = load_json(HOMEWORK_FILE)

    print("\n📝 添加作业")
    course = input("课程名称: ").strip()
    title = input("作业标题: ").strip()
    deadline_str = input("截止日期 (YYYY-MM-DD): ").strip()
    note = input("备注 (可选): ").strip()

    if not course or not title or not deadline_str:
        print("❌ 课程、标题、截止日期为必填")
        return

    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except ValueError:
        print("❌ 日期格式错误，请使用 YYYY-MM-DD")
        return

    new_id = max([h.get("id", 0) for h in data], default=0) + 1
    data.append({
        "id": new_id,
        "course": course,
        "title": title,
        "deadline": deadline.isoformat(),
        "done": False,
        "note": note,
    })

    save_json(HOMEWORK_FILE, data)
    print(f"✅ 已添加作业 (ID: {new_id})")


def homework_list(show_all: bool = False):
    """列出作业"""
    data = load_json(HOMEWORK_FILE)
    if not data:
        print("📭 暂无作业")
        return

    today = date.today()
    pending = [h for h in data if not h["done"]]
    done = [h for h in data if h["done"]]

    pending.sort(key=lambda h: h["deadline"])

    print("\n📝 作业列表")
    print("=" * 70)

    if pending:
        print("\n⏳ 待完成:")
        for h in pending:
            dl = datetime.strptime(h["deadline"], "%Y-%m-%d").date()
            days_left = (dl - today).days
            urgency = "🔴" if days_left <= 1 else ("🟡" if days_left <= 3 else "🟢")
            print(f"  [{h['id']}] {urgency} {h['course']} - {h['title']}")
            print(f"      截止: {h['deadline']} (剩 {days_left} 天) | {h['note'] or '无备注'}")

    if show_all and done:
        print("\n✅ 已完成:")
        for h in done[-5:]:  # 只显示最近 5 个
            print(f"  [{h['id']}] {h['course']} - {h['title']}")

    print("\n" + "=" * 70)


def homework_done(hw_id: int):
    """标记作业完成"""
    data = load_json(HOMEWORK_FILE)
    for h in data:
        if h["id"] == hw_id:
            h["done"] = True
            save_json(HOMEWORK_FILE, data)
            print(f"✅ 作业 [{hw_id}] {h['course']} - {h['title']} 已完成！")
            return
    print(f"❌ 未找到 ID 为 {hw_id} 的作业")


def homework_delete(hw_id: int):
    """删除作业"""
    data = load_json(HOMEWORK_FILE)
    data = [h for h in data if h["id"] != hw_id]
    save_json(HOMEWORK_FILE, data)
    print(f"🗑️ 已删除作业 (ID: {hw_id})")


# ── 考试模块 ──────────────────────────────────────────────

def exam_add():
    """交互式添加考试"""
    ensure_data_dir()
    data = load_json(EXAM_FILE)

    print("\n📋 添加考试")
    course = input("课程名称: ").strip()
    exam_type = input("考试类型 (期中/期末/其他): ").strip()
    exam_date_str = input("考试日期 (YYYY-MM-DD): ").strip()
    location = input("考试地点 (可选): ").strip()
    note = input("备注 (可选): ").strip()

    if not course or not exam_date_str:
        print("❌ 课程和日期为必填")
        return

    try:
        exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("❌ 日期格式错误，请使用 YYYY-MM-DD")
        return

    new_id = max([e.get("id", 0) for e in data], default=0) + 1
    data.append({
        "id": new_id,
        "course": course,
        "type": exam_type or "考试",
        "date": exam_date.isoformat(),
        "location": location,
        "note": note,
    })

    save_json(EXAM_FILE, data)
    print(f"✅ 已添加考试 (ID: {new_id})")


def exam_list():
    """列出所有考试"""
    data = load_json(EXAM_FILE)
    if not data:
        print("📭 暂无考试")
        return

    today = date.today()
    data.sort(key=lambda e: e["date"])

    print("\n📋 考试列表")
    print("=" * 70)

    for e in data:
        ed = datetime.strptime(e["date"], "%Y-%m-%d").date()
        days_left = (ed - today).days
        status = "已结束" if days_left < 0 else f"剩 {days_left} 天"
        bar = "🔴" if days_left <= 3 else ("🟡" if days_left <= 14 else "🟢")
        if days_left < 0:
            bar = "⚫"

        print(f"  [{e['id']}] {bar} {e['course']} - {e['type']}")
        print(f"      日期: {e['date']} | {status} | 地点: {e['location'] or '待定'} | {e['note'] or ''}")

    print("\n" + "=" * 70)


def exam_countdown():
    """考试倒计时"""
    data = load_json(EXAM_FILE)
    if not data:
        print("📭 暂无考试")
        return

    today = date.today()
    future = [(e, datetime.strptime(e["date"], "%Y-%m-%d").date()) for e in data]
    future = [(e, d) for e, d in future if d >= today]
    future.sort(key=lambda x: x[1])

    print("\n⏰ 考试倒计时")
    print("=" * 60)

    if not future:
        print("🎉 所有考试已结束！")
        return

    for e, ed in future:
        days_left = (ed - today).days
        bar = "▓" * min(days_left, 30) + "░" * max(30 - days_left, 0)
        print(f"\n  📚 {e['course']} - {e['type']}")
        print(f"  📅 {e['date']} │ 倒计时: {days_left} 天")
        print(f"  [{bar}]")

    print("\n" + "=" * 60)


def exam_delete(exam_id: int):
    """删除考试"""
    data = load_json(EXAM_FILE)
    data = [e for e in data if e["id"] != exam_id]
    save_json(EXAM_FILE, data)
    print(f"🗑️ 已删除考试 (ID: {exam_id})")


# ── 提醒模块 ──────────────────────────────────────────────

def remind():
    """今日提醒汇总"""
    today = date.today()
    day_of_week = today.weekday()

    print(f"\n🔔 {today.isoformat()} {WEEKDAYS_CN[day_of_week]} 今日提醒")
    print("=" * 60)

    # 1. 今日课程
    schedule = load_json(SCHEDULE_FILE)
    today_courses = [c for c in schedule if c["day"] == day_of_week + 1]
    print(f"\n📅 今日课程 ({len(today_courses)} 节):")
    if today_courses:
        today_courses.sort(key=lambda c: c["time"].split("-")[0])
        for c in today_courses:
            print(f"  {c['time']} {c['course']} @ {c['location']}")
    else:
        print("  无课 🎉")

    # 2. 即将到期的作业
    homework = load_json(HOMEWORK_FILE)
    pending = [h for h in homework if not h["done"]]
    urgent = [h for h in pending if (datetime.strptime(h["deadline"], "%Y-%m-%d").date() - today).days <= 3]
    print(f"\n📝 即将到期作业 ({len(urgent)} 项):")
    if urgent:
        for h in urgent:
            dl = datetime.strptime(h["deadline"], "%Y-%m-%d").date()
            days_left = (dl - today).days
            print(f"  🔴 {h['course']}: {h['title']} (剩 {days_left} 天)")
    else:
        print("  无紧急作业 ✅")

    # 3. 临近考试
    exams = load_json(EXAM_FILE)
    near_exams = []
    for e in exams:
        ed = datetime.strptime(e["date"], "%Y-%m-%d").date()
        days_left = (ed - today).days
        if 0 <= days_left <= 14:
            near_exams.append((e, days_left))
    near_exams.sort(key=lambda x: x[1])

    print(f"\n⏰ 临近考试 ({len(near_exams)} 场):")
    if near_exams:
        for e, days in near_exams:
            print(f"  {'🔴' if days <= 3 else '🟡'} {e['course']} - {e['type']}: {e['date']} (剩 {days} 天)")
    else:
        print("  14 天内无考试 ✅")

    print("\n" + "=" * 60)


# ── CLI 入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🎓 大学生助手 v1.0 - 课表、作业、考试、提醒",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python3 student_engine.py init                    # 初始化（含示例数据）
  python3 student_engine.py schedule import 课表.json  # 导入课表
  python3 student_engine.py schedule show           # 查看完整课表
  python3 student_engine.py schedule today          # 今日课程
  python3 student_engine.py homework add            # 添加作业
  python3 student_engine.py homework list           # 查看待完成作业
  python3 student_engine.py homework list --all     # 查看全部作业
  python3 student_engine.py homework done 1         # 标记作业1完成
  python3 student_engine.py homework delete 1       # 删除作业1
  python3 student_engine.py exam add                # 添加考试
  python3 student_engine.py exam list               # 查看考试列表
  python3 student_engine.py exam countdown          # 考试倒计时
  python3 student_engine.py exam delete 1           # 删除考试1
  python3 student_engine.py remind                  # 今日提醒汇总
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # init
    subparsers.add_parser("init", help="初始化数据目录和示例数据")

    # schedule
    sched = subparsers.add_parser("schedule", help="课表管理")
    sched_sub = sched.add_subparsers(dest="subcommand")
    sched_import = sched_sub.add_parser("import", help="导入课表")
    sched_import.add_argument("file", help="课表文件路径 (.json 或 .csv)")
    sched_sub.add_parser("show", help="查看完整课表")
    sched_sub.add_parser("today", help="查看今日课程")

    # homework
    hw = subparsers.add_parser("homework", help="作业管理")
    hw_sub = hw.add_subparsers(dest="subcommand")
    hw_sub.add_parser("add", help="添加作业")
    hw_list = hw_sub.add_parser("list", help="查看作业")
    hw_list.add_argument("--all", action="store_true", help="显示所有（含已完成）")
    hw_done = hw_sub.add_parser("done", help="标记完成")
    hw_done.add_argument("id", type=int, help="作业 ID")
    hw_del = hw_sub.add_parser("delete", help="删除作业")
    hw_del.add_argument("id", type=int, help="作业 ID")

    # exam
    ex = subparsers.add_parser("exam", help="考试管理")
    ex_sub = ex.add_subparsers(dest="subcommand")
    ex_sub.add_parser("add", help="添加考试")
    ex_sub.add_parser("list", help="查看考试列表")
    ex_sub.add_parser("countdown", help="考试倒计时")
    ex_del = ex_sub.add_parser("delete", help="删除考试")
    ex_del.add_argument("id", type=int, help="考试 ID")

    # remind
    subparsers.add_parser("remind", help="今日提醒汇总")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "init":
        init_cmd()

    elif args.command == "schedule":
        if args.subcommand == "import":
            schedule_import(args.file)
        elif args.subcommand == "show":
            schedule_show()
        elif args.subcommand == "today":
            schedule_today()
        else:
            sched.print_help()

    elif args.command == "homework":
        if args.subcommand == "add":
            homework_add()
        elif args.subcommand == "list":
            homework_list(show_all=args.all)
        elif args.subcommand == "done":
            homework_done(args.id)
        elif args.subcommand == "delete":
            homework_delete(args.id)
        else:
            hw.print_help()

    elif args.command == "exam":
        if args.subcommand == "add":
            exam_add()
        elif args.subcommand == "list":
            exam_list()
        elif args.subcommand == "countdown":
            exam_countdown()
        elif args.subcommand == "delete":
            exam_delete(args.id)
        else:
            ex.print_help()

    elif args.command == "remind":
        remind()


if __name__ == "__main__":
    main()
