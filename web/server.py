#!/usr/bin/env python3
"""
学生助手 v1.1 — Web API Server
基于滴答清单深度定制
"""

import json, os, sys, uuid
from datetime import datetime, date, timedelta
from pathlib import Path

# 把 scripts 目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from engine import (
    BASE, CUR, WEEKDAYS,
    _d, _r, _w, _sd, _cs, _sc, _now, _today, _parse_date,
    _tf, _lf, _hbf, _pf, _cdf, _sf, _hf, _ef, _df, _gf, _rf, _prf, _wf, _plf
)

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ── 辅助 ──
def sem(): return _cs()

# ── 首页 ──
@app.route("/")
def index():
    return render_template("index.html")

# ── API: 今日概览 ──
@app.route("/api/today")
def api_today():
    s = sem(); t = _today(); dow = t.weekday()
    tasks = _r(_tf(s)); habits = _r(_hbf(s))
    exams = _r(_ef(s)); schedule = _r(_sf(s))

    today_courses = sorted(
        [c for c in schedule if c["day"] == dow + 1],
        key=lambda x: x["time"]
    )

    today_tasks = [
        tk for tk in tasks
        if tk.get("due_date") and _parse_date(tk["due_date"]) <= t and not tk["done"]
    ]

    near_exams = [
        e for e in exams
        if 0 <= (_parse_date(e["date"]) - t).days <= 14
    ]

    return jsonify({
        "date": t.isoformat(),
        "weekday": WEEKDAYS[dow],
        "courses": today_courses,
        "tasks": today_tasks,
        "habits": habits,
        "near_exams": sorted(near_exams, key=lambda x: x["date"])
    })

# ── API: 任务 ──
@app.route("/api/tasks")
def api_tasks():
    s = sem()
    tasks = _r(_tf(s))
    list_id = request.args.get("list_id")
    show_done = request.args.get("show_done", "0") == "1"
    
    if list_id:
        tasks = [t for t in tasks if t["list_id"] == list_id]
    if not show_done:
        tasks = [t for t in tasks if not t["done"]]
    
    tasks.sort(key=lambda t: (t.get("priority", 2) or 2))
    return jsonify(tasks)

@app.route("/api/tasks", methods=["POST"])
def api_task_add():
    s = sem(); data = _r(_tf(s))
    body = request.json
    task = {
        "id": str(uuid.uuid4())[:8],
        "title": body["title"],
        "list_id": body.get("list_id", "inbox"),
        "priority": body.get("priority", 2),
        "due_date": body.get("due_date"),
        "reminder": body.get("reminder"),
        "repeat": body.get("repeat"),
        "eisenhower": body.get("eisenhower"),
        "tags": body.get("tags", []),
        "done": False,
        "subtasks": body.get("subtasks", []),
        "note": body.get("note", ""),
        "created": _now(),
        "completed": None
    }
    data.append(task)
    _w(_tf(s), data)
    return jsonify(task)

@app.route("/api/tasks/<tid>", methods=["PUT"])
def api_task_update(tid):
    s = sem(); data = _r(_tf(s))
    for t in data:
        if t["id"] == tid:
            t.update(request.json)
            _w(_tf(s), data)
            return jsonify(t)
    return jsonify({"error": "not found"}), 404

@app.route("/api/tasks/<tid>", methods=["DELETE"])
def api_task_delete(tid):
    s = sem(); data = _r(_tf(s))
    data = [t for t in data if t["id"] != tid]
    _w(_tf(s), data)
    return jsonify({"ok": True})

@app.route("/api/tasks/<tid>/done", methods=["POST"])
def api_task_done(tid):
    s = sem(); data = _r(_tf(s))
    for t in data:
        if t["id"] == tid:
            t["done"] = True
            t["completed"] = _now()
            _w(_tf(s), data)
            return jsonify(t)
    return jsonify({"error": "not found"}), 404

