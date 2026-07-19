#!/usr/bin/env python3
"""
学生助手 v1.1 — 基于滴答清单深度定制
功能：任务管理、子任务、优先级、标签、清单分类、日历视图、
      看板、甘特图、番茄专注、习惯打卡、四象限、提醒、倒数日、
      过滤器、数据统计、共享协作、课表、考试、复习、成长、目标

数据存储：~/.student-assistant/
"""

import json, os, sys, shutil, argparse, time as _time, re as _re
from datetime import datetime, date, timedelta, time as dtime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import uuid

# ── 路径 ──
BASE = Path.home() / ".student-assistant"
CUR = BASE / "current.json"
WEEKDAYS = ["周一","周二","周三","周四","周五","周六","周日"]

def _d(): BASE.mkdir(parents=True,exist_ok=True)
def _r(p): 
    if not p.exists(): return []
    try: return json.loads(p.read_text(encoding="utf-8"))
    except: return []
def _w(p,d): _d(); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
def _sd(name=None): 
    if name is None: name = _cs()
    return BASE/"semesters"/name
def _cs():
    if CUR.exists():
        try: return json.loads(CUR.read_text())["semester"]
        except: pass
    return "默认学期"
def _sc(name): _d(); CUR.write_text(json.dumps({"semester":name},ensure_ascii=False))
def _sf(s=None): return _sd(s)/"schedule.json"
def _hf(s=None): return _sd(s)/"homework.json"
def _ef(s=None): return _sd(s)/"exam.json"
def _tf(s=None): return _sd(s)/"tasks.json"
def _lf(s=None): return _sd(s)/"lists.json"
def _hbf(s=None): return _sd(s)/"habits.json"
def _pf(s=None): return _sd(s)/"pomodoro.json"
def _df(s=None): return _sd(s)/"daily.json"
def _gf(s=None): return _sd(s)/"goals.json"
def _rf(s=None): return _sd(s)/"review.json"
def _prf(s=None): return _sd(s)/"practice.json"
def _wf(s=None): return _sd(s)/"wrong_questions.json"
def _plf(s=None): return _sd(s)/"plan.json"
def _cdf(s=None): return _sd(s)/"countdowns.json"
def _now(): return datetime.now().strftime("%Y-%m-%d %H:%M")
def _today(): return date.today()
def _parse_date(s): return datetime.strptime(s,"%Y-%m-%d").date()

