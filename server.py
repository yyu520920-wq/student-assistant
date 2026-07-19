#!/usr/bin/env python3
"""
大学生助手 v1.1 - Web 服务
启动后浏览器打开 http://localhost:5000

用法：
  python3 server.py              # 启动服务
  python3 server.py --port 8080  # 指定端口
"""

import sys
import os
import json
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
from engine import (
    get_remind_data, get_current_semester, get_semester_dir,
    load_json, save_json, ensure_dir,
    _schedule_file, _homework_file, _exam_file,
    BASE_DIR,
)

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")


# ── 首页 ──
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# ── 数据 API ──

@app.route("/api/remind")
def api_remind():
    """获取今日提醒数据"""
    return jsonify(get_remind_data())


@app.route("/api/schedule")
def api_schedule():
    """获取课表"""
    sem = get_current_semester()
    return jsonify({"semester": sem, "courses": load_json(_schedule_file(sem))})


@app.route("/api/schedule", methods=["POST"])
def api_schedule_add():
    """添加课程"""
    sem = get_current_semester()
    data = load_json(_schedule_file(sem))
    course = request.json
    course["id"] = max([c.get("id", 0) for c in data], default=0) + 1
    data.append(course)
    save_json(_schedule_file(sem), data)
    return jsonify({"ok": True, "id": course["id"]})


@app.route("/api/schedule/<int:cid>", methods=["DELETE"])
def api_schedule_delete(cid):
    sem = get_current_semester()
    data = load_json(_schedule_file(sem))
    data = [c for c in data if c.get("id") != cid]
    save_json(_schedule_file(sem), data)
    return jsonify({"ok": True})


@app.route("/api/schedule/import", methods=["POST"])
def api_schedule_import():
    """导入课表 JSON"""
    sem = get_current_semester()
    courses = request.json
    save_json(_schedule_file(sem), courses)
    return jsonify({"ok": True, "count": len(courses)})


@app.route("/api/homework")
def api_homework():
    sem = get_current_semester()
    return jsonify({"semester": sem, "items": load_json(_homework_file(sem))})


@app.route("/api/homework", methods=["POST"])
def api_homework_add():
    sem = get_current_semester()
    data = load_json(_homework_file(sem))
    hw = request.json
    hw["id"] = max([h.get("id", 0) for h in data], default=0) + 1
    hw["done"] = False
    data.append(hw)
    save_json(_homework_file(sem), data)
    return jsonify({"ok": True, "id": hw["id"]})


@app.route("/api/homework/<int:hid>", methods=["PUT"])
def api_homework_update(hid):
    sem = get_current_semester()
    data = load_json(_homework_file(sem))
    for h in data:
        if h["id"] == hid:
            h.update(request.json)
            save_json(_homework_file(sem), data)
            return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "not found"}), 404


@app.route("/api/homework/<int:hid>", methods=["DELETE"])
def api_homework_delete(hid):
    sem = get_current_semester()
    data = load_json(_homework_file(sem))
    data = [h for h in data if h["id"] != hid]
    save_json(_homework_file(sem), data)
    return jsonify({"ok": True})


@app.route("/api/exam")
def api_exam():
    sem = get_current_semester()
    return jsonify({"semester": sem, "items": load_json(_exam_file(sem))})


@app.route("/api/exam", methods=["POST"])
def api_exam_add():
    sem = get_current_semester()
    data = load_json(_exam_file(sem))
    exam = request.json
    exam["id"] = max([e.get("id", 0) for e in data], default=0) + 1
    data.append(exam)
    save_json(_exam_file(sem), data)
    return jsonify({"ok": True, "id": exam["id"]})


@app.route("/api/exam/<int:eid>", methods=["DELETE"])
def api_exam_delete(eid):
    sem = get_current_semester()
    data = load_json(_exam_file(sem))
    data = [e for e in data if e["id"] != eid]
    save_json(_exam_file(sem), data)
    return jsonify({"ok": True})


