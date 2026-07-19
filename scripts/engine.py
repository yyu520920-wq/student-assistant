#!/usr/bin/env python3
"""
大学生助手 v1.1 - 核心引擎
功能：多学期管理、课表导入、作业管理、考试倒计时、每日提醒、iCal导出

用法：
  python3 engine.py init
  python3 engine.py semester new <名称>
  python3 engine.py semester switch <名称>
  python3 engine.py semester list
  python3 engine.py schedule import <文件>
  python3 engine.py schedule show
  python3 engine.py schedule today
  python3 engine.py homework add
  python3 engine.py homework list
  python3 engine.py homework done <id>
  python3 engine.py exam add
  python3 engine.py exam list
  python3 engine.py exam countdown
  python3 engine.py remind
  python3 engine.py export ical --type all --output 课表.ics
"""

import json
import os
import sys
import shutil
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ── 数据目录 ──────────────────────────────────────────────
BASE_DIR = Path.home() / ".student-assistant"
CURRENT_FILE = BASE_DIR / "current.json"
WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def get_current_semester() -> str:
    """获取当前学期名称"""
    if CURRENT_FILE.exists():
        try:
            with open(CURRENT_FILE) as f:
                return json.load(f).get("semester", "默认学期")
        except:
            pass
    return "默认学期"


def set_current_semester(name: str):
    """设置当前学期"""
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CURRENT_FILE, "w") as f:
        json.dump({"semester": name}, f, ensure_ascii=False)


def get_semester_dir(name: str = None) -> Path:
    """获取学期数据目录"""
    if name is None:
        name = get_current_semester()
    return BASE_DIR / "semesters" / name


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path) -> List[Dict]:
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_json(filepath: Path, data):
    ensure_dir(filepath.parent)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _schedule_file(sem: str = None) -> Path:
    return get_semester_dir(sem) / "schedule.json"


def _homework_file(sem: str = None) -> Path:
    return get_semester_dir(sem) / "homework.json"


def _exam_file(sem: str = None) -> Path:
    return get_semester_dir(sem) / "exam.json"


def _migrate_old_data():
    """迁移 v1 旧数据到默认学期"""
    old_files = {
        BASE_DIR / "schedule.json": _schedule_file("默认学期"),
        BASE_DIR / "homework.json": _homework_file("默认学期"),
        BASE_DIR / "exam.json": _exam_file("默认学期"),
    }
    for old, new in old_files.items():
        if old.exists() and not new.exists():
            ensure_dir(new.parent)
            shutil.move(str(old), str(new))


# ── 学期管理 ──────────────────────────────────────────────

def semester_new(name: str):
    """创建新学期"""
    sd = get_semester_dir(name)
    if sd.exists():
        print(f"⚠️ 学期 '{name}' 已存在")
        return
    ensure_dir(sd)
    save_json(_schedule_file(name), [])
    save_json(_homework_file(name), [])
    save_json(_exam_file(name), [])
    set_current_semester(name)
    print(f"✅ 已创建学期 '{name}' 并切换为当前学期")


def semester_switch(name: str):
    """切换学期"""
    sd = get_semester_dir(name)
    if not sd.exists():
        print(f"❌ 学期 '{name}' 不存在，请先用 'semester new {name}' 创建")
        return
    set_current_semester(name)
    print(f"✅ 已切换到学期 '{name}'")


def semester_list():
    """列出所有学期"""
    sem_dir = BASE_DIR / "semesters"
    if not sem_dir.exists():
        print("📭 暂无学期，请运行 init")
        return
    current = get_current_semester()
    print("\n📚 学期列表")
    print("=" * 40)
    for d in sorted(sem_dir.iterdir()):
        if d.is_dir():
            marker = " ← 当前" if d.name == current else ""
            count = len(load_json(d / "schedule.json"))
            print(f"  {d.name}{marker} ({count} 门课)")
    print("=" * 40)


# ── 初始化 ──────────────────────────────────────────────

def init_cmd():
    _migrate_old_data()
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    ensure_dir(sd)

    sf = _schedule_file(sem)
    if not sf.exists():
        save_json(sf, [
            {"day": 1, "time": "08:00-09:40", "course": "高等数学", "teacher": "张老师", "location": "教1-301", "weeks": "1-16"},
            {"day": 1, "time": "10:00-11:40", "course": "大学英语", "teacher": "李老师", "location": "教2-205", "weeks": "1-16"},
            {"day": 2, "time": "08:00-09:40", "course": "线性代数", "teacher": "王老师", "location": "教1-201", "weeks": "1-16"},
            {"day": 2, "time": "14:00-15:40", "course": "程序设计基础", "teacher": "赵老师", "location": "机房3", "weeks": "1-16"},
            {"day": 3, "time": "10:00-11:40", "course": "大学物理", "teacher": "刘老师", "location": "教3-102", "weeks": "1-16"},
            {"day": 3, "time": "14:00-15:40", "course": "体育", "teacher": "陈老师", "location": "操场", "weeks": "1-16"},
            {"day": 4, "time": "08:00-09:40", "course": "高等数学", "teacher": "张老师", "location": "教1-301", "weeks": "1-16"},
            {"day": 4, "time": "14:00-15:40", "course": "思想政治", "teacher": "周老师", "location": "教4-101", "weeks": "1-16"},
            {"day": 5, "time": "10:00-11:40", "course": "大学英语", "teacher": "李老师", "location": "教2-205", "weeks": "1-16"},
        ])
        print("✅ 已创建示例课表（9门课程）")

    hf = _homework_file(sem)
    if not hf.exists():
        today = date.today()
        save_json(hf, [
            {"id": 1, "course": "高等数学", "title": "习题3.2 第1-10题", "deadline": (today + timedelta(days=3)).isoformat(), "done": False, "note": "交纸质版"},
            {"id": 2, "course": "大学英语", "title": "Unit 5 课后翻译", "deadline": (today + timedelta(days=5)).isoformat(), "done": False, "note": "提交到学习通"},
            {"id": 3, "course": "程序设计基础", "title": "实验报告：排序算法", "deadline": (today + timedelta(days=7)).isoformat(), "done": False, "note": "含代码和运行截图"},
        ])
        print("✅ 已创建示例作业（3项）")

    ef = _exam_file(sem)
    if not ef.exists():
        today = date.today()
        save_json(ef, [
            {"id": 1, "course": "高等数学", "type": "期中考试", "date": (today + timedelta(days=14)).isoformat(), "location": "教1-301", "note": "第1-4章"},
            {"id": 2, "course": "大学英语", "type": "期末考试", "date": (today + timedelta(days=45)).isoformat(), "location": "待定", "note": "含听力"},
        ])
        print("✅ 已创建示例考试（2场）")

    print(f"\n📁 数据目录: {sd}")
    print(f"📚 当前学期: {sem}")
    print("💡 运行 'python3 scripts/engine.py --help' 查看所有命令。")


# ── 课表 ──────────────────────────────────────────────