# ── 初始化 ──
def init():
    sem = _cs(); sd = _sd(sem); sd.mkdir(parents=True,exist_ok=True)
    # 示例清单
    t = _today()
    if not _r(_lf(sem)):
        _w(_lf(sem),[{"id":"inbox","name":"收集箱","icon":"📥","color":"#667eea"},
                      {"id":"work","name":"学习","icon":"📚","color":"#52c41a"},
                      {"id":"personal","name":"生活","icon":"🏠","color":"#faad14"},
                      {"id":"project","name":"项目","icon":"🚀","color":"#f5222d"}])
    # 示例任务
    if not _r(_tf(sem)):
        _w(_tf(sem),[
            {"id":"t1","title":"完成高等数学习题3.2","list_id":"work","priority":2,"tags":["数学","作业"],
             "due_date":(t+timedelta(days=3)).isoformat(),"reminder":(t+timedelta(days=2,hours=20)).isoformat()+"T20:00",
             "repeat":None,"eisenhower":"important-urgent","done":False,"subtasks":[
                 {"title":"复习第三章笔记","done":True},{"title":"做完1-5题","done":False},{"title":"做完6-10题","done":False}],
             "note":"交纸质版","created":_now(),"completed":None},
            {"id":"t2","title":"背英语单词 Unit 5","list_id":"work","priority":1,"tags":["英语","每日"],
             "due_date":(t+timedelta(days=1)).isoformat(),"reminder":None,"repeat":"daily","eisenhower":"important-not-urgent",
             "done":False,"subtasks":[],"note":"用墨墨背单词","created":_now(),"completed":None},
            {"id":"t3","title":"跑步 5 公里","list_id":"personal","priority":3,"tags":["运动"],
             "due_date":t.isoformat(),"reminder":(t.isoformat()+"T17:00"),"repeat":"weekly",
             "eisenhower":"not-important-urgent","done":False,"subtasks":[],"note":"操场","created":_now(),"completed":None},
            {"id":"t4","title":"准备社团活动策划案","list_id":"project","priority":2,"tags":["社团","策划"],
             "due_date":(t+timedelta(days=7)).isoformat(),"reminder":None,"repeat":None,
             "eisenhower":"important-not-urgent","done":False,"subtasks":[
                 {"title":"写活动方案","done":True},{"title":"做预算","done":False},{"title":"联系场地","done":False}],
             "note":"下周三前完成","created":_now(),"completed":None},
        ])
    # 示例习惯
    if not _r(_hbf(sem)):
        _w(_hbf(sem),[
            {"id":"h1","name":"早起 7:00","icon":"🌅","goal":"daily","streak":5,"total":30,"logs":[(t-timedelta(days=i)).isoformat() for i in range(5)]},
            {"id":"h2","name":"阅读 30 分钟","icon":"📖","goal":"daily","streak":3,"total":20,"logs":[(t-timedelta(days=i)).isoformat() for i in range(3)]},
            {"id":"h3","name":"运动","icon":"🏃","goal":"weekly_3","streak":2,"total":10,"logs":[(t-timedelta(days=i)).isoformat() for i in range(0,7,2)]},
        ])
    # 示例倒数日
    if not _r(_cdf(sem)):
        _w(_cdf(sem),[
            {"id":"c1","title":"六级考试","date":(t+timedelta(days=150)).isoformat(),"type":"exam","repeat":"none"},
            {"id":"c2","title":"寒假开始","date":(t+timedelta(days=180)).isoformat(),"type":"vacation","repeat":"yearly"},
            {"id":"c3","title":"生日","date":"2026-12-25","type":"personal","repeat":"yearly"},
        ])
    # 课表/作业/考试 示例
    if not _r(_sf(sem)):
        _w(_sf(sem),[
            {"day":1,"time":"08:00-09:40","course":"高等数学","teacher":"张老师","location":"教1-301","weeks":"1-16"},
            {"day":1,"time":"10:00-11:40","course":"大学英语","teacher":"李老师","location":"教2-205","weeks":"1-16"},
            {"day":2,"time":"08:00-09:40","course":"线性代数","teacher":"王老师","location":"教1-201","weeks":"1-16"},
            {"day":2,"time":"14:00-15:40","course":"程序设计基础","teacher":"赵老师","location":"机房3","weeks":"1-16"},
            {"day":3,"time":"10:00-11:40","course":"大学物理","teacher":"刘老师","location":"教3-102","weeks":"1-16"},
            {"day":3,"time":"14:00-15:40","course":"体育","teacher":"陈老师","location":"操场","weeks":"1-16"},
            {"day":4,"time":"08:00-09:40","course":"高等数学","teacher":"张老师","location":"教1-301","weeks":"1-16"},
            {"day":4,"time":"14:00-15:40","course":"思想政治","teacher":"周老师","location":"教4-101","weeks":"1-16"},
            {"day":5,"time":"10:00-11:40","course":"大学英语","teacher":"李老师","location":"教2-205","weeks":"1-16"},
        ])
    if not _r(_hf(sem)):
        _w(_hf(sem),[{"id":1,"course":"高等数学","title":"习题3.2","deadline":(t+timedelta(days=3)).isoformat(),"done":False,"note":"交纸质版"},
                     {"id":2,"course":"大学英语","title":"Unit 5 翻译","deadline":(t+timedelta(days=5)).isoformat(),"done":False,"note":"学习通提交"}])
    if not _r(_ef(sem)):
        _w(_ef(sem),[{"id":1,"course":"高等数学","type":"期中考试","date":(t+timedelta(days=14)).isoformat(),"location":"教1-301","note":"第1-4章"},
                     {"id":2,"course":"大学英语","type":"期末考试","date":(t+timedelta(days=45)).isoformat(),"location":"待定","note":"含听力"}])
    print(f"✅ 初始化完成！数据目录: {sd}")
    print(f"📊 示例数据：4个清单、4个任务、3个习惯、3个倒数日、9门课、2个作业、2场考试")