@app.route("/api/semester")
def api_semester():
    """学期列表 + 当前学期"""
    sem_dir = BASE_DIR / "semesters"
    semesters = []
    if sem_dir.exists():
        for d in sorted(sem_dir.iterdir()):
            if d.is_dir():
                semesters.append({
                    "name": d.name,
                    "course_count": len(load_json(d / "schedule.json")),
                })
    return jsonify({
        "current": get_current_semester(),
        "semesters": semesters,
    })


@app.route("/api/semester/switch", methods=["POST"])
def api_semester_switch():
    from engine import set_current_semester, ensure_dir
    name = request.json.get("name")
    sd = get_semester_dir(name)
    if not sd.exists():
        ensure_dir(sd)
        save_json(_schedule_file(name), [])
        save_json(_homework_file(name), [])
        save_json(_exam_file(name), [])
    set_current_semester(name)
    return jsonify({"ok": True, "current": name})


# ── 仪表盘 API ──

@app.route("/api/dashboard")
def api_dashboard():
    """返回仪表盘汇总数据"""
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    today = date.today()

    # 复习数据
    review = load_json(sd / "review.json")
    total_kp = len(review)
    mastered = sum(1 for k in review if k.get("mastery", 0) >= 80)
    weak = sum(1 for k in review if k.get("mastery", 0) < 50)

    # 成长数据
    daily = load_json(sd / "daily.json")
    last7 = daily[-7:] if len(daily) >= 7 else daily
    study_trend = [{"date": d.get("date", ""), "hours": d.get("study_hours", 0)} for d in last7]
    total_study = sum(d.get("study_hours", 0) for d in daily)
    streak = 0
    check_date = today
    for d in reversed(daily):
        if d.get("date") == check_date.isoformat():
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    # 目标
    goals = load_json(sd / "goals.json")
    goal_progress = [{"title": g.get("title", ""), "progress": g.get("progress", 0),
                      "type": g.get("type", ""), "deadline": g.get("deadline", "")} for g in goals]

    # 刷题
    practice = load_json(sd / "practice.json")
    total_questions = sum(p.get("count", 0) for p in practice)
    total_correct = sum(p.get("correct", 0) for p in practice)
    accuracy = round(total_correct / max(total_questions, 1) * 100, 1)

    # 错题
    wrong = load_json(sd / "wrong_questions.json")
    unreviewed_wrong = sum(1 for w in wrong if not w.get("reviewed", False))

    # 考试倒计时
    exams = load_json(sd / "exam.json")
    next_exam = None
    min_days = 999
    for e in exams:
        days = (datetime.strptime(e["date"], "%Y-%m-%d").date() - today).days
        if 0 <= days < min_days:
            min_days = days
            next_exam = {"course": e["course"], "type": e["type"], "date": e["date"], "days": days}

    return jsonify({
        "semester": sem,
        "review": {"total": total_kp, "mastered": mastered, "weak": weak,
                   "mid": total_kp - mastered - weak, "rate": round(mastered / max(total_kp, 1) * 100, 1)},
        "daily": {"study_trend": study_trend, "total_study": total_study, "streak": streak,
                  "total_days": len(daily)},
        "goals": {"items": goal_progress, "completed": sum(1 for g in goals if g.get("progress", 0) >= 100)},
        "practice": {"total_questions": total_questions, "total_correct": total_correct, "accuracy": accuracy},
        "wrong": {"total": len(wrong), "unreviewed": unreviewed_wrong},
        "next_exam": next_exam,
    })


@app.route("/api/review", methods=["GET"])
def api_review():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    return jsonify({"knowledge_points": load_json(sd / "review.json")})


@app.route("/api/review/knowledge", methods=["POST"])
def api_review_add():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    data = load_json(sd / "review.json")
    kp = request.json
    kp["id"] = max([k.get("id", 0) for k in data], default=0) + 1
    data.append(kp)
    save_json(sd / "review.json", data)
    return jsonify({"ok": True})


@app.route("/api/daily", methods=["GET"])
def api_daily():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    return jsonify({"records": load_json(sd / "daily.json")})


@app.route("/api/daily", methods=["POST"])
def api_daily_add():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    data = load_json(sd / "daily.json")
    record = request.json
    record["date"] = date.today().isoformat()
    # 覆盖同日记录
    data = [d for d in data if d.get("date") != record["date"]]
    data.append(record)
    save_json(sd / "daily.json", data)
    return jsonify({"ok": True})


