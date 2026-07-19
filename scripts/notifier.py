#!/usr/bin/env python3
"""
大学生助手 v1.1 - 桌面通知服务
跨平台：Windows / macOS / Linux

用法：
  python3 notifier.py              # 后台常驻，每30分钟检查
  python3 notifier.py --once        # 单次检查并通知
  python3 notifier.py --test        # 发送测试通知
"""

import sys
import os
import time
import json
from datetime import datetime, date, timedelta
from pathlib import Path

# 添加 engine 模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import get_remind_data, get_current_semester, BASE_DIR, WEEKDAYS_CN


def notify(title: str, message: str, timeout: int = 10):
    """发送桌面通知"""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="大学生助手",
            timeout=timeout,
        )
        print(f"🔔 通知已发送: {title}")
        return True
    except Exception as e:
        print(f"⚠️ 通知发送失败: {e}")
        # 降级：打印到控制台
        print(f"\n{'='*40}")
        print(f"🔔 {title}")
        print(f"   {message}")
        print(f"{'='*40}\n")
        return False


def check_and_notify():
    """检查并发送通知"""
    try:
        data = get_remind_data()
    except Exception as e:
        print(f"⚠️ 获取数据失败: {e}")
        return

    notifications_sent = 0

    # 1. 明天有课吗？（晚上 21:00 提醒）
    now = datetime.now()
    if 21 <= now.hour <= 22:
        tomorrow_dow = (date.today().weekday() + 1) % 7
        schedule = data.get("courses", [])  # 这是今天的，我们需要明天的
        # 从文件读明天的课
        sem = get_current_semester()
        import json as _json
        sf = BASE_DIR / "semesters" / sem / "schedule.json"
        if sf.exists():
            with open(sf) as f:
                all_courses = _json.load(f)
            tomorrow_courses = [c for c in all_courses if c["day"] == tomorrow_dow + 1]
            if tomorrow_courses:
                names = "、".join(c["course"] for c in sorted(tomorrow_courses, key=lambda c: c["time"])[:3])
                if len(tomorrow_courses) > 3:
                    names += f"等{len(tomorrow_courses)}门课"
                notify("📅 明天课程提醒", f"明天有 {names}")

    # 2. 作业即将到期
    for h in data.get("urgent_homework", []):
        days = h["days_left"]
        if days <= 1 and days >= 0:
            notify("📝 作业即将截止！", f"{h['course']}: {h['title']} (还剩 {days} 天)", timeout=15)
            notifications_sent += 1

    # 3. 考试临近
    for item in data.get("near_exams", []):
        days = item["days"]
        if days <= 3:
            notify("⏰ 考试临近！", f"{item['exam']['course']} {item['exam']['type']} 还剩 {days} 天！", timeout=15)
            notifications_sent += 1

    if notifications_sent == 0:
        print(f"[{now.strftime('%H:%M')}] 检查完成，无需紧急通知")

    return notifications_sent


def test_notify():
    """发送测试通知"""
    notify("🎓 大学生助手", "桌面通知功能正常！如果你看到这条消息，说明一切 OK。", timeout=5)


def main():
    if "--test" in sys.argv:
        test_notify()
        return

    if "--once" in sys.argv:
        print("🔍 单次检查...")
        check_and_notify()
        return

    print("🔔 大学生助手通知服务已启动")
    print(f"   每 30 分钟自动检查作业和考试")
    print(f"   按 Ctrl+C 停止\n")

    try:
        while True:
            check_and_notify()
            time.sleep(1800)  # 30 分钟
    except KeyboardInterrupt:
        print("\n👋 通知服务已停止")


if __name__ == "__main__":
    main()