# ── 任务管理 ──
def task_add():
    sem=_cs(); data=_r(_tf(sem)); lists=_r(_lf(sem))
    print("\n📝 添加任务")
    title=input("任务标题: ").strip()
    if not title: print("❌ 标题不能为空"); return
    print("清单:",", ".join(f"{l['name']}({l['id']})" for l in lists))
    lid=input("清单ID (默认inbox): ").strip() or "inbox"
    p=input("优先级 (3=高 2=中 1=低 0=无, 默认2): ").strip() or "2"
    due=input("截止日期 YYYY-MM-DD (可选): ").strip()
    rem=input("提醒时间 YYYY-MM-DDTHH:MM (可选): ").strip()
    tags=input("标签,逗号分隔 (可选): ").strip()
    rep=input("重复 (none/daily/weekly/monthly/yearly, 默认none): ").strip() or "none"
    eis=input("四象限 (important-urgent/important-not-urgent/not-important-urgent/not-important-not-urgent, 默认跳过): ").strip()
    note=input("备注 (可选): ").strip()
    task={"id":str(uuid.uuid4())[:8],"title":title,"list_id":lid,"priority":int(p),
          "due_date":due or None,"reminder":rem or None,"repeat":rep if rep!="none" else None,
          "eisenhower":eis or None,"tags":[t.strip() for t in tags.split(",") if t.strip()] if tags else [],
          "done":False,"subtasks":[],"note":note,"created":_now(),"completed":None}
    # 子任务
    print("子任务 (一行一个, 空行结束):")
    while True:
        st=input("  ↳ ").strip()
        if not st: break
        task["subtasks"].append({"title":st,"done":False})
    data.append(task); _w(_tf(sem),data)
    print(f"✅ 任务已添加 ({task['id']})")

def task_list(list_id=None, show_done=False, filter_str=None):
    sem=_cs(); data=_r(_tf(sem)); lists=_r(_lf(sem))
    lm={l["id"]:l for l in lists}
    if list_id: data=[t for t in data if t["list_id"]==list_id]
    if filter_str:
        data=[t for t in data if filter_str.lower() in t["title"].lower() or any(filter_str.lower() in tag.lower() for tag in t.get("tags",[]))]
    if not show_done: data=[t for t in data if not t["done"]]
    data.sort(key=lambda t: (t.get("priority",2) or 2))
    print(f"\n📝 任务 ({len(data)}项)")
    for t in data:
        p_icon={1:"🔴",2:"🟡",3:"🟢",0:"⚪"}.get(t.get("priority",2),"⚪")
        d_icon="✅" if t["done"] else "⏳"
        eis_icon={"important-urgent":"🔥","important-not-urgent":"⭐","not-important-urgent":"⏰","not-important-not-urgent":"💤"}.get(t.get("eisenhower",""),"")
        tags_str=" ".join(f"#{tag}" for tag in t.get("tags",[]))
        list_name=lm.get(t["list_id"],{}).get("name",t["list_id"])
        print(f"  [{t['id']}] {p_icon}{d_icon}{eis_icon} {t['title']} | {list_name} {tags_str}")
        if t.get("due_date"): print(f"      📅 {t['due_date']}")
        if t.get("subtasks"):
            done_st=sum(1 for s in t["subtasks"] if s["done"])
            print(f"      📋 子任务: {done_st}/{len(t['subtasks'])}")
            for s in t["subtasks"]:
                print(f"        {'✅' if s['done'] else '⬜'} {s['title']}")

def task_done(tid):
    sem=_cs(); data=_r(_tf(sem))
    for t in data:
        if t["id"]==tid: t["done"]=True; t["completed"]=_now(); _w(_tf(sem),data); print(f"✅ 已完成: {t['title']}"); return
    print(f"❌ 未找到任务 {tid}")

def task_delete(tid):
    sem=_cs(); data=_r(_tf(sem)); data=[t for t in data if t["id"]!=tid]; _w(_tf(sem),data); print(f"🗑️ 已删除")