@app.route("/api/goals", methods=["GET"])
def api_goals():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    return jsonify({"goals": load_json(sd / "goals.json")})


@app.route("/api/goals", methods=["POST"])
def api_goals_add():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    data = load_json(sd / "goals.json")
    goal = request.json
    goal["id"] = max([g.get("id", 0) for g in data], default=0) + 1
    goal["created"] = date.today().isoformat()
    goal["milestones"] = goal.get("milestones", [])
    data.append(goal)
    save_json(sd / "goals.json", data)
    return jsonify({"ok": True})


@app.route("/api/goals/<int:gid>", methods=["PUT"])
def api_goals_update(gid):
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    data = load_json(sd / "goals.json")
    for g in data:
        if g["id"] == gid:
            g.update(request.json)
            save_json(sd / "goals.json", data)
            return jsonify({"ok": True})
    return jsonify({"ok": False}), 404


@app.route("/api/practice", methods=["GET"])
def api_practice():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    return jsonify({"records": load_json(sd / "practice.json")})


@app.route("/api/practice", methods=["POST"])
def api_practice_add():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    data = load_json(sd / "practice.json")
    record = request.json
    record["id"] = max([r.get("id", 0) for r in data], default=0) + 1
    record["date"] = date.today().isoformat()
    data.append(record)
    save_json(sd / "practice.json", data)
    return jsonify({"ok": True})


@app.route("/api/export/excel")
def api_export_excel():
    """生成并下载 Excel"""
    import subprocess, tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    tmp.close()
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "scripts", "export_excel.py"), "-o", tmp.name])
    from flask import send_file
    return send_file(tmp.name, as_attachment=True, download_name="大学生数据报表.xlsx")


# ── 简历 API ──

@app.route("/api/resume/generate", methods=["POST"])
def api_resume_generate():
    """生成简历并下载"""
    import subprocess, tempfile
    data = request.json
    tmp_json = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8")
    json.dump(data, tmp_json, ensure_ascii=False)
    tmp_json.close()
    tmp_docx = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    tmp_docx.close()
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "scripts", "generate_resume.py"),
                    "--from-json", tmp_json.name, "-t", data.get("template", "classic"), "-o", tmp_docx.name])
    from flask import send_file
    return send_file(tmp_docx.name, as_attachment=True, download_name="个人简历.docx")


# ── 规划 API ──

@app.route("/api/plan", methods=["GET"])
def api_plan():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    from engine import _plan_file
    return jsonify({"plans": load_json(_plan_file(sem))})


@app.route("/api/plan", methods=["POST"])
def api_plan_add():
    sem = get_current_semester()
    sd = get_semester_dir(sem)
    from engine import _plan_file
    data = load_json(_plan_file(sem))
    plan = request.json
    plan["id"] = max([p.get("id", 0) for p in data], default=0) + 1
    plan["created"] = date.today().isoformat()
    data.append(plan)
    save_json(_plan_file(sem), data)
    return jsonify({"ok": True})


@app.route("/api/plan/<int:pid>", methods=["PUT"])
def api_plan_update(pid):
    sem = get_current_semester()
    from engine import _plan_file
    data = load_json(_plan_file(sem))
    for p in data:
        if p["id"] == pid:
            p["done"] = request.json.get("done", True)
            save_json(_plan_file(sem), data)
            return jsonify({"ok": True})
    return jsonify({"ok": False}), 404


# ── 启动 ──

def main():
    import argparse
    parser = argparse.ArgumentParser(description="大学生助手 Web 服务")
    parser.add_argument("--port", "-p", type=int, default=5000, help="端口号")
    args = parser.parse_args()

    print("🎓 大学生助手 v1.1 Web 服务")
    print(f"   打开浏览器访问: http://localhost:{args.port}")
    print(f"   按 Ctrl+C 停止\n")

    app.run(host="0.0.0.0", port=args.port, debug=True)


if __name__ == "__main__":
    main()