def schedule_import(filepath: str):
    sem = get_current_semester()
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
            for row in csv.DictReader(f):
                data.append({
                    "day": int(row.get("day", 1)), "time": row.get("time", ""),
                    "course": row.get("course", ""), "teacher": row.get("teacher", ""),
                    "location": row.get("location", ""), "weeks": row.get("weeks", "1-16"),
                })
    else:
        print("❌ 不支持的文件格式，请使用 .json 或 .csv")
        sys.exit(1)

    for i, item in enumerate(data):
        if "day" not in item or "course" not in item:
            print(f"❌ 第 {i+1} 条数据缺少 day 或 course 字段")
            sys.exit(1)

    save_json(_schedule_file(sem), data)
    print(f"✅ 已导入 {len(data)} 门课程到学期 '{sem}'")


def schedule_show(sem_name: str = None):
    sem = sem_name or get_current_semester()
    data = load_json(_schedule_file(sem))
    if not data:
        print("📭 课表为空")
        return

    print(f"\n📅 课表 [{sem}]")
    print("=" * 80)
    for day in range(1, 8):
        courses = sorted([c for c in data if c["day"] == day], key=lambda c: c["time"])
        if not courses:
            continue
        print(f"\n【{WEEKDAYS_CN[day-1]}】")
        for c in courses:
            print(f"  {c['time']} │ {c['course']} │ {c.get('teacher','')} │ {c.get('location','')} │ 第{c.get('weeks','1-16')}周")
    print("\n" + "=" * 80)


def schedule_today():
    sem = get_current_semester()
    data = load_json(_schedule_file(sem))
    today = date.today()
    dow = today.weekday()
    courses = sorted([c for c in data if c["day"] == dow + 1], key=lambda c: c["time"])

    print(f"\n📅 {today.isoformat()} {WEEKDAYS_CN[dow]} [{sem}]")
    print("=" * 60)
    if not courses:
        print("🎉 今天没有课！")
    else:
        for c in courses:
            print(f"  {c['time']} │ {c['course']} │ {c.get('teacher','')} │ {c.get('location','')}")
    print("=" * 60)


# ── 作业 ──────────────────────────────────────────────

def homework_add():
    sem = get_current_semester()
    data = load_json(_homework_file(sem))

    print("\n📝 添加作业")
    course = input("课程名称: ").strip()
    title = input("作业标题: ").strip()
    deadline_str = input("截止日期 (YYYY-MM-DD): ").strip()
    note = input("备注 (可选): ").strip()

    if not course or not title or not deadline_str:
        print("❌ 课程、标题、截止日期为必填"); return
    try:
        dl = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except ValueError:
        print("❌ 日期格式错误"); return

    new_id = max([h.get("id", 0) for h in data], default=0) + 1
    data.append({"id": new_id, "course": course, "title": title, "deadline": dl.isoformat(), "done": False, "note": note})
    save_json(_homework_file(sem), data)
    print(f"✅ 已添加作业 (ID: {new_id})")


def homework_list(show_all=False):
    sem = get_current_semester()
    data = load_json(_homework_file(sem))
    if not data:
        print("📭 暂无作业"); return

    today = date.today()
    pending = sorted([h for h in data if not h["done"]], key=lambda h: h["deadline"])
    done = [h for h in data if h["done"]]

    print(f"\n📝 作业列表 [{sem}]")
    print("=" * 70)
    if pending:
        print("\n⏳ 待完成:")
        for h in pending:
            dl = datetime.strptime(h["deadline"], "%Y-%m-%d").date()
            days = (dl - today).days
            u = "🔴" if days <= 1 else ("🟡" if days <= 3 else "🟢")
            print(f"  [{h['id']}] {u} {h['course']} - {h['title']}")
            print(f"      截止: {h['deadline']} (剩 {days} 天) | {h.get('note','') or '无备注'}")
    if show_all and done:
        print("\n✅ 已完成:")
        for h in done[-5:]:
            print(f"  [{h['id']}] {h['course']} - {h['title']}")
    print("\n" + "=" * 70)


def homework_done(hw_id: int):
    sem = get_current_semester()
    data = load_json(_homework_file(sem))
    for h in data:
        if h["id"] == hw_id:
            h["done"] = True
            save_json(_homework_file(sem), data)
            print(f"✅ 作业 [{hw_id}] {h['course']} - {h['title']} 已完成！")
            return
    print(f"❌ 未找到 ID 为 {hw_id} 的作业")


def homework_delete(hw_id: int):
    sem = get_current_semester()
    data = load_json(_homework_file(sem))
    data = [h for h in data if h["id"] != hw_id]
    save_json(_homework_file(sem), data)
    print(f"🗑️ 已删除作业 (ID: {hw_id})")


# ── 考试 ──────────────────────────────────────────────

def exam_add():
    sem = get_current_semester()
    data = load_json(_exam_file(sem))

    print("\n📋 添加考试")
    course = input("课程名称: ").strip()
    exam_type = input("考试类型 (期中/期末/其他): ").strip()
    exam_date_str = input("考试日期 (YYYY-MM-DD): ").strip()
    location = input("考试地点 (可选): ").strip()
    note = input("备注 (可选): ").strip()

    if not course or not exam_date_str:
        print("❌ 课程和日期为必填"); return
    try:
        ed = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("❌ 日期格式错误"); return

    new_id = max([e.get("id", 0) for e in data], default=0) + 1
    data.append({"id": new_id, "course": course, "type": exam_type or "考试", "date": ed.isoformat(), "location": location, "note": note})
    save_json(_exam_file(sem), data)
    print(f"✅ 已添加考试 (ID: {new_id})")


def exam_list():
    sem = get_current_semester()
    data = sorted(load_json(_exam_file(sem)), key=lambda e: e["date"])
    if not data:
        print("📭 暂无考试"); return

    today = date.today()
    print(f"\n📋 考试列表 [{sem}]")
    print("=" * 70)
    for e in data:
        ed = datetime.strptime(e["date"], "%Y-%m-%d").date()
        days = (ed - today).days
        bar = "⚫" if days < 0 else ("🔴" if days <= 3 else ("🟡" if days <= 14 else "🟢"))
        status = "已结束" if days < 0 else f"剩 {days} 天"
        print(f"  [{e['id']}] {bar} {e['course']} - {e['type']}")
        print(f"      日期: {e['date']} | {status} | 地点: {e.get('location','') or '待定'} | {e.get('note','') or ''}")
    print("\n" + "=" * 70)


def exam_countdown():
    sem = get_current_semester()
    data = load_json(_exam_file(sem))
    if not data:
        print("📭 暂无考试"); return

    today = date.today()
    future = sorted([(e, datetime.strptime(e["date"], "%Y-%m-%d").date()) for e in data if datetime.strptime(e["date"], "%Y-%m-%d").date() >= today], key=lambda x: x[1])

    print(f"\n⏰ 考试倒计时 [{sem}]")
    print("=" * 60)
    if not future:
        print("🎉 所有考试已结束！"); return
    for e, ed in future:
        days = (ed - today).days
        bar = "▓" * min(days, 30) + "░" * max(30 - days, 0)
        print(f"\n  📚 {e['course']} - {e['type']}")
        print(f"  📅 {e['date']} │ 倒计时: {days} 天")
        print(f"  [{bar}]")
    print("\n" + "=" * 60)


def exam_delete(exam_id: int):
    sem = get_current_semester()
    data = load_json(_exam_file(sem))
    data = [e for e in data if e["id"] != exam_id]
    save_json(_exam_file(sem), data)
    print(f"🗑️ 已删除考试 (ID: {exam_id})")