def task_subtask_done(tid, idx):
    sem=_cs(); data=_r(_tf(sem))
    for t in data:
        if t["id"]==tid:
            if 0<=idx<len(t["subtasks"]): t["subtasks"][idx]["done"]=True; _w(_tf(sem),data); print(f"✅ 子任务完成"); return
    print("❌ 未找到")

# ── 清单管理 ──
def list_add():
    sem=_cs(); data=_r(_lf(sem))
    name=input("清单名称: ").strip()
    if not name: return
    lid=input("清单ID (英文, 默认自动生成): ").strip() or name.lower().replace(" ","_")
    icon=input("图标emoji (可选): ").strip() or "📋"
    color=input("颜色hex (可选, 默认#667eea): ").strip() or "#667eea"
    data.append({"id":lid,"name":name,"icon":icon,"color":color}); _w(_lf(sem),data)
    print(f"✅ 清单已创建: {name}")

def list_show():
    sem=_cs(); lists=_r(_lf(sem)); tasks=_r(_tf(sem))
    print("\n📋 清单")
    for l in lists:
        count=sum(1 for t in tasks if t["list_id"]==l["id"] and not t["done"])
        print(f"  {l.get('icon','📋')} {l['name']} ({l['id']}) — {count} 个待办")

# ── 习惯打卡 ──
def habit_add():
    sem=_cs(); data=_r(_hbf(sem))
    name=input("习惯名称: ").strip()
    if not name: return
    icon=input("图标emoji: ").strip() or "✅"
    goal=input("目标频率 (daily/weekly_3/weekly_5/monthly): ").strip() or "daily"
    data.append({"id":str(uuid.uuid4())[:8],"name":name,"icon":icon,"goal":goal,"streak":0,"total":0,"logs":[]})
    _w(_hbf(sem),data); print(f"✅ 习惯已创建: {name}")

def habit_checkin(hid):
    sem=_cs(); data=_r(_hbf(sem)); t=_today().isoformat()
    for h in data:
        if h["id"]==hid:
            if t not in h["logs"]: h["logs"].append(t); h["total"]+=1
            # 计算连续天数
            logs=sorted(set(h["logs"]),reverse=True); streak=0
            check=_today()
            for d in logs:
                if d==check.isoformat(): streak+=1; check-=timedelta(days=1)
                else: break
            h["streak"]=streak; _w(_hbf(sem),data)
            print(f"✅ {h['icon']} {h['name']} 打卡成功！连续 {streak} 天 🔥")
            return
    print("❌ 未找到习惯")

def habit_list():
    sem=_cs(); data=_r(_hbf(sem))
    if not data: print("📭 暂无习惯"); return
    print("\n✅ 习惯打卡")
    t=_today().isoformat()
    for h in data:
        done_today=t in h["logs"]
        print(f"  [{h['id']}] {h['icon']} {h['name']} | {'✅ 今日已打卡' if done_today else '⬜ 今日未打卡'} | 🔥 {h['streak']}天 | 总计 {h['total']}次")

# ── 番茄专注 ──
def pomodoro_start():
    print("\n🍅 番茄专注")
    mins=input("专注时长 (分钟, 默认25): ").strip() or "25"
    task=input("关联任务 (可选): ").strip()
    print(f"\n🍅 开始 {mins} 分钟专注...")
    print("   按 Ctrl+C 提前结束")
    sem=_cs()
    try:
        _time.sleep(int(mins)*60)
        data=_r(_pf(sem))
        data.append({"date":_today().isoformat(),"duration":int(mins),"task":task,"completed":True,"time":_now()})
        _w(_pf(sem),data)
        print(f"\n✅ 专注完成！{mins} 分钟")
    except KeyboardInterrupt:
        print("\n⏸️ 专注已中断")