@app.route("/api/tasks/<tid>/subtask/<int:idx>", methods=["POST"])
def api_subtask_done(tid, idx):
    s = sem(); data = _r(_tf(s))
    for t in data:
        if t["id"] == tid:
            if 0 <= idx < len(t["subtasks"]):
                t["subtasks"][idx]["done"] = True
                _w(_tf(s), data)
                return jsonify(t)
    return jsonify({"error": "not found"}), 404

# ── API: 清单 ──
@app.route("/api/lists")
def api_lists():
    s = sem()
    lists = _r(_lf(s))
    tasks = _r(_tf(s))
    for l in lists:
        l["count"] = sum(1 for t in tasks if t["list_id"] == l["id"] and not t["done"])
    return jsonify(lists)

@app.route("/api/lists", methods=["POST"])
def api_list_add():
    s = sem(); data = _r(_lf(s))
    body = request.json
    lst = {
        "id": body.get("id", body["name"].lower().replace(" ", "_")),
        "name": body["name"],
        "icon": body.get("icon", "📋"),
        "color": body.get("color", "#667eea")
    }
    data.append(lst)
    _w(_lf(s), data)
    return jsonify(lst)

# ── API: 习惯 ──
@app.route("/api/habits")
def api_habits():
    return jsonify(_r(_hbf(sem())))

@app.route("/api/habits", methods=["POST"])
def api_habit_add():
    s = sem(); data = _r(_hbf(s))
    body = request.json
    habit = {
        "id": str(uuid.uuid4())[:8],
        "name": body["name"],
        "icon": body.get("icon", "✅"),
        "goal": body.get("goal", "daily"),
        "streak": 0,
        "total": 0,
        "logs": []
    }
    data.append(habit)
    _w(_hbf(s), data)
    return jsonify(habit)

@app.route("/api/habits/<hid>/checkin", methods=["POST"])
def api_habit_checkin(hid):
    s = sem(); data = _r(_hbf(s)); t = _today().isoformat()
    for h in data:
        if h["id"] == hid:
            if t not in h["logs"]:
                h["logs"].append(t)
                h["total"] += 1
            logs = sorted(set(h["logs"]), reverse=True)
            streak = 0; check = _today()
            for d in logs:
                if d == check.isoformat():
                    streak += 1; check -= timedelta(days=1)
                else: break
            h["streak"] = streak
            _w(_hbf(s), data)
            return jsonify(h)
    return jsonify({"error": "not found"}), 404

# ── API: 倒数日 ──
@app.route("/api/countdowns")
def api_countdowns():
    data = _r(_cdf(sem()))
    t = _today()
    result = []
    for c in sorted(data, key=lambda x: x["date"]):
        days = (_parse_date(c["date"]) - t).days
        c["days"] = days
        result.append(c)
    return jsonify(result)

@app.route("/api/countdowns", methods=["POST"])
def api_countdown_add():
    s = sem(); data = _r(_cdf(s))
    body = request.json
    cd = {
        "id": str(uuid.uuid4())[:8],
        "title": body["title"],
        "date": body["date"],
        "type": body.get("type", "other"),
        "repeat": body.get("repeat", "none")
    }
    data.append(cd)
    _w(_cdf(s), data)
    return jsonify(cd)

# ── API: 课表 ──
@app.route("/api/schedule")
def api_schedule():
    data = _r(_sf(sem()))
    result = {}
    for d in range(1, 8):
        result[WEEKDAYS[d-1]] = sorted(
            [c for c in data if c["day"] == d],
            key=lambda x: x["time"]
        )
    return jsonify(result)

# ── API: 作业 ──
@app.route("/api/homework")
def api_homework():
    data = _r(_hf(sem()))
    t = _today()
    for h in data:
        h["days_left"] = (_parse_date(h["deadline"]) - t).days
    return jsonify(data)

# ── API: 考试 ──
@app.route("/api/exams")
def api_exams():
    data = _r(_ef(sem()))
    t = _today()
    for e in data:
        e["days_left"] = (_parse_date(e["date"]) - t).days
    return jsonify(sorted(data, key=lambda x: x["date"]))