# ── 提醒 ──────────────────────────────────────────────

def remind():
    sem = get_current_semester()
    today = date.today()
    dow = today.weekday()

    print(f"\n🔔 {today.isoformat()} {WEEKDAYS_CN[dow]} 今日提醒 [{sem}]")
    print("=" * 60)

    # 今日课程
    schedule = load_json(_schedule_file(sem))
    today_courses = sorted([c for c in schedule if c["day"] == dow + 1], key=lambda c: c["time"])
    print(f"\n📅 今日课程 ({len(today_courses)} 节):")
    if today_courses:
        for c in today_courses:
            print(f"  {c['time']} {c['course']} @ {c.get('location','')}")
    else:
        print("  无课 🎉")

    # 即将到期作业
    homework = load_json(_homework_file(sem))
    pending = [h for h in homework if not h["done"]]
    urgent = [h for h in pending if (datetime.strptime(h["deadline"], "%Y-%m-%d").date() - today).days <= 3]
    print(f"\n📝 即将到期作业 ({len(urgent)} 项):")
    if urgent:
        for h in urgent:
            days = (datetime.strptime(h["deadline"], "%Y-%m-%d").date() - today).days
            print(f"  🔴 {h['course']}: {h['title']} (剩 {days} 天)")
    else:
        print("  无紧急作业 ✅")

    # 临近考试
    exams = load_json(_exam_file(sem))
    near = sorted([(e, (datetime.strptime(e["date"], "%Y-%m-%d").date() - today).days) for e in exams if 0 <= (datetime.strptime(e["date"], "%Y-%m-%d").date() - today).days <= 14], key=lambda x: x[1])
    print(f"\n⏰ 临近考试 ({len(near)} 场):")
    if near:
        for e, days in near:
            print(f"  {'🔴' if days <= 3 else '🟡'} {e['course']} - {e['type']}: {e['date']} (剩 {days} 天)")
    else:
        print("  14 天内无考试 ✅")
    print("\n" + "=" * 60)


def get_remind_data() -> Dict:
    """返回提醒数据（供 notifier 和 API 使用）"""
    sem = get_current_semester()
    today = date.today()
    dow = today.weekday()

    schedule = load_json(_schedule_file(sem))
    today_courses = sorted([c for c in schedule if c["day"] == dow + 1], key=lambda c: c["time"])

    homework = load_json(_homework_file(sem))
    pending = [h for h in homework if not h["done"]]
    urgent = [h for h in pending if (datetime.strptime(h["deadline"], "%Y-%m-%d").date() - today).days <= 3]

    exams = load_json(_exam_file(sem))
    near = [{"exam": e, "days": (datetime.strptime(e["date"], "%Y-%m-%d").date() - today).days}
            for e in exams if 0 <= (datetime.strptime(e["date"], "%Y-%m-%d").date() - today).days <= 14]

    return {
        "date": today.isoformat(), "weekday": WEEKDAYS_CN[dow], "semester": sem,
        "courses": today_courses,
        "urgent_homework": [{"id": h["id"], "course": h["course"], "title": h["title"],
                             "deadline": h["deadline"], "days_left": (datetime.strptime(h["deadline"], "%Y-%m-%d").date() - today).days} for h in urgent],
        "near_exams": near,
        "all_pending_homework": [{"id": h["id"], "course": h["course"], "title": h["title"],
                                   "deadline": h["deadline"], "days_left": (datetime.strptime(h["deadline"], "%Y-%m-%d").date() - today).days, "done": h["done"]} for h in homework],
        "all_exams": sorted([{"id": e["id"], "course": e["course"], "type": e["type"], "date": e["date"],
                               "days_left": (datetime.strptime(e["date"], "%Y-%m-%d").date() - today).days,
                               "location": e.get("location", ""), "note": e.get("note", "")} for e in exams], key=lambda x: x["date"]),
    }


# ── 期末复习系统 ──────────────────────────────────────

def _review_file(sem: str = None) -> Path:
    return get_semester_dir(sem) / "review.json"


def _practice_file(sem: str = None) -> Path:
    return get_semester_dir(sem) / "practice.json"


def _wrong_questions_file(sem: str = None) -> Path:
    return get_semester_dir(sem) / "wrong_questions.json"


def review_knowledge_add():
    """交互式添加知识点"""
    sem = get_current_semester()
    print("📝 添加知识点")
    course = input("  课程: ").strip()
    if not course:
        print("  ❌ 课程不能为空")
        return
    topic = input("  知识点: ").strip()
    if not topic:
        print("  ❌ 知识点不能为空")
        return
    mastery_str = input("  掌握度 (0-100, 默认 0): ").strip()
    try:
        mastery = max(0, min(100, int(mastery_str))) if mastery_str else 0
    except:
        mastery = 0
    notes = input("  备注 (可选): ").strip()

    items = load_json(_review_file(sem))
    new_id = max([i["id"] for i in items], default=0) + 1
    items.append({"id": new_id, "course": course, "topic": topic, "mastery": mastery, "notes": notes})
    save_json(_review_file(sem), items)
    print(f"  ✅ 知识点 [{new_id}] {topic} 已添加（掌握度: {mastery}）")