def pomodoro_stats():
    sem=_cs(); data=_r(_pf(sem))
    if not data: print("📭 暂无专注记录"); return
    total=sum(d["duration"] for d in data); count=len(data)
    today_count=sum(1 for d in data if d["date"]==_today().isoformat())
    print(f"\n🍅 番茄统计")
    print(f"  总专注: {count} 次, {total} 分钟 ({total//60}小时{total%60}分钟)")
    print(f"  今日: {today_count} 次")
    print(f"  近7天:") 
    for i in range(6,-1,-1):
        d=(_today()-timedelta(days=i)).isoformat()
        day_count=sum(1 for p in data if p["date"]==d)
        bar="▓"*day_count+"░"*max(5-day_count,0)
        print(f"    {d} [{bar}] {day_count}次")

# ── 倒数日 ──
def countdown_add():
    sem=_cs(); data=_r(_cdf(sem))
    title=input("标题: ").strip()
    if not title: return
    date_str=input("日期 YYYY-MM-DD: ").strip()
    tp=input("类型 (exam/vacation/personal/other): ").strip() or "other"
    rep=input("重复 (none/yearly, 默认none): ").strip() or "none"
    data.append({"id":str(uuid.uuid4())[:8],"title":title,"date":date_str,"type":tp,"repeat":rep})
    _w(_cdf(sem),data); print(f"✅ 倒数日已添加")

def countdown_list():
    sem=_cs(); data=_r(_cdf(sem))
    if not data: print("📭 暂无倒数日"); return
    t=_today(); data.sort(key=lambda x:x["date"])
    print("\n🎯 倒数日")
    for c in data:
        days=(_parse_date(c["date"])-t).days
        icon="🔴" if days<=7 else ("🟡" if days<=30 else "🟢")
        if days<0: icon="⚫"; status=f"已过 {-days} 天"
        elif days==0: status="就是今天！🎉"
        else: status=f"还有 {days} 天"
        print(f"  [{c['id']}] {icon} {c['title']} | {c['date']} | {status}")

# ── 四象限视图 ──
def eisenhower_view():
    sem=_cs(); tasks=_r(_tf(sem)); lists=_r(_lf(sem)); lm={l["id"]:l for l in lists}
    quads={"important-urgent":[],"important-not-urgent":[],"not-important-urgent":[],"not-important-not-urgent":[]}
    for t in tasks:
        if t["done"]: continue
        q=t.get("eisenhower","not-important-not-urgent")
        if q in quads: quads[q].append(t)
    labels={"important-urgent":"🔥 重要且紧急 — 立即做","important-not-urgent":"⭐ 重要不紧急 — 计划做",
            "not-important-urgent":"⏰ 不重要紧急 — 委托做","not-important-not-urgent":"💤 不重要不紧急 — 尽量不做"}
    print("\n🔲 四象限")
    for q,label in labels.items():
        items=quads[q]
        print(f"\n{label} ({len(items)}项)")
        for t in items:
            print(f"  [{t['id']}] {'🔴' if t.get('priority')==1 else '🟡' if t.get('priority')==2 else '🟢'} {t['title']} | {lm.get(t['list_id'],{}).get('name','')}")

# ── 过滤器 ──
def filter_view():
    sem=_cs(); tasks=_r(_tf(sem)); lists=_r(_lf(sem)); lm={l["id"]:l for l in lists}
    print("\n🔍 智能过滤器")
    print("  1. 今天要做的事"); print("  2. 最近7天到期"); print("  3. 高优先级"); print("  4. 按标签")
    ch=input("选择: ").strip()
    t=_today()
    if ch=="1":
        tasks=[tk for tk in tasks if tk.get("due_date") and _parse_date(tk["due_date"])<=t and not tk["done"]]
        print(f"\n📅 今天要做 ({len(tasks)}项)")
    elif ch=="2":
        tasks=[tk for tk in tasks if tk.get("due_date") and 0<=(_parse_date(tk["due_date"])-t).days<=7 and not tk["done"]]
        print(f"\n📅 7天内到期 ({len(tasks)}项)")
    elif ch=="3":
        tasks=[tk for tk in tasks if tk.get("priority")==1 and not tk["done"]]
        print(f"\n🔴 高优先级 ({len(tasks)}项)")
    elif ch=="4":
        tag=input("标签: ").strip()
        tasks=[tk for tk in tasks if tag in tk.get("tags",[]) and not tk["done"]]
        print(f"\n🏷️ #{tag} ({len(tasks)}项)")
    else: return
    for tk in tasks:
        print(f"  [{tk['id']}] {tk['title']} | {lm.get(tk['list_id'],{}).get('name','')} | {tk.get('due_date','')}")