# ── API: 番茄 ──
@app.route("/api/pomodoro")
def api_pomodoro():
    data = _r(_pf(sem()))
    total = sum(d["duration"] for d in data)
    count = len(data)
    today_count = sum(1 for d in data if d["date"] == _today().isoformat())
    return jsonify({
        "total": total,
        "count": count,
        "today_count": today_count,
        "records": data[-20:]
    })

@app.route("/api/pomodoro", methods=["POST"])
def api_pomodoro_add():
    s = sem(); data = _r(_pf(s))
    body = request.json
    record = {
        "date": _today().isoformat(),
        "duration": body["duration"],
        "task": body.get("task", ""),
        "completed": True,
        "time": _now()
    }
    data.append(record)
    _w(_pf(s), data)
    return jsonify(record)

# ── API: 四象限 ──
@app.route("/api/eisenhower")
def api_eisenhower():
    s = sem(); tasks = _r(_tf(s))
    quads = {
        "important-urgent": [],
        "important-not-urgent": [],
        "not-important-urgent": [],
        "not-important-not-urgent": []
    }
    for t in tasks:
        if t["done"]: continue
        q = t.get("eisenhower", "not-important-not-urgent")
        if q in quads: quads[q].append(t)
    return jsonify(quads)

# ── API: 仪表盘数据 ──
@app.route("/api/dashboard")
def api_dashboard():
    s = sem()
    tasks = _r(_tf(s))
    habits = _r(_hbf(s))
    pomodoro = _r(_pf(s))
    exams = _r(_ef(s))
    t = _today()

    total_tasks = len(tasks)
    done_tasks = sum(1 for tk in tasks if tk["done"])
    pending_tasks = total_tasks - done_tasks

    urgent_count = sum(1 for tk in tasks if not tk["done"] and tk.get("due_date") and (_parse_date(tk["due_date"]) - t).days <= 3)

    total_pomo = sum(p["duration"] for p in pomodoro)
    today_pomo = sum(1 for p in pomodoro if p["date"] == t.isoformat())

    habit_streaks = sum(h["streak"] for h in habits)

    near_exams = sum(1 for e in exams if 0 <= (_parse_date(e["date"]) - t).days <= 14)

    # 近7天完成任务趋势
    trend = []
    for i in range(6, -1, -1):
        d = (t - timedelta(days=i)).isoformat()
        trend.append({
            "date": d,
            "done": sum(1 for tk in tasks if tk.get("completed") and tk["completed"].startswith(d)),
            "pomodoro": sum(p["duration"] for p in pomodoro if p["date"] == d)
        })

    return jsonify({
        "stats": {
            "total_tasks": total_tasks,
            "done_tasks": done_tasks,
            "pending_tasks": pending_tasks,
            "urgent_count": urgent_count,
            "total_pomodoro": total_pomo,
            "today_pomodoro": today_pomo,
            "habit_streaks": habit_streaks,
            "near_exams": near_exams
        },
        "trend": trend
    })

# ── API: 学期 ──
@app.route("/api/semesters")
def api_semesters():
    d = BASE / "semesters"
    if not d.exists(): return jsonify(["默认学期"])
    current = _cs()
    result = []
    for sd in sorted(d.iterdir()):
        if sd.is_dir():
            result.append({"name": sd.name, "current": sd.name == current})
    return jsonify(result)

@app.route("/api/semesters/switch", methods=["POST"])
def api_semester_switch():
    name = request.json["name"]
    _sc(name)
    _sd(name).mkdir(parents=True, exist_ok=True)
    return jsonify({"ok": True, "semester": name})

# ── API: 导出 ──
@app.route("/api/export")
def api_export():
    s = sem(); sd = _sd(s)
    all_data = {
        "semester": s,
        "exported": _now(),
        "tasks": _r(_tf(s)),
        "lists": _r(_lf(s)),
        "habits": _r(_hbf(s)),
        "pomodoro": _r(_pf(s)),
        "countdowns": _r(_cdf(s)),
        "schedule": _r(_sf(s)),
        "homework": _r(_hf(s)),
        "exams": _r(_ef(s))
    }
    return jsonify(all_data)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--host", default="0.0.0.0")
    args = p.parse_args()
    print(f"🎓 学生助手 Web 服务启动: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)