def review_knowledge_list():
    """列出知识点（按掌握度排序）"""
    sem = get_current_semester()
    items = load_json(_review_file(sem))
    if not items:
        print("📖 暂无知识点")
        return
    items.sort(key=lambda x: x["mastery"])
    print(f"📖 知识点清单（{sem}）共 {len(items)} 条\n")
    for i in items:
        bar = "█" * (i["mastery"] // 10) + "░" * (10 - i["mastery"] // 10)
        note = f" | 📝 {i['notes']}" if i["notes"] else ""
        print(f"  [{i['id']:>3}] {i['course']} - {i['topic']}  [{bar}] {i['mastery']}%{note}")


def review_knowledge_update(id: int, mastery: int):
    """更新知识点掌握度"""
    sem = get_current_semester()
    items = load_json(_review_file(sem))
    for i in items:
        if i["id"] == id:
            old = i["mastery"]
            i["mastery"] = max(0, min(100, mastery))
            save_json(_review_file(sem), items)
            print(f"  ✅ [{id}] {i['topic']} 掌握度: {old}% → {i['mastery']}%")
            return
    print(f"  ❌ 未找到知识点 [{id}]")


def review_practice_add():
    """添加刷题记录"""
    sem = get_current_semester()
    print("✏️  添加刷题记录")
    date_str = input("  日期 (YYYY-MM-DD, 默认今天): ").strip()
    if not date_str:
        date_str = date.today().isoformat()
    course = input("  课程: ").strip()
    if not course:
        print("  ❌ 课程不能为空")
        return
    try:
        count = int(input("  总题数: ").strip())
        correct = int(input("  正确数: ").strip())
        duration = int(input("  时长(分钟): ").strip())
    except ValueError:
        print("  ❌ 请输入有效数字")
        return

    items = load_json(_practice_file(sem))
    new_id = max([i["id"] for i in items], default=0) + 1
    items.append({"id": new_id, "date": date_str, "course": course, "count": count, "correct": correct, "duration_min": duration})
    save_json(_practice_file(sem), items)
    rate = f"{correct / count * 100:.0f}%" if count > 0 else "N/A"
    print(f"  ✅ 刷题记录 [{new_id}] {course} {count}题 正确率 {rate}")


def review_practice_list():
    """列出刷题记录"""
    sem = get_current_semester()
    items = load_json(_practice_file(sem))
    if not items:
        print("✏️  暂无刷题记录")
        return
    items.sort(key=lambda x: x["date"], reverse=True)
    print(f"✏️  刷题记录（{sem}）共 {len(items)} 条\n")
    for i in items:
        rate = f"{i['correct'] / i['count'] * 100:.0f}%" if i["count"] > 0 else "N/A"
        print(f"  [{i['id']:>3}] {i['date']} {i['course']} {i['count']}题 正确{i['correct']} ({rate}) ⏱️{i['duration_min']}分钟")


def review_practice_stats():
    """刷题统计"""
    sem = get_current_semester()
    items = load_json(_practice_file(sem))
    if not items:
        print("✏️  暂无刷题数据")
        return
    total_count = sum(i["count"] for i in items)
    total_correct = sum(i["correct"] for i in items)
    total_duration = sum(i["duration_min"] for i in items)
    overall_rate = f"{total_correct / total_count * 100:.1f}%" if total_count > 0 else "N/A"

    print(f"📊 刷题统计（{sem}）\n")
    print(f"  总题数: {total_count}")
    print(f"  总正确: {total_correct}")
    print(f"  总正确率: {overall_rate}")
    print(f"  总时长: {total_duration} 分钟 ({total_duration / 60:.1f} 小时)")
    print(f"  刷题次数: {len(items)}")

    # 按日期统计正确率趋势
    items.sort(key=lambda x: x["date"])
    print(f"\n  📈 正确率趋势:")
    for i in items:
        rate = f"{i['correct'] / i['count'] * 100:.0f}%" if i["count"] > 0 else "N/A"
        bar = "█" * (i["correct"] * 10 // i["count"]) if i["count"] > 0 else ""
        print(f"    {i['date']} {i['course']}: [{bar}] {rate}")


def review_wrong_add():
    """添加错题"""
    sem = get_current_semester()
    print("❌ 添加错题")
    course = input("  课程: ").strip()
    if not course:
        print("  ❌ 课程不能为空")
        return
    topic = input("  知识点: ").strip()
    if not topic:
        print("  ❌ 知识点不能为空")
        return
    question = input("  题目描述: ").strip()
    answer = input("  正确答案: ").strip()
    my_answer = input("  你的错误答案: ").strip()
    reason = input("  错误原因: ").strip()
    date_str = input("  日期 (YYYY-MM-DD, 默认今天): ").strip()
    if not date_str:
        date_str = date.today().isoformat()

    items = load_json(_wrong_questions_file(sem))
    new_id = max([i["id"] for i in items], default=0) + 1
    items.append({
        "id": new_id, "course": course, "topic": topic, "question": question,
        "answer": answer, "my_answer": my_answer, "reason": reason,
        "reviewed": False, "date": date_str
    })
    save_json(_wrong_questions_file(sem), items)
    print(f"  ✅ 错题 [{new_id}] 已添加")


def review_wrong_list():
    """列出错题"""
    sem = get_current_semester()
    items = load_json(_wrong_questions_file(sem))
    if not items:
        print("❌ 暂无错题")
        return
    items.sort(key=lambda x: x["date"], reverse=True)
    print(f"❌ 错题本（{sem}）共 {len(items)} 条\n")
    for i in items:
        status = "✅已复习" if i["reviewed"] else "🔴未复习"
        print(f"  [{i['id']:>3}] {status} {i['date']} {i['course']} - {i['topic']}")
        print(f"       题目: {i['question']}")
        print(f"       正确答案: {i['answer']}")
        print(f"       你的答案: {i['my_answer']}")
        print(f"       原因: {i['reason']}")
        print()


def review_wrong_review(id: int):
    """标记错题已复习"""
    sem = get_current_semester()
    items = load_json(_wrong_questions_file(sem))
    for i in items:
        if i["id"] == id:
            i["reviewed"] = True
            save_json(_wrong_questions_file(sem), items)
            print(f"  ✅ 错题 [{id}] {i['topic']} 已标记为已复习")
            return
    print(f"  ❌ 未找到错题 [{id}]")


def review_plan():
    """根据考试日期和知识点自动生成复习计划"""
    sem = get_current_semester()
    today = date.today()
    exams = load_json(_exam_file(sem))
    knowledge = load_json(_review_file(sem))

    if not exams:
        print("📅 暂无考试安排，请先添加考试")
        return
    if not knowledge:
        print("📖 暂无知识点，请先添加知识点")
        return

    # 按考试日期排序
    upcoming = sorted(
        [{"exam": e, "days": (datetime.strptime(e["date"], "%Y-%m-%d").date() - today).days}
         for e in exams if (datetime.strptime(e["date"], "%Y-%m-%d").date() - today).days >= 0],
        key=lambda x: x["days"]
    )

    if not upcoming:
        print("📅 没有即将到来的考试")
        return

    print(f"📋 复习计划（{sem}）\n")
    print(f"  距离最近考试还有 {upcoming[0]['days']} 天\n")

    for idx, item in enumerate(upcoming):
        exam = item["exam"]
        days_left = item["days"]
        print(f"  🎯 考试 [{exam['id']}] {exam['course']} - {exam['type']}")
        print(f"     日期: {exam['date']} | 剩余 {days_left} 天")

        # 找出相关知识点（按课程匹配）
        related = [k for k in knowledge if k["course"] == exam["course"]]
        if related:
            related.sort(key=lambda x: x["mastery"])  # 掌握度低的优先
            print(f"     复习知识点:")
            for k in related:
                priority = "🔴" if k["mastery"] < 40 else "🟡" if k["mastery"] < 70 else "🟢"
                bar = "█" * (k["mastery"] // 10) + "░" * (10 - k["mastery"] // 10)
                print(f"       {priority} [{k['id']:>3}] {k['topic']} [{bar}] {k['mastery']}%")
        else:
            print(f"     ⚠️ 暂无相关知识点，请先添加")
        print()


# ── 每日成长记录 ──────────────────────────────────────

def _daily_file(sem: str = None) -> Path:
    return get_semester_dir(sem) / "daily.json"


def daily_checkin():
    """今日打卡（交互式）"""
    sem = get_current_semester()
    today_str = date.today().isoformat()
    items = load_json(_daily_file(sem))

    # 检查今天是否已打卡
    existing = [i for i in items if i["date"] == today_str]
    if existing:
        print(f"📅 今天 ({today_str}) 已经打卡过了")
        rec = existing[0]
        print(f"  📚 学习: {rec['study_hours']}h | 📖阅读: {'是' if rec['reading'] else '否'} | 🏃运动: {'是' if rec['exercise'] else '否'}")
        print(f"  ⏰早起: {'是' if rec['early_rise'] else '否'} | 😊心情: {rec['mood']}")
        if rec.get("diary"):
            print(f"  📝日记: {rec['diary']}")
        return

    print(f"📅 每日打卡 - {today_str}")
    try:
        study_hours = float(input("  学习时长(小时): ").strip())
    except ValueError:
        print("  ❌ 请输入有效数字")
        return
    reading = input("  是否阅读？(y/n, 默认 n): ").strip().lower() == "y"
    exercise = input("  是否运动？(y/n, 默认 n): ").strip().lower() == "y"
    early_rise = input("  是否早起？(y/n, 默认 n): ").strip().lower() == "y"
    mood = input("  今日心情 (如 😊😢😤😴🤩, 默认 😊): ").strip() or "😊"
    diary = input("  今日小结 (可选): ").strip()

    items.append({
        "date": today_str, "study_hours": study_hours, "reading": reading,
        "exercise": exercise, "early_rise": early_rise, "mood": mood, "diary": diary
    })
    save_json(_daily_file(sem), items)

    habit_count = sum([reading, exercise, early_rise])
    print(f"\n  ✅ 打卡成功！")
    print(f"  📚 学习 {study_hours}h | 好习惯 {habit_count}/3 | 😊 {mood}")


def daily_list(days: int = 7):
    """最近N天记录"""
    sem = get_current_semester()
    items = load_json(_daily_file(sem))
    if not items:
        print("📅 暂无打卡记录")
        return

    items.sort(key=lambda x: x["date"], reverse=True)
    display = items[:days]
    print(f"📅 最近 {len(display)} 天打卡记录（{sem}）\n")
    for i in display:
        habits = []
        if i.get("reading"): habits.append("📖")
        if i.get("exercise"): habits.append("🏃")
        if i.get("early_rise"): habits.append("⏰")
        habit_str = " ".join(habits) if habits else "无"
        print(f"  {i['date']} | 📚{i['study_hours']}h | {habit_str} | {i.get('mood', '😊')}")
        if i.get("diary"):
            print(f"    📝 {i['diary']}")


def daily_stats():
    """统计：连续打卡天数、总学习时长、打卡率"""
    sem = get_current_semester()
    items = load_json(_daily_file(sem))
    if not items:
        print("📊 暂无打卡数据")
        return

    today = date.today()
    items.sort(key=lambda x: x["date"], reverse=True)

    # 连续打卡天数
    streak = 0
    check_date = today
    dates_set = {i["date"] for i in items}
    while check_date.isoformat() in dates_set:
        streak += 1
        check_date -= timedelta(days=1)

    # 总学习时长
    total_hours = sum(i["study_hours"] for i in items)

    # 打卡率（从第一天打卡到今天）
    first_date_str = items[-1]["date"]
    try:
        first_date = datetime.strptime(first_date_str, "%Y-%m-%d").date()
        total_days = (today - first_date).days + 1
        checkin_rate = f"{len(items) / total_days * 100:.1f}%"
    except:
        checkin_rate = "N/A"

    # 好习惯统计
    reading_days = sum(1 for i in items if i.get("reading"))
    exercise_days = sum(1 for i in items if i.get("exercise"))
    early_rise_days = sum(1 for i in items if i.get("early_rise"))

    print(f"📊 打卡统计（{sem}）\n")
    print(f"  🔥 连续打卡: {streak} 天")
    print(f"  📚 总学习时长: {total_hours:.1f} 小时")
    print(f"  📅 打卡率: {checkin_rate} ({len(items)}/{total_days if 'total_days' in dir() else '?'} 天)")
    print(f"  📖 阅读天数: {reading_days}")
    print(f"  🏃 运动天数: {exercise_days}")
    print(f"  ⏰ 早起天数: {early_rise_days}")
    print(f"  📝 日记篇数: {sum(1 for i in items if i.get('diary'))}")


# ── 目标管理 ──────────────────────────────────────────

def _goals_file(sem: str = None) -> Path:
    return get_semester_dir(sem) / "goals.json"


def goal_add():
    """添加目标"""
    sem = get_current_semester()
    print("🎯 添加目标")
    title = input("  目标标题: ").strip()
    if not title:
        print("  ❌ 标题不能为空")
        return
    goal_type = input("  类型 (long/short, 默认 long): ").strip() or "long"
    try:
        progress = int(input("  当前进度 (默认 0): ").strip() or "0")
        target = int(input("  目标值 (默认 100): ").strip() or "100")
    except ValueError:
        print("  ❌ 请输入有效数字")
        return
    deadline = input("  截止日期 (YYYY-MM-DD, 可选): ").strip() or ""
    created = date.today().isoformat()

    items = load_json(_goals_file(sem))
    new_id = max([i["id"] for i in items], default=0) + 1
    items.append({
        "id": new_id, "title": title, "type": goal_type, "progress": progress,
        "target": target, "deadline": deadline, "milestones": [], "created": created
    })
    save_json(_goals_file(sem), items)
    print(f"  ✅ 目标 [{new_id}] {title} 已添加")


def goal_list():
    """列出所有目标"""
    sem = get_current_semester()
    items = load_json(_goals_file(sem))
    if not items:
        print("🎯 暂无目标")
        return

    print(f"🎯 目标清单（{sem}）共 {len(items)} 个\n")
    for g in items:
        pct = g["progress"] / g["target"] * 100 if g["target"] > 0 else 0
        bar = "█" * (int(pct) // 10) + "░" * (10 - int(pct) // 10)
        deadline_str = f" | 📅 {g['deadline']}" if g.get("deadline") else ""
        type_label = "🏁长期" if g["type"] == "long" else "⚡短期"
        print(f"  [{g['id']:>3}] {type_label} {g['title']} [{bar}] {pct:.0f}% ({g['progress']}/{g['target']}){deadline_str}")
        if g.get("milestones"):
            for idx, m in enumerate(g["milestones"]):
                status = "✅" if m["done"] else "⬜"
                print(f"       里程碑 {idx}: {status} {m['name']}")
        print()


def goal_update(id: int, progress: int):
    """更新目标进度"""
    sem = get_current_semester()
    items = load_json(_goals_file(sem))
    for g in items:
        if g["id"] == id:
            old = g["progress"]
            g["progress"] = progress
            save_json(_goals_file(sem), items)
            pct = progress / g["target"] * 100 if g["target"] > 0 else 0
            print(f"  ✅ [{id}] {g['title']} 进度: {old}/{g['target']} → {progress}/{g['target']} ({pct:.0f}%)")
            return
    print(f"  ❌ 未找到目标 [{id}]")


def goal_milestone(id: int, name: str):
    """添加里程碑"""
    sem = get_current_semester()
    items = load_json(_goals_file(sem))
    for g in items:
        if g["id"] == id:
            g.setdefault("milestones", []).append({"name": name, "done": False})
            save_json(_goals_file(sem), items)
            print(f"  ✅ 目标 [{id}] {g['title']} 添加里程碑: {name}")
            return
    print(f"  ❌ 未找到目标 [{id}]")


def goal_milestone_done(id: int, index: int):
    """标记里程碑完成"""
    sem = get_current_semester()
    items = load_json(_goals_file(sem))
    for g in items:
        if g["id"] == id:
            if 0 <= index < len(g.get("milestones", [])):
                g["milestones"][index]["done"] = True
                save_json(_goals_file(sem), items)
                print(f"  ✅ 目标 [{id}] {g['title']} 里程碑 [{index}] {g['milestones'][index]['name']} 已完成")
            else:
                print(f"  ❌ 里程碑索引 {index} 无效（共 {len(g.get('milestones', []))} 个里程碑）")
            return
    print(f"  ❌ 未找到目标 [{id}]")


# ── 仪表盘数据 ────────────────────────────────────────

def get_dashboard_data() -> Dict:
    """返回所有仪表盘需要的数据（供 API 使用）"""
    sem = get_current_semester()
    today = date.today()

    # 最近7天学习时长
    daily_items = load_json(_daily_file(sem))
    daily_items.sort(key=lambda x: x["date"])
    seven_days = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    study_data = {}
    for d in seven_days:
        match = [i for i in daily_items if i["date"] == d]
        study_data[d] = match[0]["study_hours"] if match else 0

    # 最近7天打卡情况
    checkin_data = {}
    for d in seven_days:
        match = [i for i in daily_items if i["date"] == d]
        if match:
            rec = match[0]
            checkin_data[d] = {
                "reading": rec.get("reading", False),
                "exercise": rec.get("exercise", False),
                "early_rise": rec.get("early_rise", False),
                "mood": rec.get("mood", "😊"),
            }
        else:
            checkin_data[d] = None

    # 连续打卡天数
    items_sorted = sorted(daily_items, key=lambda x: x["date"], reverse=True)
    streak = 0
    check_date = today
    dates_set = {i["date"] for i in daily_items}
    while check_date.isoformat() in dates_set:
        streak += 1
        check_date -= timedelta(days=1)

    # 总学习时长
    total_study_hours = sum(i["study_hours"] for i in daily_items)

    # 复习进度汇总
    knowledge = load_json(_review_file(sem))
    total_knowledge = len(knowledge)
    avg_mastery = sum(k["mastery"] for k in knowledge) / total_knowledge if total_knowledge > 0 else 0
    low_mastery = [k for k in knowledge if k["mastery"] < 40]
    review_summary = {
        "total_knowledge": total_knowledge,
        "average_mastery": round(avg_mastery, 1),
        "low_mastery_count": len(low_mastery),
        "low_mastery_items": [{"id": k["id"], "course": k["course"], "topic": k["topic"], "mastery": k["mastery"]} for k in low_mastery],
    }

    # 错题统计
    wrong = load_json(_wrong_questions_file(sem))
    wrong_summary = {
        "total": len(wrong),
        "reviewed": sum(1 for w in wrong if w["reviewed"]),
        "unreviewed": sum(1 for w in wrong if not w["reviewed"]),
    }

    # 目标完成度
    goals = load_json(_goals_file(sem))
    goal_list_data = []
    for g in goals:
        pct = g["progress"] / g["target"] * 100 if g["target"] > 0 else 0
        milestones_done = sum(1 for m in g.get("milestones", []) if m["done"])
        milestones_total = len(g.get("milestones", []))
        goal_list_data.append({
            "id": g["id"], "title": g["title"], "type": g["type"],
            "progress": g["progress"], "target": g["target"],
            "percentage": round(pct, 1), "deadline": g.get("deadline", ""),
            "milestones_done": milestones_done, "milestones_total": milestones_total,
        })

    # 刷题正确率趋势
    practice = load_json(_practice_file(sem))
    practice.sort(key=lambda x: x["date"])
    practice_trend = []
    for p in practice:
        rate = round(p["correct"] / p["count"] * 100, 1) if p["count"] > 0 else 0
        practice_trend.append({
            "date": p["date"], "course": p["course"],
            "count": p["count"], "correct": p["correct"],
            "rate": rate, "duration_min": p["duration_min"],
        })

    return {
        "semester": sem,
        "date": today.isoformat(),
        "study_hours_7days": study_data,
        "checkin_7days": checkin_data,
        "streak": streak,
        "total_study_hours": round(total_study_hours, 1),
        "review_summary": review_summary,
        "wrong_summary": wrong_summary,
        "goals": goal_list_data,
        "practice_trend": practice_trend,
    }


# ── 大学规划模块 ──────────────────────────────────────────

def _plan_file(sem: str = None) -> Path:
    return get_semester_dir(sem) / "plan.json"


def plan_semester():
    """生成学期规划"""
    sem = get_current_semester()
    print(f"\n📋 学期规划 [{sem}]")
    print("=" * 60)
    print("\n请思考以下问题，我会帮你整理成规划：")
    print("  1. 本学期最重要的 3 个目标是什么？")
    print("  2. 有哪些重要时间节点（考试、比赛、活动）？")
    print("  3. 每周固定安排（课程表之外的时间）？")
    print("\n输入你的规划内容 (输入 'done' 结束):")

    lines = []
    while True:
        line = input("> ").strip()
        if line.lower() == "done":
            break
        lines.append(line)

    plan_text = "\n".join(lines)
    data = load_json(_plan_file(sem))
    data.append({
        "id": max([p.get("id", 0) for p in data], default=0) + 1,
        "type": "semester",
        "semester": sem,
        "title": f"{sem} 学期规划",
        "content": plan_text,
        "created": date.today().isoformat(),
        "done": False,
    })
    save_json(_plan_file(sem), data)
    print(f"\n✅ 学期规划已保存！")


def plan_week():
    """生成周计划"""
    sem = get_current_semester()
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    print(f"\n📋 周计划: {monday.isoformat()} ~ {sunday.isoformat()}")
    print("=" * 60)
    print("\n每天最重要的 1-3 件事 (输入 'done' 结束):")

    for i in range(7):
        day = monday + timedelta(days=i)
        print(f"\n【{WEEKDAYS_CN[i]} {day.isoformat()}】")
        items = []
        while True:
            item = input("  任务 (空行跳过): ").strip()
            if not item:
                break
            items.append(item)

        if items:
            data = load_json(_plan_file(sem))
            data.append({
                "id": max([p.get("id", 0) for p in data], default=0) + 1,
                "type": "week",
                "title": f"{WEEKDAYS_CN[i]} {day.isoformat()}",
                "date": day.isoformat(),
                "content": "\n".join(items),
                "created": today.isoformat(),
                "done": False,
            })
            save_json(_plan_file(sem), data)

    print("\n✅ 周计划已保存！")


def plan_day():
    """添加日计划"""
    sem = get_current_semester()
    today = date.today()

    print(f"\n📋 今日计划: {today.isoformat()} {WEEKDAYS_CN[today.weekday()]}")
    print("输入任务 (空行结束):")
    items = []
    while True:
        item = input("  • ").strip()
        if not item:
            break
        items.append(item)

    if items:
        data = load_json(_plan_file(sem))
        data.append({
            "id": max([p.get("id", 0) for p in data], default=0) + 1,
            "type": "day",
            "title": f"{today.isoformat()} 日计划",
            "date": today.isoformat(),
            "content": "\n".join(items),
            "created": today.isoformat(),
            "done": False,
        })
        save_json(_plan_file(sem), data)
        print("✅ 日计划已保存！")
    else:
        print("未添加任何任务")


def plan_fouryear():
    """大学四年规划"""
    sem = get_current_semester()
    print("\n🎯 大学四年规划")
    print("=" * 60)
    print("\n大一：适应 + 基础")
    print("  • 适应大学生活，养成学习习惯")
    print("  • 通过四六级，打好专业课基础")
    print("  • 参加 1-2 个社团，探索兴趣")
    print("\n大二：深耕 + 拓展")
    print("  • 确定专业方向，开始深入学习")
    print("  • 参加竞赛、科研项目")
    print("  • 考取相关证书（计算机二级、教资等）")
    print("\n大三：抉择 + 准备")
    print("  • 决定考研/出国/就业方向")
    print("  • 考研：开始系统复习")
    print("  • 就业：找实习，积累项目经验")
    print("\n大四：冲刺 + 收官")
    print("  • 考研：冲刺 + 复试")
    print("  • 就业：秋招 + 春招")
    print("  • 完成毕业论文，顺利毕业")
    print("\n" + "=" * 60)
    print("\n输入你自己的四年规划 (输入 'done' 结束):")

    lines = []
    while True:
        line = input("> ").strip()
        if line.lower() == "done":
            break
        lines.append(line)

    if lines:
        data = load_json(_plan_file(sem))
        data.append({
            "id": max([p.get("id", 0) for p in data], default=0) + 1,
            "type": "fouryear",
            "title": "大学四年规划",
            "content": "\n".join(lines),
            "created": date.today().isoformat(),
            "done": False,
        })
        save_json(_plan_file(sem), data)
        print("\n✅ 四年规划已保存！")


def plan_list():
    """列出所有规划"""
    sem = get_current_semester()
    data = load_json(_plan_file(sem))
    if not data:
        print("📭 暂无规划")
        return

    type_labels = {"semester": "📋 学期", "week": "📅 周", "day": "📌 日", "fouryear": "🎯 四年"}
    print(f"\n📋 规划列表 [{sem}]")
    print("=" * 60)

    for p in sorted(data, key=lambda x: x.get("created", ""), reverse=True):
        label = type_labels.get(p.get("type", ""), "📌")
        status = "✅" if p.get("done") else "⏳"
        print(f"  [{p['id']}] {label} {status} {p.get('title','')}")
        if p.get("date"):
            print(f"      日期: {p['date']}")
        if p.get("content"):
            for line in p["content"].split("\n")[:3]:
                print(f"        {line}")
    print("=" * 60)


def plan_done(plan_id: int):
    """标记规划完成"""
    sem = get_current_semester()
    data = load_json(_plan_file(sem))
    for p in data:
        if p["id"] == plan_id:
            p["done"] = True
            save_json(_plan_file(sem), data)
            print(f"✅ 规划 [{plan_id}] 已完成！")
            return
    print(f"❌ 未找到 ID 为 {plan_id} 的规划")


# ── iCal 导出 ──────────────────────────────────────────

def export_ical(output: str, export_type: str = "all"):
    """导出课表/考试/作业为 iCal 格式"""
    sem = get_current_semester()
    today = date.today()
    # 找到本周一
    monday = today - timedelta(days=today.weekday())

    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//大学生助手//CN",
           "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
           "X-WR-CALNAME:大学生助手 - 课表", "X-WR-TIMEZONE:Asia/Shanghai"]

    if export_type in ("all", "schedule"):
        schedule = load_json(_schedule_file(sem))
        for c in schedule:
            for wk in range(1, 17):  # 默认16周
                event_date = monday + timedelta(days=c["day"] - 1, weeks=wk - 1)
                start_time, end_time = c["time"].split("-")
                dtstart = f"{event_date.isoformat().replace('-','')}T{start_time.replace(':','')}00"
                dtend = f"{event_date.isoformat().replace('-','')}T{end_time.replace(':','')}00"
                ics.extend([
                    "BEGIN:VEVENT",
                    f"DTSTART:{dtstart}", f"DTEND:{dtend}",
                    f"SUMMARY:{c['course']}",
                    f"LOCATION:{c.get('location','')}",
                    f"DESCRIPTION:教师: {c.get('teacher','')}\\n周次: 第{wk}周",
                    "END:VEVENT"
                ])

    if export_type in ("all", "exam"):
        exams = load_json(_exam_file(sem))
        for e in exams:
            ed = e["date"].replace("-", "")
            ics.extend([
                "BEGIN:VEVENT",
                f"DTSTART;VALUE=DATE:{ed}", f"DTEND;VALUE=DATE:{ed}",
                f"SUMMARY:📝 {e['course']} - {e['type']}",
                f"LOCATION:{e.get('location','')}",
                f"DESCRIPTION:{e.get('note','')}",
                "BEGIN:VALARM", "TRIGGER:-PT1440M", "ACTION:DISPLAY",
                f"DESCRIPTION:明天 {e['course']} {e['type']}！", "END:VALARM",
                "END:VEVENT"
            ])

    if export_type in ("all", "homework"):
        hw = load_json(_homework_file(sem))
        for h in hw:
            if h["done"]:
                continue
            dl = h["deadline"].replace("-", "")
            ics.extend([
                "BEGIN:VEVENT",
                f"DTSTART;VALUE=DATE:{dl}", f"DTEND;VALUE=DATE:{dl}",
                f"SUMMARY:📄 {h['course']}: {h['title']}",
                f"DESCRIPTION:{h.get('note','')}",
                "BEGIN:VALARM", "TRIGGER:-PT180M", "ACTION:DISPLAY",
                f"DESCRIPTION:{h['course']}作业 3小时后截止！", "END:VALARM",
                "END:VEVENT"
            ])

    ics.append("END:VCALENDAR")

    out_path = Path(output)
    out_path.write_text("\r\n".join(ics), encoding="utf-8")
    print(f"✅ 已导出到 {out_path.absolute()}")
    print(f"💡 双击 .ics 文件即可导入到 Apple Calendar / Google Calendar / Outlook")


# ── CLI 入口 ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🎓 大学生助手 v1.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python3 engine.py init                       # 初始化
  python3 engine.py semester new 2025-春季      # 创建新学期
  python3 engine.py semester switch 2025-春季   # 切换学期
  python3 engine.py semester list               # 列出学期
  python3 engine.py schedule import 课表.json    # 导入课表
  python3 engine.py schedule show               # 查看课表
  python3 engine.py schedule today              # 今日课程
  python3 engine.py homework add                # 添加作业
  python3 engine.py homework list               # 查看作业
  python3 engine.py homework done 1             # 标记完成
  python3 engine.py exam add                    # 添加考试
  python3 engine.py exam countdown              # 考试倒计时
  python3 engine.py remind                      # 今日提醒
  python3 engine.py export ical --output 课表.ics  # 导出日历
        """
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="初始化")
    subparsers.add_parser("remind", help="今日提醒")
    subparsers.add_parser("data-dir", help="显示数据目录路径")

    # semester
    sem_p = subparsers.add_parser("semester", help="学期管理")
    sem_sub = sem_p.add_subparsers(dest="subcommand")
    sem_new = sem_sub.add_parser("new", help="创建新学期")
    sem_new.add_argument("name", help="学期名称")
    sem_sw = sem_sub.add_parser("switch", help="切换学期")
    sem_sw.add_argument("name", help="学期名称")
    sem_sub.add_parser("list", help="列出学期")

    # schedule
    sched = subparsers.add_parser("schedule", help="课表")
    sched_sub = sched.add_subparsers(dest="subcommand")
    si = sched_sub.add_parser("import", help="导入课表")
    si.add_argument("file")
    sched_sub.add_parser("show", help="查看课表")
    sched_sub.add_parser("today", help="今日课程")

    # homework
    hw = subparsers.add_parser("homework", help="作业")
    hw_sub = hw.add_subparsers(dest="subcommand")
    hw_sub.add_parser("add")
    hl = hw_sub.add_parser("list")
    hl.add_argument("--all", action="store_true")
    hd = hw_sub.add_parser("done")
    hd.add_argument("id", type=int)
    hdel = hw_sub.add_parser("delete")
    hdel.add_argument("id", type=int)

    # exam
    ex = subparsers.add_parser("exam", help="考试")
    ex_sub = ex.add_subparsers(dest="subcommand")
    ex_sub.add_parser("add")
    ex_sub.add_parser("list")
    ex_sub.add_parser("countdown")
    edel = ex_sub.add_parser("delete")
    edel.add_argument("id", type=int)

    # review
    rev = subparsers.add_parser("review", help="期末复习")
    rev_sub = rev.add_subparsers(dest="subcommand")
    # review knowledge
    rev_k = rev_sub.add_parser("knowledge", help="知识点管理")
    rev_k_sub = rev_k.add_subparsers(dest="action")
    rev_k_sub.add_parser("add")
    rev_k_sub.add_parser("list")
    rev_ku = rev_k_sub.add_parser("update")
    rev_ku.add_argument("id", type=int)
    rev_ku.add_argument("mastery", type=int)
    # review practice
    rev_p = rev_sub.add_parser("practice", help="刷题管理")
    rev_p_sub = rev_p.add_subparsers(dest="action")
    rev_p_sub.add_parser("add")
    rev_p_sub.add_parser("list")
    rev_p_sub.add_parser("stats")
    # review wrong
    rev_w = rev_sub.add_parser("wrong", help="错题管理")
    rev_w_sub = rev_w.add_subparsers(dest="action")
    rev_w_sub.add_parser("add")
    rev_w_sub.add_parser("list")
    rev_wr = rev_w_sub.add_parser("review")
    rev_wr.add_argument("id", type=int)
    # review plan
    rev_sub.add_parser("plan")

    # daily
    daily = subparsers.add_parser("daily", help="每日成长记录")
    daily_sub = daily.add_subparsers(dest="subcommand")
    daily_sub.add_parser("checkin")
    dl = daily_sub.add_parser("list")
    dl.add_argument("--days", type=int, default=7)
    daily_sub.add_parser("stats")

    # goal
    goal = subparsers.add_parser("goal", help="目标管理")
    goal_sub = goal.add_subparsers(dest="subcommand")
    goal_sub.add_parser("add")
    goal_sub.add_parser("list")
    gu = goal_sub.add_parser("update")
    gu.add_argument("id", type=int)
    gu.add_argument("progress", type=int)
    # goal milestone
    gm = goal_sub.add_parser("milestone", help="里程碑管理")
    gm_sub = gm.add_subparsers(dest="action")
    gma = gm_sub.add_parser("add")
    gma.add_argument("id", type=int)
    gma.add_argument("name")
    gmd = gm_sub.add_parser("done")
    gmd.add_argument("id", type=int)
    gmd.add_argument("index", type=int)

    # dashboard
    subparsers.add_parser("dashboard", help="仪表盘数据")

    # plan
    pl = subparsers.add_parser("plan", help="大学规划")
    pl_sub = pl.add_subparsers(dest="subcommand")
    pl_sub.add_parser("semester", help="学期规划")
    pl_sub.add_parser("week", help="周计划")
    pl_sub.add_parser("day", help="日计划")
    pl_sub.add_parser("fouryear", help="四年规划")
    pl_sub.add_parser("list", help="查看所有规划")
    pld = pl_sub.add_parser("done", help="标记完成")
    pld.add_argument("id", type=int)

    # export
    exp = subparsers.add_parser("export", help="导出")
    exp_sub = exp.add_subparsers(dest="subcommand")
    exp_ical = exp_sub.add_parser("ical", help="导出 iCal")
    exp_ical.add_argument("--type", default="all", choices=["all", "schedule", "exam", "homework"])
    exp_ical.add_argument("--output", "-o", default="课表.ics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help(); return

    if args.command == "init":
        init_cmd()
    elif args.command == "remind":
        remind()
    elif args.command == "data-dir":
        print(get_semester_dir())
    elif args.command == "semester":
        if args.subcommand == "new": semester_new(args.name)
        elif args.subcommand == "switch": semester_switch(args.name)
        elif args.subcommand == "list": semester_list()
        else: sem_p.print_help()
    elif args.command == "schedule":
        if args.subcommand == "import": schedule_import(args.file)
        elif args.subcommand == "show": schedule_show()
        elif args.subcommand == "today": schedule_today()
        else: sched.print_help()
    elif args.command == "homework":
        if args.subcommand == "add": homework_add()
        elif args.subcommand == "list": homework_list(show_all=args.all)
        elif args.subcommand == "done": homework_done(args.id)
        elif args.subcommand == "delete": homework_delete(args.id)
        else: hw.print_help()
    elif args.command == "exam":
        if args.subcommand == "add": exam_add()
        elif args.subcommand == "list": exam_list()
        elif args.subcommand == "countdown": exam_countdown()
        elif args.subcommand == "delete": exam_delete(args.id)
        else: ex.print_help()
    elif args.command == "review":
        if args.subcommand == "knowledge":
            if args.action == "add": review_knowledge_add()
            elif args.action == "list": review_knowledge_list()
            elif args.action == "update": review_knowledge_update(args.id, args.mastery)
            else: rev_k.print_help()
        elif args.subcommand == "practice":
            if args.action == "add": review_practice_add()
            elif args.action == "list": review_practice_list()
            elif args.action == "stats": review_practice_stats()
            else: rev_p.print_help()
        elif args.subcommand == "wrong":
            if args.action == "add": review_wrong_add()
            elif args.action == "list": review_wrong_list()
            elif args.action == "review": review_wrong_review(args.id)
            else: rev_w.print_help()
        elif args.subcommand == "plan":
            review_plan()
        else:
            rev.print_help()
    elif args.command == "daily":
        if args.subcommand == "checkin": daily_checkin()
        elif args.subcommand == "list": daily_list(days=args.days)
        elif args.subcommand == "stats": daily_stats()
        else: daily.print_help()
    elif args.command == "goal":
        if args.subcommand == "add": goal_add()
        elif args.subcommand == "list": goal_list()
        elif args.subcommand == "update": goal_update(args.id, args.progress)
        elif args.subcommand == "milestone":
            if args.action == "add": goal_milestone(args.id, args.name)
            elif args.action == "done": goal_milestone_done(args.id, args.index)
            else: gm.print_help()
        else: goal.print_help()
    elif args.command == "dashboard":
        import json as _json
        print(_json.dumps(get_dashboard_data(), ensure_ascii=False, indent=2))
    elif args.command == "plan":
        if args.subcommand == "semester": plan_semester()
        elif args.subcommand == "week": plan_week()
        elif args.subcommand == "day": plan_day()
        elif args.subcommand == "fouryear": plan_fouryear()
        elif args.subcommand == "list": plan_list()
        elif args.subcommand == "done":
            plan_done(args.id)
        else: pl.print_help()
    elif args.command == "export":
        if args.subcommand == "ical": export_ical(args.output, args.type)
        else: exp.print_help()


if __name__ == "__main__":
    main()