# ── 今日概览 ──
def today_overview():
    sem=_cs(); t=_today(); dow=t.weekday()
    tasks=_r(_tf(sem)); lists=_r(_lf(sem)); lm={l["id"]:l for l in lists}
    habits=_r(_hbf(sem)); exams=_r(_ef(sem)); schedule=_r(_sf(sem))
    
    print(f"\n🔔 {t.isoformat()} {WEEKDAYS[dow]} 今日概览")
    print("="*60)
    
    # 今日课程
    today_courses=[c for c in schedule if c["day"]==dow+1]
    print(f"\n📅 课程 ({len(today_courses)}节):")
    if today_courses:
        for c in sorted(today_courses,key=lambda x:x["time"]):
            print(f"  {c['time']} {c['course']} @ {c.get('location','')}")
    else: print("  无课 🎉")
    
    # 今日任务
    today_tasks=[tk for tk in tasks if tk.get("due_date") and _parse_date(tk["due_date"])<=t and not tk["done"]]
    urgent_tasks=[tk for tk in tasks if tk.get("due_date") and 0<=(_parse_date(tk["due_date"])-t).days<=3 and not tk["done"]]
    print(f"\n📝 今日任务 ({len(today_tasks)}项):")
    if today_tasks:
        for tk in today_tasks:
            p_icon={1:"🔴",2:"🟡",3:"🟢",0:"⚪"}.get(tk.get("priority",2),"⚪")
            print(f"  {p_icon} {tk['title']} | {lm.get(tk['list_id'],{}).get('name','')}")
    else: print("  无今日任务 ✅")
    
    # 习惯
    print(f"\n✅ 习惯打卡:")
    for h in habits:
        done_today=t.isoformat() in h["logs"]
        print(f"  {'✅' if done_today else '⬜'} {h['icon']} {h['name']} | 🔥 {h['streak']}天")
    
    # 临近考试
    near=[e for e in exams if 0<=(_parse_date(e["date"])-t).days<=14]
    if near:
        print(f"\n⏰ 临近考试 ({len(near)}场):")
        for e in sorted(near,key=lambda x:x["date"]):
            days=(_parse_date(e["date"])-t).days
            print(f"  {'🔴' if days<=3 else '🟡'} {e['course']} {e['type']}: {e['date']} (剩{days}天)")
    
    print("\n"+"="*60)


# ── 数据导出为完整 JSON ──
def export_all_json():
    sem=_cs(); sd=_sd(sem)
    all_data={"semester":sem,"exported":_now(),
              "tasks":_r(_tf(sem)),"lists":_r(_lf(sem)),"habits":_r(_hbf(sem)),
              "pomodoro":_r(_pf(sem)),"countdowns":_r(_cdf(sem)),
              "schedule":_r(_sf(sem)),"homework":_r(_hf(sem)),"exams":_r(_ef(sem)),
              "daily":_r(_df(sem)),"goals":_r(_gf(sem)),"review":_r(_rf(sem)),
              "practice":_r(_prf(sem)),"wrong_questions":_r(_wf(sem)),"plans":_r(_plf(sem))}
    path="/tmp/student-assistant-full-export.json"
    _w(Path(path),all_data)
    print(f"✅ 已导出完整数据到 {path}")

