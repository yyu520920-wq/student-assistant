#!/usr/bin/env python3
"""
大学日程计划 v3.0 — 原创设计的大学生日程与学习管理工具（非交互式重构版）
功能：任务管理、子任务、优先级、标签、清单分类、四象限、
      番茄专注、习惯打卡、倒数日、过滤器、今日概览、
      课表、作业、考试、多学期管理、数据导出

设计原则：全部命令参数驱动，无 input() 交互，AI 可直接调用。
数据存储：~/.student-assistant/
优先级统一：1=高🔴 2=中🟡 3=低🟢 0=无⚪
"""

import json, os, sys, argparse, tempfile
from datetime import datetime, date, timedelta
from pathlib import Path
import uuid

# ── 路径 ──
BASE = Path.home() / ".student-assistant"
CUR = BASE / "current.json"
WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# 优先级统一映射：1=高 2=中 3=低 0=无
PRIORITY_ICON = {1: "🔴", 2: "🟡", 3: "🟢", 0: "⚪"}
EISENHOWER_ICON = {
    "important-urgent": "🔥",
    "important-not-urgent": "⭐",
    "not-important-urgent": "⏰",
    "not-important-not-urgent": "💤",
}


def _d():
    BASE.mkdir(parents=True, exist_ok=True)


def _r(p):
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def _w(p, d):
    _d()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def _sd(name=None):
    if name is None:
        name = _cs()
    return BASE / "semesters" / name


def _cs():
    if CUR.exists():
        try:
            return json.loads(CUR.read_text())["semester"]
        except Exception:
            pass
    return "默认学期"


def _sc(name):
    _d()
    CUR.write_text(json.dumps({"semester": name}, ensure_ascii=False))


def _sf(s=None): return _sd(s) / "schedule.json"
def _hf(s=None): return _sd(s) / "homework.json"
def _ef(s=None): return _sd(s) / "exam.json"
def _tf(s=None): return _sd(s) / "tasks.json"
def _lf(s=None): return _sd(s) / "lists.json"
def _hbf(s=None): return _sd(s) / "habits.json"
def _pf(s=None): return _sd(s) / "pomodoro.json"
def _cdf(s=None): return _sd(s) / "countdowns.json"
# 以下路径函数供 web/server.py 使用（CLI 未暴露对应命令）
def _df(s=None): return _sd(s) / "daily.json"
def _gf(s=None): return _sd(s) / "goals.json"
def _rf(s=None): return _sd(s) / "review.json"
def _prf(s=None): return _sd(s) / "practice.json"
def _wf(s=None): return _sd(s) / "wrong_questions.json"
def _plf(s=None): return _sd(s) / "plan.json"


def _now(): return datetime.now().strftime("%Y-%m-%d %H:%M")
def _today(): return date.today()
def _parse_date(s): return datetime.strptime(s, "%Y-%m-%d").date()


