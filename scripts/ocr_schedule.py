#!/usr/bin/env python3
"""
大学生助手 v1.1 - OCR 课表识别
支持：easyocr（推荐，纯 Python）、pytesseract（备选）

用法：
  python3 ocr_schedule.py screenshot.png              # 识别课表截图
  python3 ocr_schedule.py screenshot.png --auto-import # 识别并自动导入
  python3 ocr_schedule.py screenshot.png --output result.json  # 输出到文件
"""

import sys
import os
import json
import re
from pathlib import Path

# 添加 engine 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def extract_schedule_easyocr(image_path: str) -> list:
    """使用 easyocr 识别课表"""
    try:
        import easyocr
    except ImportError:
        print("❌ 请先安装 easyocr: pip install easyocr")
        sys.exit(1)

    print("🔍 正在加载 OCR 模型（首次运行会下载，约 100MB）...")
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    print("🔍 正在识别图片...")

    result = reader.readtext(image_path)
    texts = [item[1] for item in result]

    print(f"📝 识别到 {len(texts)} 个文本片段:")
    for t in texts:
        print(f"  • {t}")

    # 尝试解析课表
    courses = _parse_schedule_texts(texts)
    return courses


def _parse_schedule_texts(texts: list) -> list:
    """从 OCR 文本中提取课表"""
    courses = []
    weekdays_map = {
        "周一": 1, "星期一": 1, "周一": 1, "Mon": 1,
        "周二": 2, "星期二": 2, "Tue": 2,
        "周三": 3, "星期三": 3, "Wed": 3,
        "周四": 4, "星期四": 4, "Thu": 4,
        "周五": 5, "星期五": 5, "Fri": 5,
        "周六": 6, "星期六": 6, "Sat": 6,
        "周日": 7, "星期日": 7, "Sun": 7,
    }

    time_pattern = re.compile(r'(\d{1,2}:\d{2})\s*[-~至到]\s*(\d{1,2}:\d{2})')
    location_pattern = re.compile(r'(教\d|实验|机房|操场|体育|语音|多媒体).*')

    current_day = None
    for text in texts:
        text = text.strip()
        if not text:
            continue

        # 检测星期
        for kw, day_num in weekdays_map.items():
            if kw in text:
                current_day = day_num
                break

        # 检测时间段
        time_match = time_pattern.search(text)
        if time_match and current_day:
            time_str = f"{time_match.group(1)}-{time_match.group(2)}"

            # 尝试找课程名（通常在时间后面）
            rest = text[time_match.end():].strip()
            # 课程名通常是中文
            course_match = re.search(r'([\u4e00-\u9fa5]{2,}(?:\([^)]*\))?)', rest)
            course_name = course_match.group(1) if course_match else rest[:6]

            # 找教室
            loc_match = location_pattern.search(rest)
            location = loc_match.group(0) if loc_match else ""

            # 找教师
            teacher_match = re.search(r'([\u4e00-\u9fa5]{1,3}老师)', rest)
            teacher = teacher_match.group(1) if teacher_match else ""

            courses.append({
                "day": current_day,
                "time": time_str,
                "course": course_name,
                "teacher": teacher,
                "location": location,
                "weeks": "1-16",
            })

    return courses


def extract_schedule_tesseract(image_path: str) -> list:
    """使用 pytesseract 识别（备选方案）"""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        print("❌ 请先安装: pip install pytesseract Pillow")
        print("   还需要安装 tesseract: apt install tesseract-ocr tesseract-ocr-chi-sim")
        sys.exit(1)

    print("🔍 正在用 tesseract 识别...")
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')

    print("📝 识别结果:")
    print(text)

    texts = [line.strip() for line in text.split('\n') if line.strip()]
    return _parse_schedule_texts(texts)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="OCR 识别课表截图")
    parser.add_argument("image", help="课表截图路径")
    parser.add_argument("--engine", default="easyocr", choices=["easyocr", "tesseract"], help="OCR 引擎")
    parser.add_argument("--auto-import", action="store_true", help="识别后自动导入")
    parser.add_argument("--output", "-o", help="输出 JSON 文件")

    args = parser.parse_args()

    if not Path(args.image).exists():
        print(f"❌ 文件不存在: {args.image}")
        sys.exit(1)

    # 识别
    if args.engine == "tesseract":
        courses = extract_schedule_tesseract(args.image)
    else:
        courses = extract_schedule_easyocr(args.image)

    if not courses:
        print("\n⚠️ 未能识别出课表信息")
        print("💡 建议：")
        print("   1. 确保截图清晰、文字可辨认")
        print("   2. 裁剪掉无关区域，只保留课表表格")
        print("   3. 手动输入课表：对我说'添加课程'即可")
        return

    print(f"\n✅ 识别出 {len(courses)} 门课程:")
    for c in courses:
        print(f"  周{c['day']} {c['time']} {c['course']} {c['teacher']} {c['location']}")

    # 输出
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(courses, f, ensure_ascii=False, indent=2)
        print(f"\n📁 已保存到 {args.output}")

    # 自动导入
    if args.auto_import:
        from engine import schedule_import
        tmp_file = "/tmp/ocr_schedule.json"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(courses, f, ensure_ascii=False)
        schedule_import(tmp_file)

    # 确认
    if not args.auto_import and courses:
        print("\n💡 导入命令:")
        print(f"   python3 scripts/ocr_schedule.py {args.image} --auto-import")


if __name__ == "__main__":
    main()