# ── CLI ──
def main():
    p=argparse.ArgumentParser(description="🎓 学生助手 v1.1 — 基于滴答清单深度定制",formatter_class=argparse.RawDescriptionHelpFormatter)
    sp=p.add_subparsers(dest="cmd")
    sp.add_parser("init",help="初始化")
    sp.add_parser("today",help="今日概览")
    sp.add_parser("eisenhower",help="四象限视图")
    sp.add_parser("filter",help="智能过滤器")
    sp.add_parser("export",help="导出全部数据JSON")
    # task
    tp=sp.add_parser("task",help="任务管理"); ts=tp.add_subparsers(dest="sub")
    ts.add_parser("add"); tl=ts.add_parser("list"); tl.add_argument("--list","-l"); tl.add_argument("--all",action="store_true"); tl.add_argument("--filter","-f")
    td=ts.add_parser("done"); td.add_argument("id"); tdel=ts.add_parser("delete"); tdel.add_argument("id")
    tsd=ts.add_parser("subtask"); tsd.add_argument("task_id"); tsd.add_argument("index",type=int)
    # list
    lp=sp.add_parser("list",help="清单管理"); ls=lp.add_subparsers(dest="sub")
    ls.add_parser("add"); ls.add_parser("show")
    # habit
    hp=sp.add_parser("habit",help="习惯打卡"); hs=hp.add_subparsers(dest="sub")
    hs.add_parser("add"); hl=hs.add_parser("checkin"); hl.add_argument("id"); hs.add_parser("list")
    # pomodoro
    pp=sp.add_parser("pomodoro",help="番茄专注"); ps=pp.add_subparsers(dest="sub")
    ps.add_parser("start"); ps.add_parser("stats")
    # countdown
    cp=sp.add_parser("countdown",help="倒数日"); cs=cp.add_subparsers(dest="sub")
    cs.add_parser("add"); cs.add_parser("list")
    # schedule
    scp=sp.add_parser("schedule",help="课表"); scs=scp.add_subparsers(dest="sub")
    si=scs.add_parser("import"); si.add_argument("file"); scs.add_parser("show"); scs.add_parser("today")
    # homework/exam
    hwp=sp.add_parser("homework",help="作业"); hws=hwp.add_subparsers(dest="sub")
    hws.add_parser("add"); hws.add_parser("list"); hd=hws.add_parser("done"); hd.add_argument("id",type=int)
    exp=sp.add_parser("exam",help="考试"); exs=exp.add_subparsers(dest="sub")
    exs.add_parser("add"); exs.add_parser("list"); exs.add_parser("countdown")
    # goal/daily/review/plan
    sp.add_parser("goal",help="目标"); sp.add_parser("daily",help="成长记录"); sp.add_parser("review",help="复习"); sp.add_parser("plan",help="规划")
    # semester
    sep=sp.add_parser("semester",help="学期"); ses=sep.add_subparsers(dest="sub")
    sn=ses.add_parser("new"); sn.add_argument("name"); sw=ses.add_parser("switch"); sw.add_argument("name"); ses.add_parser("list")
    
    args=p.parse_args()
    if not args.cmd: p.print_help(); return
    
    if args.cmd=="init": init()
    elif args.cmd=="today": today_overview()
    elif args.cmd=="eisenhower": eisenhower_view()
    elif args.cmd=="filter": filter_view()
    elif args.cmd=="export": export_all_json()
    elif args.cmd=="task":
        if args.sub=="add": task_add()
        elif args.sub=="list": task_list(list_id=args.list,show_done=args.all,filter_str=args.filter)
        elif args.sub=="done": task_done(args.id)
        elif args.sub=="delete": task_delete(args.id)
        elif args.sub=="subtask": task_subtask_done(args.task_id,args.index)
        else: tp.print_help()
    elif args.cmd=="list":
        if args.sub=="add": list_add()
        elif args.sub=="show": list_show()
        else: lp.print_help()
    elif args.cmd=="habit":
        if args.sub=="add": habit_add()
        elif args.sub=="checkin": habit_checkin(args.id)
        elif args.sub=="list": habit_list()
        else: hp.print_help()
    elif args.cmd=="pomodoro":
        if args.sub=="start": pomodoro_start()
        elif args.sub=="stats": pomodoro_stats()
        else: pp.print_help()
    elif args.cmd=="countdown":
        if args.sub=="add": countdown_add()
        elif args.sub=="list": countdown_list()
        else: cp.print_help()
    elif args.cmd=="schedule":
        if args.sub=="import": 
            fp=Path(args.file)
            if fp.suffix==".json": _w(_sf(),json.loads(fp.read_text(encoding="utf-8")))
            elif fp.suffix==".csv":
                import csv
                data=[{"day":int(r["day"]),"time":r["time"],"course":r["course"],"teacher":r.get("teacher",""),"location":r.get("location",""),"weeks":r.get("weeks","1-16")} for r in csv.DictReader(fp.read_text(encoding="utf-8").splitlines())]
                _w(_sf(),data)
            print(f"✅ 已导入")
        elif args.sub=="show":
            sem=_cs(); data=_r(_sf(sem))
            if not data: print("📭 课表为空"); return
            for d in range(1,8):
                courses=sorted([c for c in data if c["day"]==d],key=lambda c:c["time"])
                if courses:
                    print(f"\n【{WEEKDAYS[d-1]}】")
                    for c in courses: print(f"  {c['time']} {c['course']} {c.get('teacher','')} @ {c.get('location','')}")
        elif args.sub=="today":
            sem=_cs(); dow=_today().weekday(); data=_r(_sf(sem))
            courses=sorted([c for c in data if c["day"]==dow+1],key=lambda c:c["time"])
            print(f"\n📅 {WEEKDAYS[dow]}")
            if courses:
                for c in courses: print(f"  {c['time']} {c['course']} @ {c.get('location','')}")
            else: print("🎉 今天没有课！")
    elif args.cmd=="homework":
        sem=_cs()
        if args.sub=="add":
            data=_r(_hf(sem)); c=input("课程: ").strip(); t=input("标题: ").strip(); d=input("截止日期: ").strip()
            data.append({"id":max([h.get("id",0) for h in data],default=0)+1,"course":c,"title":t,"deadline":d,"done":False,"note":""})
            _w(_hf(sem),data); print("✅ 已添加")
        elif args.sub=="list":
            data=_r(_hf(sem)); pending=[h for h in data if not h["done"]]
            for h in sorted(pending,key=lambda x:x["deadline"]):
                days=(_parse_date(h["deadline"])-_today()).days
                u="🔴" if days<=1 else ("🟡" if days<=3 else "🟢")
                print(f"  [{h['id']}] {u} {h['course']}: {h['title']} (剩{days}天)")
        elif args.sub=="done":
            data=_r(_hf(sem))
            for h in data:
                if h["id"]==args.id: h["done"]=True; _w(_hf(sem),data); print("✅"); return
    elif args.cmd=="exam":
        sem=_cs()
        if args.sub=="add":
            data=_r(_ef(sem)); c=input("课程: ").strip(); t=input("类型: ").strip(); d=input("日期: ").strip()
            data.append({"id":max([e.get("id",0) for e in data],default=0)+1,"course":c,"type":t,"date":d,"location":"","note":""})
            _w(_ef(sem),data); print("✅ 已添加")
        elif args.sub=="list":
            data=sorted(_r(_ef(sem)),key=lambda x:x["date"])
            for e in data:
                days=(_parse_date(e["date"])-_today()).days
                print(f"  [{e['id']}] {'🔴' if days<=3 else '🟡'} {e['course']} {e['type']}: {e['date']} (剩{days}天)")
        elif args.sub=="countdown":
            data=sorted([e for e in _r(_ef(sem)) if _parse_date(e["date"])>=_today()],key=lambda x:x["date"])
            for e in data:
                days=(_parse_date(e["date"])-_today()).days
                bar="▓"*min(days,30)+"░"*max(30-days,0)
                print(f"\n  {e['course']} {e['type']}\n  {e['date']} 剩{days}天\n  [{bar}]")
    elif args.cmd=="semester":
        if args.sub=="new": _sc(args.name); _sd(args.name).mkdir(parents=True,exist_ok=True); init(); print(f"✅ 已创建学期 {args.name}")
        elif args.sub=="switch": _sc(args.name); print(f"✅ 已切换到 {args.name}")
        elif args.sub=="list":
            d=BASE/"semesters"
            if d.exists():
                for sd in sorted(d.iterdir()):
                    if sd.is_dir(): print(f"  {'👉' if sd.name==_cs() else '  '} {sd.name}")


if __name__=="__main__":
    main()
