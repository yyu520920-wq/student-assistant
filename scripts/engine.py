#!/usr/bin/env python3
"""
大学日程计划 v1.3 — 原创设计的大学生日程与学习管理工具（非交互式重构版）
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
# 学术模块（全局，不按学期）
def _ref_f(): return BASE / "references.json"
def _ol_f(): return BASE / "outlines.json"


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


def schedule_add(course, day, time, teacher="", location="", weeks="1-16"):
    """添加单门课到课表（不覆盖，追加）"""
    sem = _cs(); data = _r(_sf(sem))
    data.append({"day": day, "time": time, "course": course,
                 "teacher": teacher, "location": location, "weeks": weeks})
    _w(_sf(sem), data)
    print(f"✅ 已添加: {WEEKDAYS[day-1]} {time} {course} {teacher} @ {location} (第{weeks}周)")


def schedule_clear():
    """清空当前学期课表"""
    sem = _cs(); _w(_sf(sem), [])
    print(f"✅ 课表已清空（学期: {sem}）")


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


# ══ 学术模块 ══

REF_TYPES = {"journal": "期刊论文[J]", "conference": "会议论文[C]",
             "book": "图书[M]", "thesis": "学位论文[D]", "web": "网页[EB/OL]"}

OUTLINE_TEMPLATES = {
    "review": {
        "name": "文献综述",
        "sections": [
            "一、引言（研究背景与意义）",
            "二、核心概念界定",
            "三、文献综述",
            "  3.1 理论基础研究",
            "  3.2 研究方法综述",
            "  3.3 研究成果综述",
            "四、研究现状评析",
            "五、存在的问题与不足",
            "六、未来研究方向",
            "七、结论",
            "参考文献",
        ],
    },
    "empirical": {
        "name": "实证研究",
        "sections": [
            "一、引言",
            "  1.1 研究背景",
            "  1.2 研究问题与意义",
            "二、文献回顾与研究假设",
            "  2.1 文献回顾",
            "  2.2 研究假设",
            "三、研究方法",
            "  3.1 研究设计",
            "  3.2 数据来源与样本",
            "  3.3 变量定义",
            "  3.4 模型构建",
            "四、实证结果与分析",
            "  4.1 描述性统计",
            "  4.2 相关性分析",
            "  4.3 回归分析",
            "  4.4 稳健性检验",
            "五、结论与政策建议",
            "参考文献",
        ],
    },
    "case": {
        "name": "案例研究",
        "sections": [
            "一、引言",
            "  1.1 研究背景",
            "  1.2 案例选择依据",
            "二、案例背景介绍",
            "  2.1 案例概况",
            "  2.2 发展历程",
            "三、案例分析",
            "  3.1 分析框架",
            "  3.2 案例剖析",
            "四、问题发现与讨论",
            "五、解决方案与建议",
            "六、经验总结与启示",
            "参考文献",
        ],
    },
    "experiment": {
        "name": "实验研究",
        "sections": [
            "一、引言",
            "  1.1 研究背景与问题",
            "  1.2 研究意义",
            "二、文献回顾",
            "  2.1 理论基础",
            "  2.2 相关研究",
            "  2.3 研究假设",
            "三、实验方法",
            "  3.1 实验设计",
            "  3.2 实验材料与设备",
            "  3.3 实验流程",
            "  3.4 数据采集与处理",
            "四、实验结果",
            "  4.1 结果呈现",
            "  4.2 数据分析",
            "五、讨论",
            "  5.1 结果解释",
            "  5.2 与已有研究对比",
            "  5.3 局限性",
            "六、结论",
            "参考文献",
        ],
    },
}


def _tokenize(text):
    """简单分词：中文字符按字，英文按词"""
    import re
    return re.findall(r"[\u4e00-\u9fff]|[a-zA-Z]+|[0-9]+", text.lower())


def _ngrams(tokens, n):
    return set(tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def format_citation(ref, fmt="gbt"):
    """将文献对象格式化为引用字符串（支持 GB/T 7714、APA、MLA）"""
    authors = ref.get("authors", [])
    title = ref.get("title", "")
    year = ref.get("year", "")
    rtype = ref.get("type", "journal")

    if fmt == "gbt":
        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += ", 等"
        tag = {"journal": "J", "conference": "C", "book": "M", "thesis": "D", "web": "EB/OL"}.get(rtype, "J")
        if rtype == "journal":
            j = ref.get("journal", "")
            v = ref.get("volume", "")
            i = ref.get("issue", "")
            p = ref.get("pages", "")
            return f"{author_str}. {title}[{tag}]. {j}, {year}, {v}({i}): {p}."
        elif rtype == "conference":
            c = ref.get("journal", "")
            loc = ref.get("location", "")
            pub = ref.get("publisher", "")
            p = ref.get("pages", "")
            return f"{author_str}. {title}[C]//{c}. {loc}: {pub}, {year}: {p}."
        elif rtype == "book":
            pub = ref.get("publisher", "")
            loc = ref.get("location", "")
            return f"{author_str}. {title}[M]. {loc}: {pub}, {year}."
        elif rtype == "thesis":
            school = ref.get("publisher", "")
            return f"{author_str}. {title}[D]. {school}, {year}."
        else:
            url = ref.get("url", "")
            return f"{author_str}. {title}[EB/OL]. ({year}). {url}."

    elif fmt == "apa":
        author_str = ", ".join(authors) if authors else ""
        if rtype == "journal":
            j = ref.get("journal", "")
            v = ref.get("volume", "")
            i = ref.get("issue", "")
            p = ref.get("pages", "")
            i_str = f"({i})" if i else ""
            return f"{author_str} ({year}). {title}. {j}, {v}{i_str}, {p}."
        elif rtype == "book":
            pub = ref.get("publisher", "")
            return f"{author_str} ({year}). {title}. {pub}."
        else:
            return f"{author_str} ({year}). {title}."

    elif fmt == "mla":
        author_str = ", ".join(authors) if authors else ""
        if rtype == "journal":
            j = ref.get("journal", "")
            v = ref.get("volume", "")
            i = ref.get("issue", "")
            p = ref.get("pages", "")
            return f'{author_str}. "{title}." {j}, vol. {v}, no. {i}, {year}, pp. {p}.'
        elif rtype == "book":
            pub = ref.get("publisher", "")
            return f"{author_str}. {title}. {pub}, {year}."
        else:
            return f'{author_str}. "{title}." {year}.'


def ref_add(title, authors, rtype="journal", journal="", year="", volume="",
            issue="", pages="", doi="", publisher="", location="", url="", tags="", note=""):
    data = _r(_ref_f())
    rid = f"ref{len(data) + 1:03d}"
    author_list = [a.strip() for a in authors.split(",") if a.strip()] if isinstance(authors, str) else authors
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    ref = {
        "id": rid, "type": rtype, "title": title, "authors": author_list,
        "journal": journal, "year": year, "volume": volume, "issue": issue,
        "pages": pages, "doi": doi, "publisher": publisher, "location": location,
        "url": url, "tags": tag_list, "note": note, "created": _now(),
    }
    data.append(ref)
    _w(_ref_f(), data)
    print(f"✅ 文献已添加: [{rid}] {title}")
    print(f"   格式预览(GB/T 7714): {format_citation(ref, 'gbt')}")


def ref_list(tag=None):
    data = _r(_ref_f())
    if tag:
        data = [r for r in data if tag in r.get("tags", [])]
    if not data:
        print("📭 暂无文献记录"); return
    print(f"\n📚 文献库 ({len(data)}条)")
    for r in data:
        authors = ", ".join(r.get("authors", [])[:2])
        if len(r.get("authors", [])) > 2:
            authors += " 等"
        print(f"  [{r['id']}] {authors} ({r.get('year','')}) {r['title']}")
        if r.get("journal"):
            print(f"       来源: {r['journal']}")


def ref_delete(rid):
    data = _r(_ref_f())
    new = [r for r in data if r["id"] != rid]
    if len(new) == len(data):
        print(f"❌ 未找到文献: {rid}"); return
    _w(_ref_f(), new)
    print(f"✅ 已删除文献: {rid}")


def ref_cite(rid, fmt="gbt"):
    data = _r(_ref_f())
    ref = next((r for r in data if r["id"] == rid), None)
    if not ref:
        print(f"❌ 未找到文献: {rid}"); return
    fmt_name = {"gbt": "GB/T 7714", "apa": "APA", "mla": "MLA"}.get(fmt, fmt.upper())
    print(f"\n📄 引用格式 ({fmt_name})")
    print(f"   {format_citation(ref, fmt)}")


def outline_generate(topic, otype="review"):
    tpl = OUTLINE_TEMPLATES.get(otype)
    if not tpl:
        print(f"❌ 未知论文类型: {otype}（可选: review/empirical/case/experiment）"); return
    data = _r(_ol_f())
    oid = f"ol{len(data) + 1:03d}"
    outline = {
        "id": oid, "topic": topic, "type": otype, "type_name": tpl["name"],
        "sections": tpl["sections"], "created": _now(),
    }
    data.append(outline)
    _w(_ol_f(), data)
    print(f"✅ 论文大纲已生成: [{oid}]")
    print(f"   主题: {topic}")
    print(f"   类型: {tpl['name']}")
    print(f"\n📋 大纲结构:")
    for s in tpl["sections"]:
        print(f"   {s}")


def outline_list():
    data = _r(_ol_f())
    if not data:
        print("📭 暂无大纲记录"); return
    print(f"\n📋 论文大纲 ({len(data)}条)")
    for o in data:
        print(f"  [{o['id']}] {o['topic']} ({o.get('type_name','')})")


def plagiarism_check(text1, text2, n=3):
    """n-gram Jaccard 相似度检测"""
    t1 = _tokenize(text1)
    t2 = _tokenize(text2)
    g1 = _ngrams(t1, n)
    g2 = _ngrams(t2, n)
    if not g1 or not g2:
        print("⚠️ 文本太短，无法进行有效检测"); return
    inter = g1 & g2
    union = g1 | g2
    sim = len(inter) / len(union)
    pct = round(sim * 100, 1)
    print(f"\n🔍 查重预检结果")
    print(f"   相似度: {pct}%")
    print(f"   重复片段数: {len(inter)}")
    print(f"   总独立片段数: {len(union)}")
    if pct < 10:
        print(f"   评估: ✅ 相似度极低，基本无重复")
    elif pct < 25:
        print(f"   评估: 🟢 相似度较低，可接受")
    elif pct < 50:
        print(f"   评估: 🟡 相似度中等，建议修改")
    else:
        print(f"   评估: 🔴 相似度较高，需重点修改")
    if inter:
        print(f"\n   重复片段示例（前5个）:")
        for i, ng in enumerate(sorted(inter)[:5]):
            phrase = "".join(ng) if any("\u4e00" <= c <= "\u9fff" for c in "".join(ng)) else " ".join(ng)
            print(f"     {i+1}. {phrase}")



def main():
    p = argparse.ArgumentParser(
        description="🎓 大学日程计划 v1.3 — 非交互式参数驱动（AI 可直接调用）",
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
    si = scs.add_parser("import", help="导入课表(覆盖)"); si.add_argument("file")
    sca = scs.add_parser("add", help="添加单门课(追加)")
    sca.add_argument("--course", required=True, help="课程名")
    sca.add_argument("--day", type=int, required=True, help="星期几 1=周一 7=周日")
    sca.add_argument("--time", required=True, help="时间 如 08:00-09:40")
    sca.add_argument("--teacher", default="", help="教师")
    sca.add_argument("--location", default="", help="地点")
    sca.add_argument("--weeks", default="1-16", help="周次 如 1-16")
    scs.add_parser("clear", help="清空课表")
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

    # ref（文献管理）
    rp = sp.add_parser("ref", help="文献管理")
    rs = rp.add_subparsers(dest="sub")
    ra = rs.add_parser("add", help="添加文献")
    ra.add_argument("--title", required=True)
    ra.add_argument("--authors", required=True, help="作者，逗号分隔")
    ra.add_argument("--type", default="journal", choices=list(REF_TYPES.keys()))
    ra.add_argument("--journal", default="", help="期刊/会议名")
    ra.add_argument("--year", default="")
    ra.add_argument("--volume", default="")
    ra.add_argument("--issue", default="")
    ra.add_argument("--pages", default="")
    ra.add_argument("--doi", default="")
    ra.add_argument("--publisher", default="")
    ra.add_argument("--location", default="")
    ra.add_argument("--url", default="")
    ra.add_argument("--tags", default="", help="标签，逗号分隔")
    ra.add_argument("--note", default="")
    rl = rs.add_parser("list", help="文献列表"); rl.add_argument("--tag", default=None)
    rd = rs.add_parser("delete", help="删除文献"); rd.add_argument("id")
    rc = rs.add_parser("cite", help="生成引用格式")
    rc.add_argument("id"); rc.add_argument("--format", default="gbt", choices=["gbt", "apa", "mla"])

    # outline（论文大纲）
    op = sp.add_parser("outline", help="论文大纲生成")
    os_ = op.add_subparsers(dest="sub")
    og = os_.add_parser("generate", help="生成大纲")
    og.add_argument("--topic", required=True)
    og.add_argument("--type", default="review", choices=list(OUTLINE_TEMPLATES.keys()))
    os_.add_parser("list", help="大纲列表")

    # plagiarism（查重预检）
    plp = sp.add_parser("plagiarism", help="查重预检")
    plp.add_argument("--text1", required=True, help="文本1")
    plp.add_argument("--text2", required=True, help="文本2")
    plp.add_argument("--n", type=int, default=3, help="n-gram长度（默认3）")

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
        elif args.sub == "add":
            schedule_add(args.course, args.day, args.time,
                         teacher=args.teacher, location=args.location, weeks=args.weeks)
        elif args.sub == "clear":
            schedule_clear()
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

    elif args.cmd == "ref":
        if args.sub == "add":
            ref_add(args.title, args.authors, args.type, args.journal, args.year,
                    args.volume, args.issue, args.pages, args.doi, args.publisher,
                    args.location, args.url, args.tags, args.note)
        elif args.sub == "list":
            ref_list(args.tag)
        elif args.sub == "delete":
            ref_delete(args.id)
        elif args.sub == "cite":
            ref_cite(args.id, args.format)
        else:
            rp.print_help()

    elif args.cmd == "outline":
        if args.sub == "generate":
            outline_generate(args.topic, args.type)
        elif args.sub == "list":
            outline_list()
        else:
            op.print_help()

    elif args.cmd == "plagiarism":
        plagiarism_check(args.text1, args.text2, args.n)


if __name__ == "__main__":
    main()
