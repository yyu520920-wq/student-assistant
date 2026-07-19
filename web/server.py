#!/usr/bin/env python3
"""
大学日程计划 v1.3 — Web API Server（零依赖，纯标准库）
基于 http.server 实现，无需 Flask，下载即用。
"""

import json, os, sys, uuid, socket, webbrowser
from datetime import datetime, date, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 把 scripts 目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from engine import (
    BASE, CUR, WEEKDAYS,
    _d, _r, _w, _sd, _cs, _sc, _now, _today, _parse_date,
    _tf, _lf, _hbf, _pf, _cdf, _sf, _hf, _ef, _df, _gf, _rf, _prf, _wf, _plf
)

APP_HTML = Path(__file__).parent / "app.html"


def sem():
    return _cs()


def get_lan_ip():
    """获取本机局域网 IP，方便手机访问"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ── API 逻辑 ──

def api_today():
    s = sem(); t = _today(); dow = t.weekday()
    tasks = _r(_tf(s)); habits = _r(_hbf(s))
    exams = _r(_ef(s)); schedule = _r(_sf(s))
    homework = _r(_hf(s))

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
        if 0 <= (_parse_date(e["date"]) - t).days <= 30
    ]
    near_homework = [
        h for h in homework
        if not h["done"] and (_parse_date(h["deadline"]) - t).days >= 0
    ]
    return {
        "date": t.isoformat(), "weekday": WEEKDAYS[dow],
        "courses": today_courses, "tasks": today_tasks,
        "habits": habits, "near_exams": sorted(near_exams, key=lambda x: x["date"]),
        "homework": sorted(near_homework, key=lambda x: x["deadline"]),
    }


def api_tasks(query):
    s = sem(); tasks = _r(_tf(s))
    list_id = query.get("list_id", [None])[0]
    show_done = query.get("show_done", ["0"])[0] == "1"
    if list_id:
        tasks = [t for t in tasks if t["list_id"] == list_id]
    if not show_done:
        tasks = [t for t in tasks if not t["done"]]
    tasks.sort(key=lambda t: (t.get("priority", 2) or 2))
    return tasks


def api_task_add(body):
    s = sem(); data = _r(_tf(s))
    task = {
        "id": str(uuid.uuid4())[:8], "title": body.get("title", ""),
        "list_id": body.get("list_id", "inbox"),
        "priority": body.get("priority", 2),
        "due_date": body.get("due_date"), "reminder": body.get("reminder"),
        "repeat": body.get("repeat"), "eisenhower": body.get("eisenhower"),
        "tags": body.get("tags", []),
        "done": False, "subtasks": body.get("subtasks", []),
        "note": body.get("note", ""), "created": _now(), "completed": None,
    }
    data.append(task); _w(_tf(s), data)
    return task


def api_task_update(tid, body):
    s = sem(); data = _r(_tf(s))
    for t in data:
        if t["id"] == tid:
            t.update(body); _w(_tf(s), data); return t
    return {"error": "not found"}


def api_task_delete(tid):
    s = sem(); data = _r(_tf(s))
    data = [t for t in data if t["id"] != tid]; _w(_tf(s), data)
    return {"ok": True}


def api_task_done(tid):
    s = sem(); data = _r(_tf(s))
    for t in data:
        if t["id"] == tid:
            t["done"] = True; t["completed"] = _now()
            _w(_tf(s), data); return t
    return {"error": "not found"}


def api_subtask_done(tid, idx):
    s = sem(); data = _r(_tf(s))
    for t in data:
        if t["id"] == tid:
            if 0 <= idx < len(t["subtasks"]):
                t["subtasks"][idx]["done"] = True
                _w(_tf(s), data); return t
    return {"error": "not found"}


def api_lists():
    s = sem(); lists = _r(_lf(s)); tasks = _r(_tf(s))
    for l in lists:
        l["count"] = sum(1 for t in tasks if t["list_id"] == l["id"] and not t["done"])
    return lists


def api_list_add(body):
    s = sem(); data = _r(_lf(s))
    lst = {
        "id": body.get("id", body.get("name", "").lower().replace(" ", "_")),
        "name": body.get("name", ""), "icon": body.get("icon", "📋"),
        "color": body.get("color", "#667eea"),
    }
    data.append(lst); _w(_lf(s), data); return lst


def api_habits():
    return _r(_hbf(sem()))


def api_habit_add(body):
    s = sem(); data = _r(_hbf(s))
    habit = {
        "id": str(uuid.uuid4())[:8], "name": body.get("name", ""),
        "icon": body.get("icon", "✅"), "goal": body.get("goal", "daily"),
        "streak": 0, "total": 0, "logs": [],
    }
    data.append(habit); _w(_hbf(s), data); return habit


def api_habit_checkin(hid):
    s = sem(); data = _r(_hbf(s)); t = _today().isoformat()
    for h in data:
        if h["id"] == hid:
            if t not in h["logs"]:
                h["logs"].append(t); h["total"] += 1
            logs = sorted(set(h["logs"]), reverse=True); streak = 0; check = _today()
            for d in logs:
                if d == check.isoformat():
                    streak += 1; check -= timedelta(days=1)
                else:
                    break
            h["streak"] = streak; _w(_hbf(s), data); return h
    return {"error": "not found"}


def api_countdowns():
    data = _r(_cdf(sem())); t = _today(); result = []
    for c in sorted(data, key=lambda x: x["date"]):
        c["days"] = (_parse_date(c["date"]) - t).days; result.append(c)
    return result


def api_countdown_add(body):
    s = sem(); data = _r(_cdf(s))
    cd = {
        "id": str(uuid.uuid4())[:8], "title": body.get("title", ""),
        "date": body.get("date", ""), "type": body.get("type", "other"),
        "repeat": body.get("repeat", "none"),
    }
    data.append(cd); _w(_cdf(s), data); return cd


def api_schedule():
    data = _r(_sf(sem())); result = {}
    for d in range(1, 8):
        result[WEEKDAYS[d - 1]] = sorted(
            [c for c in data if c["day"] == d], key=lambda x: x["time"]
        )
    return result


def api_homework():
    data = _r(_hf(sem())); t = _today()
    for h in data:
        h["days_left"] = (_parse_date(h["deadline"]) - t).days
    return data


def api_homework_add(body):
    s = sem(); data = _r(_hf(s))
    new_id = max([h.get("id", 0) for h in data], default=0) + 1
    hw = {
        "id": new_id, "course": body.get("course", ""), "title": body.get("title", ""),
        "deadline": body.get("deadline", ""), "done": False, "note": body.get("note", ""),
    }
    data.append(hw); _w(_hf(s), data); return hw


def api_homework_done(hid):
    s = sem(); data = _r(_hf(s))
    for h in data:
        if h["id"] == hid:
            h["done"] = True; _w(_hf(s), data); return h
    return {"error": "not found"}


def api_exams():
    data = _r(_ef(sem())); t = _today()
    for e in data:
        e["days_left"] = (_parse_date(e["date"]) - t).days
    return sorted(data, key=lambda x: x["date"])


def api_exam_add(body):
    s = sem(); data = _r(_ef(s))
    new_id = max([e.get("id", 0) for e in data], default=0) + 1
    ex = {
        "id": new_id, "course": body.get("course", ""), "type": body.get("type", ""),
        "date": body.get("date", ""), "location": body.get("location", ""),
        "note": body.get("note", ""),
    }
    data.append(ex); _w(_ef(s), data); return ex


def api_pomodoro():
    data = _r(_pf(sem()))
    total = sum(d["duration"] for d in data); count = len(data)
    today_count = sum(1 for d in data if d["date"] == _today().isoformat())
    return {"total": total, "count": count, "today_count": today_count, "records": data[-30:]}


def api_pomodoro_add(body):
    s = sem(); data = _r(_pf(s))
    record = {
        "date": _today().isoformat(), "duration": body.get("duration", 25),
        "task": body.get("task", ""), "completed": True, "time": _now(),
    }
    data.append(record); _w(_pf(s), data); return record


def api_eisenhower():
    s = sem(); tasks = _r(_tf(s))
    quads = {
        "important-urgent": [], "important-not-urgent": [],
        "not-important-urgent": [], "not-important-not-urgent": [],
    }
    for t in tasks:
        if t["done"]:
            continue
        q = t.get("eisenhower", "not-important-not-urgent")
        if q in quads:
            quads[q].append(t)
    return quads


def api_dashboard():
    s = sem()
    tasks = _r(_tf(s)); habits = _r(_hbf(s))
    pomodoro = _r(_pf(s)); exams = _r(_ef(s))
    t = _today()
    total_tasks = len(tasks)
    done_tasks = sum(1 for tk in tasks if tk["done"])
    pending_tasks = total_tasks - done_tasks
    urgent_count = sum(1 for tk in tasks if not tk["done"] and tk.get("due_date")
                       and (_parse_date(tk["due_date"]) - t).days <= 3)
    total_pomo = sum(p["duration"] for p in pomodoro)
    today_pomo = sum(1 for p in pomodoro if p["date"] == t.isoformat())
    habit_streaks = sum(h["streak"] for h in habits)
    near_exams = sum(1 for e in exams if 0 <= (_parse_date(e["date"]) - t).days <= 30)
    trend = []
    for i in range(6, -1, -1):
        d = (t - timedelta(days=i)).isoformat()
        trend.append({
            "date": d,
            "done": sum(1 for tk in tasks if tk.get("completed") and tk["completed"].startswith(d)),
            "pomodoro": sum(p["duration"] for p in pomodoro if p["date"] == d),
        })
    return {
        "stats": {
            "total_tasks": total_tasks, "done_tasks": done_tasks,
            "pending_tasks": pending_tasks, "urgent_count": urgent_count,
            "total_pomodoro": total_pomo, "today_pomodoro": today_pomo,
            "habit_streaks": habit_streaks, "near_exams": near_exams,
        },
        "trend": trend,
    }


def api_semesters():
    d = BASE / "semesters"
    if not d.exists():
        return [{"name": "默认学期", "current": True}]
    current = _cs(); result = []
    for sd in sorted(d.iterdir()):
        if sd.is_dir():
            result.append({"name": sd.name, "current": sd.name == current})
    return result


def api_semester_switch(body):
    name = body.get("name", "默认学期")
    _sc(name); _sd(name).mkdir(parents=True, exist_ok=True)
    return {"ok": True, "semester": name}


def api_export():
    s = sem()
    return {
        "semester": s, "exported": _now(),
        "tasks": _r(_tf(s)), "lists": _r(_lf(s)), "habits": _r(_hbf(s)),
        "pomodoro": _r(_pf(s)), "countdowns": _r(_cdf(s)),
        "schedule": _r(_sf(s)), "homework": _r(_hf(s)), "exams": _r(_ef(s)),
    }


# ── 路由表 ──

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # 静默日志

    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, text):
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, mime):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            if APP_HTML.exists():
                self._send_file(APP_HTML, "text/html; charset=utf-8")
            else:
                self._send_html("<h1>app.html 未找到</h1>")
            return
        if path == "/api/today":
            return self._send_json(api_today())
        if path == "/api/tasks":
            return self._send_json(api_tasks(query))
        if path == "/api/lists":
            return self._send_json(api_lists())
        if path == "/api/habits":
            return self._send_json(api_habits())
        if path == "/api/countdowns":
            return self._send_json(api_countdowns())
        if path == "/api/schedule":
            return self._send_json(api_schedule())
        if path == "/api/homework":
            return self._send_json(api_homework())
        if path == "/api/exams":
            return self._send_json(api_exams())
        if path == "/api/pomodoro":
            return self._send_json(api_pomodoro())
        if path == "/api/eisenhower":
            return self._send_json(api_eisenhower())
        if path == "/api/dashboard":
            return self._send_json(api_dashboard())
        if path == "/api/semesters":
            return self._send_json(api_semesters())
        if path == "/api/export":
            return self._send_json(api_export())
        self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        parts = path.strip("/").split("/")
        body = self._read_body()

        if path == "/api/tasks":
            return self._send_json(api_task_add(body))
        if path == "/api/lists":
            return self._send_json(api_list_add(body))
        if path == "/api/habits":
            return self._send_json(api_habit_add(body))
        if path == "/api/countdowns":
            return self._send_json(api_countdown_add(body))
        if path == "/api/homework":
            return self._send_json(api_homework_add(body))
        if path == "/api/exams":
            return self._send_json(api_exam_add(body))
        if path == "/api/pomodoro":
            return self._send_json(api_pomodoro_add(body))
        if path == "/api/semesters/switch":
            return self._send_json(api_semester_switch(body))
        # /api/tasks/<id>/done
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "tasks" and parts[3] == "done":
            return self._send_json(api_task_done(parts[2]))
        # /api/tasks/<id>/subtask/<idx>
        if len(parts) == 5 and parts[0] == "api" and parts[1] == "tasks" and parts[3] == "subtask":
            return self._send_json(api_subtask_done(parts[2], int(parts[4])))
        # /api/habits/<id>/checkin
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "habits" and parts[3] == "checkin":
            return self._send_json(api_habit_checkin(parts[2]))
        # /api/homework/<id>/done
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "homework" and parts[3] == "done":
            return self._send_json(api_homework_done(int(parts[2])))
        self._send_json({"error": "not found"}, 404)

    def do_PUT(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        body = self._read_body()
        # /api/tasks/<id>
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "tasks":
            return self._send_json(api_task_update(parts[2], body))
        self._send_json({"error": "not found"}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        # /api/tasks/<id>
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "tasks":
            return self._send_json(api_task_delete(parts[2]))
        self._send_json({"error": "not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run(port=5000, host="0.0.0.0", open_browser=False):
    lan_ip = get_lan_ip()
    local_url = f"http://127.0.0.1:{port}"
    lan_url = f"http://{lan_ip}:{port}"

    print()
    print("=" * 52)
    print("  📚 大学日程计划 v1.3 — Web 服务已启动")
    print("=" * 52)
    print(f"  💻 本机访问：{local_url}")
    print(f"  📱 手机访问：{lan_url}")
    print("  （手机需与电脑连接同一个 WiFi）")
    print("-" * 52)
    print("  按 Ctrl+C 停止服务")
    print("=" * 52)
    print()

    if open_browser:
        try:
            webbrowser.open(local_url)
        except Exception:
            pass

    server = HTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
        server.server_close()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="大学日程计划 Web 服务")
    p.add_argument("--port", type=int, default=5000, help="端口号（默认5000）")
    p.add_argument("--host", default="0.0.0.0", help="监听地址")
    p.add_argument("--open", action="store_true", help="自动打开浏览器")
    args = p.parse_args()
    run(port=args.port, host=args.host, open_browser=args.open)