# ── 初始化 ──
def init():
    sem = _cs(); sd = _sd(sem); sd.mkdir(parents=True, exist_ok=True)
    t = _today()
    if not _r(_lf(sem)):
        _w(_lf(sem), [
            {"id": "inbox", "name": "收集箱", "icon": "📥", "color": "#667eea"},
            {"id": "work", "name": "学习", "icon": "📚", "color": "#52c41a"},
            {"id": "personal", "name": "生活", "icon": "🏠", "color": "#faad14"},
            {"id": "project", "name": "项目", "icon": "🚀", "color": "#f5222d"},
        ])
    if not _r(_tf(sem)):
        _w(_tf(sem), [
            {"id": "t1", "title": "完成高等数学习题3.2", "list_id": "work", "priority": 2,
             "tags": ["数学", "作业"],
             "due_date": (t + timedelta(days=3)).isoformat(),
             "reminder": None, "repeat": None, "eisenhower": "important-urgent",
             "done": False, "subtasks": [
                 {"title": "复习第三章笔记", "done": True},
                 {"title": "做完1-5题", "done": False},
                 {"title": "做完6-10题", "done": False}],
             "note": "交纸质版", "created": _now(), "completed": None},
            {"id": "t2", "title": "背英语单词 Unit 5", "list_id": "work", "priority": 1,
             "tags": ["英语", "每日"],
             "due_date": (t + timedelta(days=1)).isoformat(), "reminder": None,
             "repeat": "daily", "eisenhower": "important-not-urgent",
             "done": False, "subtasks": [], "note": "用墨墨背单词",
             "created": _now(), "completed": None},
            {"id": "t3", "title": "跑步 5 公里", "list_id": "personal", "priority": 3,
             "tags": ["运动"],
             "due_date": t.isoformat(), "reminder": None, "repeat": "weekly",
             "eisenhower": "not-important-urgent",
             "done": False, "subtasks": [], "note": "操场",
             "created": _now(), "completed": None},
            {"id": "t4", "title": "准备社团活动策划案", "list_id": "project", "priority": 2,
             "tags": ["社团", "策划"],
             "due_date": (t + timedelta(days=7)).isoformat(), "reminder": None,
             "repeat": None, "eisenhower": "important-not-urgent",
             "done": False, "subtasks": [
                 {"title": "写活动方案", "done": True},
                 {"title": "做预算", "done": False},
                 {"title": "联系场地", "done": False}],
             "note": "下周三前完成", "created": _now(), "completed": None},
        ])
    if not _r(_hbf(sem)):
        _w(_hbf(sem), [
            {"id": "h1", "name": "早起 7:00", "icon": "🌅", "goal": "daily", "streak": 5,
             "total": 30, "logs": [(t - timedelta(days=i)).isoformat() for i in range(5)]},
            {"id": "h2", "name": "阅读 30 分钟", "icon": "📖", "goal": "daily", "streak": 3,
             "total": 20, "logs": [(t - timedelta(days=i)).isoformat() for i in range(3)]},
            {"id": "h3", "name": "运动", "icon": "🏃", "goal": "weekly_3", "streak": 2,
             "total": 10, "logs": [(t - timedelta(days=i)).isoformat() for i in range(0, 7, 2)]},
        ])
    if not _r(_cdf(sem)):
        _w(_cdf(sem), [
            {"id": "c1", "title": "六级考试", "date": (t + timedelta(days=150)).isoformat(),
             "type": "exam", "repeat": "none"},
            {"id": "c2", "title": "寒假开始", "date": (t + timedelta(days=180)).isoformat(),
             "type": "vacation", "repeat": "yearly"},
            {"id": "c3", "title": "生日", "date": "2026-12-25", "type": "personal", "repeat": "yearly"},
        ])
    if not _r(_sf(sem)):
        _w(_sf(sem), [
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
    if not _r(_hf(sem)):
        _w(_hf(sem), [
            {"id": 1, "course": "高等数学", "title": "习题3.2", "deadline": (t + timedelta(days=3)).isoformat(), "done": False, "note": "交纸质版"},
            {"id": 2, "course": "大学英语", "title": "Unit 5 翻译", "deadline": (t + timedelta(days=5)).isoformat(), "done": False, "note": "学习通提交"},
        ])
    if not _r(_ef(sem)):
        _w(_ef(sem), [
            {"id": 1, "course": "高等数学", "type": "期中考试", "date": (t + timedelta(days=14)).isoformat(), "location": "教1-301", "note": "第1-4章"},
            {"id": 2, "course": "大学英语", "type": "期末考试", "date": (t + timedelta(days=45)).isoformat(), "location": "待定", "note": "含听力"},
        ])
    print(f"✅ 初始化完成！数据目录: {sd}")
    print(f"📊 示例数据：4个清单、4个任务、3个习惯、3个倒数日、9门课、2个作业、2场考试")


# ── 任务管理 ──
def task_add(title, list_id="inbox", priority=2, due=None, reminder=None,
             tags=None, repeat=None, eisenhower=None, note=None, subtasks=None):
    sem = _cs(); data = _r(_tf(sem))
    task = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "list_id": list_id,
        "priority": priority,
        "due_date": due,
        "reminder": reminder,
        "repeat": repeat,
        "eisenhower": eisenhower,
        "tags": [t.strip() for t in tags.split(",") if t.strip()] if tags else [],
        "done": False,
        "subtasks": [{"title": s.strip(), "done": False} for s in subtasks.split("|") if s.strip()] if subtasks else [],
        "note": note,
        "created": _now(),
        "completed": None,
    }
    data.append(task)
    _w(_tf(sem), data)
    print(f"✅ 任务已添加 ({task['id']}) {PRIORITY_ICON.get(priority, '⚪')} {title}")
    if task["subtasks"]:
        print(f"   子任务 {len(task['subtasks'])} 项")


def task_list(list_id=None, show_done=False, filter_str=None):
    sem = _cs(); data = _r(_tf(sem)); lists = _r(_lf(sem))
    lm = {l["id"]: l for l in lists}
    if list_id:
        data = [t for t in data if t["list_id"] == list_id]
    if filter_str:
        data = [t for t in data if filter_str.lower() in t["title"].lower()
                or any(filter_str.lower() in tag.lower() for tag in t.get("tags", []))]
    if not show_done:
        data = [t for t in data if not t["done"]]
    data.sort(key=lambda t: (t.get("priority", 2) or 2))
    print(f"\n📝 任务 ({len(data)}项)")
    if not data:
        print("  📭 暂无任务")
        return
    for t in data:
        p_icon = PRIORITY_ICON.get(t.get("priority", 2), "⚪")
        d_icon = "✅" if t["done"] else "⏳"
        eis_icon = EISENHOWER_ICON.get(t.get("eisenhower", ""), "")
        tags_str = " ".join(f"#{tag}" for tag in t.get("tags", []))
        list_name = lm.get(t["list_id"], {}).get("name", t["list_id"])
        print(f"  [{t['id']}] {p_icon}{d_icon}{eis_icon} {t['title']} | {list_name} {tags_str}")
        if t.get("due_date"):
            print(f"      📅 {t['due_date']}")
        if t.get("subtasks"):
            done_st = sum(1 for s in t["subtasks"] if s["done"])
            print(f"      📋 子任务: {done_st}/{len(t['subtasks'])}")
            for s in t["subtasks"]:
                print(f"        {'✅' if s['done'] else '⬜'} {s['title']}")


def task_done(tid):
    sem = _cs(); data = _r(_tf(sem))
    for t in data:
        if t["id"] == tid:
            t["done"] = True; t["completed"] = _now()
            _w(_tf(sem), data)
            print(f"✅ 已完成: {t['title']}")
            return
    print(f"❌ 未找到任务 {tid}")


def task_delete(tid):
    sem = _cs(); data = _r(_tf(sem))
    data = [t for t in data if t["id"] != tid]
    _w(_tf(sem), data)
    print(f"🗑️ 已删除任务 {tid}")


def task_subtask_done(tid, idx):
    sem = _cs(); data = _r(_tf(sem))
    for t in data:
        if t["id"] == tid:
            if 0 <= idx < len(t["subtasks"]):
                t["subtasks"][idx]["done"] = True
                _w(_tf(sem), data)
                print(f"✅ 子任务完成: {t['subtasks'][idx]['title']}")
                return
    print("❌ 未找到任务或子任务索引越界")


# ── 清单管理 ──
def list_add(name, lid=None, icon="📋", color="#667eea"):
    sem = _cs(); data = _r(_lf(sem))
    if lid is None:
        lid = name.lower().replace(" ", "_")
    data.append({"id": lid, "name": name, "icon": icon, "color": color})
    _w(_lf(sem), data)
    print(f"✅ 清单已创建: {icon} {name} ({lid})")


def list_show():
    sem = _cs(); lists = _r(_lf(sem)); tasks = _r(_tf(sem))
    print("\n📋 清单")
    for l in lists:
        count = sum(1 for t in tasks if t["list_id"] == l["id"] and not t["done"])
        print(f"  {l.get('icon', '📋')} {l['name']} ({l['id']}) — {count} 个待办")


# ── 习惯打卡 ──
def habit_add(name, icon="✅", goal="daily"):
    sem = _cs(); data = _r(_hbf(sem))
    data.append({"id": str(uuid.uuid4())[:8], "name": name, "icon": icon,
                 "goal": goal, "streak": 0, "total": 0, "logs": []})
    _w(_hbf(sem), data)
    print(f"✅ 习惯已创建: {icon} {name}")


def habit_checkin(hid):
    sem = _cs(); data = _r(_hbf(sem)); t = _today().isoformat()
    for h in data:
        if h["id"] == hid:
            if t not in h["logs"]:
                h["logs"].append(t); h["total"] += 1
            logs = sorted(set(h["logs"]), reverse=True); streak = 0
            check = _today()
            for d in logs:
                if d == check.isoformat():
                    streak += 1; check -= timedelta(days=1)
                else:
                    break
            h["streak"] = streak
            _w(_hbf(sem), data)
            print(f"✅ {h['icon']} {h['name']} 打卡成功！连续 {streak} 天 🔥")
            return
    print("❌ 未找到习惯")


def habit_list():
    sem = _cs(); data = _r(_hbf(sem))
    if not data:
        print("📭 暂无习惯"); return
    print("\n✅ 习惯打卡")
    t = _today().isoformat()
    for h in data:
        done_today = t in h["logs"]
        print(f"  [{h['id']}] {h['icon']} {h['name']} | "
              f"{'✅ 今日已打卡' if done_today else '⬜ 今日未打卡'} | "
              f"🔥 {h['streak']}天 | 总计 {h['total']}次")


# ── 番茄专注（非阻塞：直接记录完成，不真实倒计时）──
def pomodoro_log(duration=25, task=None):
    """记录一个已完成的番茄钟（不阻塞，AI 可直接调用）"""
    sem = _cs(); data = _r(_pf(sem))
    data.append({"date": _today().isoformat(), "duration": duration,
                 "task": task, "completed": True, "time": _now()})
    _w(_pf(sem), data)
    print(f"🍅 已记录番茄钟：{duration} 分钟" + (f" | 关联: {task}" if task else ""))


def pomodoro_stats():
    sem = _cs(); data = _r(_pf(sem))
    if not data:
        print("📭 暂无专注记录"); return
    total = sum(d["duration"] for d in data); count = len(data)
    today_count = sum(1 for d in data if d["date"] == _today().isoformat())
    print(f"\n🍅 番茄统计")
    print(f"  总专注: {count} 次, {total} 分钟 ({total // 60}小时{total % 60}分钟)")
    print(f"  今日: {today_count} 次")
    print(f"  近7天:")
    for i in range(6, -1, -1):
        d = (_today() - timedelta(days=i)).isoformat()
        day_count = sum(1 for p in data if p["date"] == d)
        bar = "▓" * day_count + "░" * max(5 - day_count, 0)
        print(f"    {d} [{bar}] {day_count}次")


# ── 倒数日 ──
def countdown_add(title, date_str, tp="other", repeat="none"):
    sem = _cs(); data = _r(_cdf(sem))
    data.append({"id": str(uuid.uuid4())[:8], "title": title, "date": date_str,
                 "type": tp, "repeat": repeat})
    _w(_cdf(sem), data)
    print(f"✅ 倒数日已添加: {title} ({date_str})")


def countdown_list():
    sem = _cs(); data = _r(_cdf(sem))
    if not data:
        print("📭 暂无倒数日"); return
    t = _today(); data.sort(key=lambda x: x["date"])
    print("\n🎯 倒数日")
    for c in data:
        days = (_parse_date(c["date"]) - t).days
        icon = "🔴" if days <= 7 else ("🟡" if days <= 30 else "🟢")
        if days < 0:
            icon = "⚫"; status = f"已过 {-days} 天"
        elif days == 0:
            status = "就是今天！🎉"
        else:
            status = f"还有 {days} 天"
        print(f"  [{c['id']}] {icon} {c['title']} | {c['date']} | {status}")


# ── 四象限视图 ──
def eisenhower_view():
    sem = _cs(); tasks = _r(_tf(sem)); lists = _r(_lf(sem))
    lm = {l["id"]: l for l in lists}
    quads = {"important-urgent": [], "important-not-urgent": [],
             "not-important-urgent": [], "not-important-not-urgent": []}
    for t in tasks:
        if t["done"]:
            continue
        q = t.get("eisenhower", "not-important-not-urgent")
        if q in quads:
            quads[q].append(t)
    labels = {
        "important-urgent": "🔥 重要且紧急 — 立即做",
        "important-not-urgent": "⭐ 重要不紧急 — 计划做",
        "not-important-urgent": "⏰ 不重要紧急 — 委托做",
        "not-important-not-urgent": "💤 不重要不紧急 — 尽量不做",
    }
    print("\n🔲 四象限")
    for q, label in labels.items():
        items = quads[q]
        print(f"\n{label} ({len(items)}项)")
        for t in items:
            p_icon = PRIORITY_ICON.get(t.get("priority", 2), "⚪")
            print(f"  [{t['id']}] {p_icon} {t['title']} | {lm.get(t['list_id'], {}).get('name', '')}")


# ── 过滤器（参数驱动）──
def filter_view(filter_type="today", tag=None):
    sem = _cs(); tasks = _r(_tf(sem)); lists = _r(_lf(sem))
    lm = {l["id"]: l for l in lists}
    t = _today()
    if filter_type == "today":
        tasks = [tk for tk in tasks if tk.get("due_date") and _parse_date(tk["due_date"]) <= t and not tk["done"]]
        print(f"\n📅 今天到期及逾期 ({len(tasks)}项)")
    elif filter_type == "7days":
        tasks = [tk for tk in tasks if tk.get("due_date") and 0 <= (_parse_date(tk["due_date"]) - t).days <= 7 and not tk["done"]]
        print(f"\n📅 7天内到期 ({len(tasks)}项)")
    elif filter_type == "high":
        tasks = [tk for tk in tasks if tk.get("priority") == 1 and not tk["done"]]
        print(f"\n🔴 高优先级 ({len(tasks)}项)")
    elif filter_type == "tag":
        if not tag:
            print("❌ 按标签筛选需要 --tag 参数"); return
        tasks = [tk for tk in tasks if tag in tk.get("tags", []) and not tk["done"]]
        print(f"\n🏷️ #{tag} ({len(tasks)}项)")
    else:
        print(f"❌ 未知过滤器类型: {filter_type}（可选: today/7days/high/tag）"); return
    for tk in tasks:
        p_icon = PRIORITY_ICON.get(tk.get("priority", 2), "⚪")
        print(f"  [{tk['id']}] {p_icon} {tk['title']} | {lm.get(tk['list_id'], {}).get('name', '')} | {tk.get('due_date', '')}")


# ── 今日概览 ──
def today_overview():
    sem = _cs(); t = _today(); dow = t.weekday()
    tasks = _r(_tf(sem)); lists = _r(_lf(sem)); lm = {l["id"]: l for l in lists}
    habits = _r(_hbf(sem)); exams = _r(_ef(sem)); schedule = _r(_sf(sem))

    print(f"\n🔔 {t.isoformat()} {WEEKDAYS[dow]} 今日概览")
    print("=" * 60)

    today_courses = [c for c in schedule if c["day"] == dow + 1]
    print(f"\n📅 课程 ({len(today_courses)}节):")
    if today_courses:
        for c in sorted(today_courses, key=lambda x: x["time"]):
            print(f"  {c['time']} {c['course']} @ {c.get('location', '')}")
    else:
        print("  无课 🎉")

    today_tasks = [tk for tk in tasks if tk.get("due_date") and _parse_date(tk["due_date"]) <= t and not tk["done"]]
    print(f"\n📝 今日任务 ({len(today_tasks)}项):")
    if today_tasks:
        for tk in today_tasks:
            p_icon = PRIORITY_ICON.get(tk.get("priority", 2), "⚪")
            print(f"  {p_icon} {tk['title']} | {lm.get(tk['list_id'], {}).get('name', '')}")
    else:
        print("  无今日任务 ✅")

    print(f"\n✅ 习惯打卡:")
    if habits:
        for h in habits:
            done_today = t.isoformat() in h["logs"]
            print(f"  {'✅' if done_today else '⬜'} {h['icon']} {h['name']} | 🔥 {h['streak']}天")
    else:
        print("  暂无习惯")

    near = [e for e in exams if 0 <= (_parse_date(e["date"]) - t).days <= 14]
    if near:
        print(f"\n⏰ 临近考试 ({len(near)}场):")
        for e in sorted(near, key=lambda x: x["date"]):
            days = (_parse_date(e["date"]) - t).days
            print(f"  {'🔴' if days <= 3 else '🟡'} {e['course']} {e['type']}: {e['date']} (剩{days}天)")

    print("\n" + "=" * 60)


# ── 数据导出（跨平台临时目录）──
def export_all_json():
    sem = _cs()
    all_data = {
        "semester": sem, "exported": _now(),
        "tasks": _r(_tf(sem)), "lists": _r(_lf(sem)), "habits": _r(_hbf(sem)),
        "pomodoro": _r(_pf(sem)), "countdowns": _r(_cdf(sem)),
        "schedule": _r(_sf(sem)), "homework": _r(_hf(sem)), "exams": _r(_ef(sem)),
    }
    out_dir = Path(tempfile.gettempdir())
    path = out_dir / "student-assistant-full-export.json"
    _w(path, all_data)
    print(f"✅ 已导出完整数据到 {path}")


# ── 课表 ──
def schedule_import(fp):
    p = Path(fp)
    if not p.exists():
        print(f"❌ 文件不存在: {fp}"); return
    if p.suffix == ".json":
        _w(_sf(), json.loads(p.read_text(encoding="utf-8")))
    elif p.suffix == ".csv":
        import csv
        data = [{"day": int(r["day"]), "time": r["time"], "course": r["course"],
                 "teacher": r.get("teacher", ""), "location": r.get("location", ""),
                 "weeks": r.get("weeks", "1-16")}
                for r in csv.DictReader(p.read_text(encoding="utf-8").splitlines())]
        _w(_sf(), data)
    else:
        print(f"❌ 不支持的格式: {p.suffix}（支持 .json / .csv）"); return
    print(f"✅ 课表已导入: {fp}")


def schedule_show():
    sem = _cs(); data = _r(_sf(sem))
    if not data:
        print("📭 课表为空"); return
    for d in range(1, 8):
        courses = sorted([c for c in data if c["day"] == d], key=lambda c: c["time"])
        if courses:
            print(f"\n【{WEEKDAYS[d - 1]}】")
            for c in courses:
                print(f"  {c['time']} {c['course']} {c.get('teacher', '')} @ {c.get('location', '')}")


def schedule_today():
    sem = _cs(); dow = _today().weekday(); data = _r(_sf(sem))
    courses = sorted([c for c in data if c["day"] == dow + 1], key=lambda c: c["time"])
    print(f"\n📅 {WEEKDAYS[dow]}")
    if courses:
        for c in courses:
            print(f"  {c['time']} {c['course']} @ {c.get('location', '')}")
    else:
        print("🎉 今天没有课！")


# ── 作业 ──
def homework_add(course, title, deadline, note=""):
    sem = _cs(); data = _r(_hf(sem))
    new_id = max([h.get("id", 0) for h in data], default=0) + 1
    data.append({"id": new_id, "course": course, "title": title,
                 "deadline": deadline, "done": False, "note": note})
    _w(_hf(sem), data)
    print(f"✅ 作业已添加: [{new_id}] {course}: {title} (截止 {deadline})")


def homework_list():
    sem = _cs(); data = _r(_hf(sem))
    pending = [h for h in data if not h["done"]]
    if not pending:
        print("📭 暂无待办作业"); return
    print(f"\n📝 作业 ({len(pending)}项待办)")
    for h in sorted(pending, key=lambda x: x["deadline"]):
        days = (_parse_date(h["deadline"]) - _today()).days
        u = "🔴" if days <= 1 else ("🟡" if days <= 3 else "🟢")
        print(f"  [{h['id']}] {u} {h['course']}: {h['title']} (剩{days}天)")


def homework_done(hid):
    sem = _cs(); data = _r(_hf(sem))
    for h in data:
        if h["id"] == hid:
            h["done"] = True; _w(_hf(sem), data)
            print(f"✅ 作业已完成: {h['course']}: {h['title']}"); return
    print(f"❌ 未找到作业 {hid}")


# ── 考试 ──
def exam_add(course, etype, edate, location="", note=""):
    sem = _cs(); data = _r(_ef(sem))
    new_id = max([e.get("id", 0) for e in data], default=0) + 1
    data.append({"id": new_id, "course": course, "type": etype, "date": edate,
                 "location": location, "note": note})
    _w(_ef(sem), data)
    print(f"✅ 考试已添加: [{new_id}] {course} {etype} ({edate})")


def exam_list():
    sem = _cs(); data = sorted(_r(_ef(sem)), key=lambda x: x["date"])
    if not data:
        print("📭 暂无考试"); return
    print(f"\n📅 考试 ({len(data)}场)")
    for e in data:
        days = (_parse_date(e["date"]) - _today()).days
        icon = "🔴" if days <= 3 else ("🟡" if days <= 14 else "🟢")
        if days < 0:
            icon = "⚫"
        print(f"  [{e['id']}] {icon} {e['course']} {e['type']}: {e['date']} (剩{days}天)")


def exam_countdown():
    sem = _cs()
    data = sorted([e for e in _r(_ef(sem)) if _parse_date(e["date"]) >= _today()], key=lambda x: x["date"])
    if not data:
        print("📭 暂无未来考试"); return
    print("\n⏰ 考试倒计时")
    for e in data:
        days = (_parse_date(e["date"]) - _today()).days
        bar = "▓" * min(days, 30) + "░" * max(30 - days, 0)
        print(f"\n  {e['course']} {e['type']}")
        print(f"  {e['date']} 剩{days}天")
        print(f"  [{bar}]")


# ── 学期 ──
def semester_new(name):
    _sc(name); _sd(name).mkdir(parents=True, exist_ok=True)
    # 新学期初始化空数据
    sem = _cs()
    if not _r(_lf(sem)):
        _w(_lf(sem), [
            {"id": "inbox", "name": "收集箱", "icon": "📥", "color": "#667eea"},
            {"id": "work", "name": "学习", "icon": "📚", "color": "#52c41a"},
            {"id": "personal", "name": "生活", "icon": "🏠", "color": "#faad14"},
            {"id": "project", "name": "项目", "icon": "🚀", "color": "#f5222d"},
        ])
    print(f"✅ 已创建并切换到学期: {name}")


def semester_switch(name):
    if not (_sd(name).exists()):
        print(f"❌ 学期不存在: {name}（先用 semester new 创建）"); return
    _sc(name)
    print(f"✅ 已切换到学期: {name}")


def semester_list():
    d = BASE / "semesters"
    if not d.exists():
        print("📭 暂无学期"); return
    cur = _cs()
    print("\n📚 学期列表")
    for sd in sorted(d.iterdir()):
        if sd.is_dir():
            mark = "👉" if sd.name == cur else "  "
            print(f"  {mark} {sd.name}")


# ── CLI ──
def main():
    p = argparse.ArgumentParser(
        description="🎓 大学日程计划 v3.0 — 非交互式参数驱动（AI 可直接调用）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
优先级统一: 1=高🔴 2=中🟡 3=低🟢 0=无⚪
示例:
  python engine.py init
  python engine.py today
  python engine.py task add --title "背单词" --priority 1 --due 2026-07-25 --tags 英语,每日
  python engine.py task list
  python engine.py habit checkin h1
  python engine.py pomodoro log --duration 25 --task "背单词"
        """)
    sp = p.add_subparsers(dest="cmd")

    sp.add_parser("init", help="初始化示例数据")
    sp.add_parser("today", help="今日概览")
    sp.add_parser("eisenhower", help="四象限视图")
    sp.add_parser("export", help="导出全部数据为 JSON")

    # task
    tp = sp.add_parser("task", help="任务管理")
    ts = tp.add_subparsers(dest="sub")
    ta = ts.add_parser("add", help="添加任务（参数式）")
    ta.add_argument("--title", required=True, help="任务标题")
    ta.add_argument("--list", "-l", default="inbox", help="清单ID (默认inbox)")
    ta.add_argument("--priority", "-p", type=int, default=2, choices=[0, 1, 2, 3], help="优先级 1=高 2=中 3=低 0=无")
    ta.add_argument("--due", help="截止日期 YYYY-MM-DD")
    ta.add_argument("--reminder", help="提醒时间 YYYY-MM-DDTHH:MM")
    ta.add_argument("--tags", help="标签,逗号分隔")
    ta.add_argument("--repeat", choices=["daily", "weekly", "monthly", "yearly"], help="重复")
    ta.add_argument("--eisenhower", choices=["important-urgent", "important-not-urgent",
                     "not-important-urgent", "not-important-not-urgent"], help="四象限")
    ta.add_argument("--note", help="备注")
    ta.add_argument("--subtasks", help="子任务,用 | 分隔")
    tl = ts.add_parser("list", help="任务列表")
    tl.add_argument("--list", "-l", help="按清单筛选")
    tl.add_argument("--all", action="store_true", help="含已完成")
    tl.add_argument("--filter", "-f", help="按关键词筛选")
    td = ts.add_parser("done", help="完成任务"); td.add_argument("id")
    tdel = ts.add_parser("delete", help="删除任务"); tdel.add_argument("id")
    tsd = ts.add_parser("subtask", help="标记子任务完成")
    tsd.add_argument("task_id"); tsd.add_argument("index", type=int)

    # list (清单)
    lp = sp.add_parser("list", help="清单管理")
    ls = lp.add_subparsers(dest="sub")
    la = ls.add_parser("add", help="添加清单")
    la.add_argument("--name", required=True)
    la.add_argument("--id")
    la.add_argument("--icon", default="📋")
    la.add_argument("--color", default="#667eea")
    ls.add_parser("show", help="查看清单")

    # habit
    hp = sp.add_parser("habit", help="习惯打卡")
    hs = hp.add_subparsers(dest="sub")
    ha = hs.add_parser("add", help="添加习惯")
    ha.add_argument("--name", required=True)
    ha.add_argument("--icon", default="✅")
    ha.add_argument("--goal", default="daily", choices=["daily", "weekly_3", "weekly_5", "monthly"])
    hl = hs.add_parser("checkin", help="打卡"); hl.add_argument("id")
    hs.add_parser("list", help="习惯列表")

    # pomodoro
    pp = sp.add_parser("pomodoro", help="番茄专注")
    ps = pp.add_subparsers(dest="sub")
    plo = ps.add_parser("log", help="记录已完成的番茄钟（不阻塞）")
    plo.add_argument("--duration", type=int, default=25, help="时长(分钟)")
    plo.add_argument("--task", help="关联任务标题")
    ps.add_parser("stats", help="番茄统计")

    # countdown
    cp = sp.add_parser("countdown", help="倒数日")
    cs = cp.add_subparsers(dest="sub")
    ca = cs.add_parser("add", help="添加倒数日")
    ca.add_argument("--title", required=True)
    ca.add_argument("--date", required=True, help="YYYY-MM-DD")
    ca.add_argument("--type", default="other", choices=["exam", "vacation", "personal", "other"])
    ca.add_argument("--repeat", default="none", choices=["none", "yearly"])
    cs.add_parser("list", help="倒数日列表")

    # filter
    fp = sp.add_parser("filter", help="智能过滤器")
    fp.add_argument("--type", default="today", choices=["today", "7days", "high", "tag"])
    fp.add_argument("--tag", help="标签名 (type=tag 时必填)")

    # schedule
    scp = sp.add_parser("schedule", help="课表")
    scs = scp.add_subparsers(dest="sub")
    si = scs.add_parser("import", help="导入课表"); si.add_argument("file")
    scs.add_parser("show", help="查看课表")
    scs.add_parser("today", help="今日课程")

    # homework
    hwp = sp.add_parser("homework", help="作业")
    hws = hwp.add_subparsers(dest="sub")
    hwa = hws.add_parser("add", help="添加作业")
    hwa.add_argument("--course", required=True)
    hwa.add_argument("--title", required=True)
    hwa.add_argument("--deadline", required=True, help="YYYY-MM-DD")
    hwa.add_argument("--note", default="")
    hws.add_parser("list", help="作业列表")
    hwd = hws.add_parser("done", help="完成作业"); hwd.add_argument("id", type=int)

    # exam
    exp = sp.add_parser("exam", help="考试")
    exs = exp.add_subparsers(dest="sub")
    exa = exs.add_parser("add", help="添加考试")
    exa.add_argument("--course", required=True)
    exa.add_argument("--type", required=True, help="如期中/期末")
    exa.add_argument("--date", required=True, help="YYYY-MM-DD")
    exa.add_argument("--location", default="")
    exa.add_argument("--note", default="")
    exs.add_parser("list", help="考试列表")
    exs.add_parser("countdown", help="考试倒计时")

    # semester
    sep = sp.add_parser("semester", help="学期管理")
    ses = sep.add_subparsers(dest="sub")
    sn = ses.add_parser("new", help="新建学期"); sn.add_argument("name")
    sw = ses.add_parser("switch", help="切换学期"); sw.add_argument("name")
    ses.add_parser("list", help="学期列表")

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return

    if args.cmd == "init":
        init()
    elif args.cmd == "today":
        today_overview()
    elif args.cmd == "eisenhower":
        eisenhower_view()
    elif args.cmd == "export":
        export_all_json()
    elif args.cmd == "task":
        if args.sub == "add":
            task_add(args.title, list_id=args.list, priority=args.priority,
                     due=args.due, reminder=args.reminder, tags=args.tags,
                     repeat=args.repeat, eisenhower=args.eisenhower,
                     note=args.note, subtasks=args.subtasks)
        elif args.sub == "list":
            task_list(list_id=args.list, show_done=args.all, filter_str=args.filter)
        elif args.sub == "done":
            task_done(args.id)
        elif args.sub == "delete":
            task_delete(args.id)
        elif args.sub == "subtask":
            task_subtask_done(args.task_id, args.index)
        else:
            tp.print_help()
    elif args.cmd == "list":
        if args.sub == "add":
            list_add(args.name, lid=args.id, icon=args.icon, color=args.color)
        elif args.sub == "show":
            list_show()
        else:
            lp.print_help()
    elif args.cmd == "habit":
        if args.sub == "add":
            habit_add(args.name, icon=args.icon, goal=args.goal)
        elif args.sub == "checkin":
            habit_checkin(args.id)
        elif args.sub == "list":
            habit_list()
        else:
            hp.print_help()
    elif args.cmd == "pomodoro":
        if args.sub == "log":
            pomodoro_log(duration=args.duration, task=args.task)
        elif args.sub == "stats":
            pomodoro_stats()
        else:
            pp.print_help()
    elif args.cmd == "countdown":
        if args.sub == "add":
            countdown_add(args.title, args.date, tp=args.type, repeat=args.repeat)
        elif args.sub == "list":
            countdown_list()
        else:
            cp.print_help()
    elif args.cmd == "filter":
        filter_view(filter_type=args.type, tag=args.tag)
    elif args.cmd == "schedule":
        if args.sub == "import":
            schedule_import(args.file)
        elif args.sub == "show":
            schedule_show()
        elif args.sub == "today":
            schedule_today()
        else:
            scp.print_help()
    elif args.cmd == "homework":
        if args.sub == "add":
            homework_add(args.course, args.title, args.deadline, note=args.note)
        elif args.sub == "list":
            homework_list()
        elif args.sub == "done":
            homework_done(args.id)
        else:
            hwp.print_help()
    elif args.cmd == "exam":
        if args.sub == "add":
            exam_add(args.course, args.type, args.date, location=args.location, note=args.note)
        elif args.sub == "list":
            exam_list()
        elif args.sub == "countdown":
            exam_countdown()
        else:
            exp.print_help()
    elif args.cmd == "semester":
        if args.sub == "new":
            semester_new(args.name)
        elif args.sub == "switch":
            semester_switch(args.name)
        elif args.sub == "list":
            semester_list()
        else:
            sep.print_help()


if __name__ == "__main__":
    main()
