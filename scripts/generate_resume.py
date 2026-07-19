#!/usr/bin/env python3
"""
大学生助手 v1.1 - 简历生成引擎
支持：AI 对话触发 / 交互式填写 / Web 界面填写
输出：精美排版 .docx 简历

用法：
  python3 generate_resume.py                      # 交互式填写
  python3 generate_resume.py --from-json data.json # 从JSON生成
  python3 generate_resume.py --template classic    # 指定模板
"""

import sys, os, json
from datetime import date
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Inches, Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
except ImportError:
    print("❌ 请安装 python-docx: pip install python-docx")
    sys.exit(1)

# ── 模板 ──
TEMPLATES = {
    "classic": {"primary": RGBColor(0x1A, 0x56, 0xDB), "name": "经典蓝"},
    "modern": {"primary": RGBColor(0x33, 0x33, 0x33), "name": "现代黑"},
    "warm": {"primary": RGBColor(0xE8, 0x6B, 0x2C), "name": "暖橙"},
}


def add_section_header(doc, title, color):
    """添加分区标题"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(title)
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = color
    # 下划线
    p_border = p.paragraph_format
    # 底部横线
    line = doc.add_paragraph()
    line.paragraph_format.space_before = Pt(0)
    line.paragraph_format.space_after = Pt(8)
    run2 = line.add_run("─" * 60)
    run2.font.size = Pt(6)
    run2.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)


def add_bullet(doc, text, bold_prefix=""):
    """添加要点"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.5)
    if bold_prefix:
        run_b = p.add_run(f"{bold_prefix}：")
        run_b.font.bold = True
        run_b.font.size = Pt(10.5)
    run = p.add_run(text if not bold_prefix else f" {text}")
    run.font.size = Pt(10.5)


def generate_resume(data: dict, template_name: str = "classic", output: str = "个人简历.docx"):
    """生成简历 docx"""
    theme = TEMPLATES.get(template_name, TEMPLATES["classic"])
    doc = Document()

    # 页面设置
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # ── 头部：姓名 + 联系方式 ──
    name = data.get("name", "姓名")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(name)
    run.font.size = Pt(26)
    run.font.bold = True
    run.font.color.rgb = theme["primary"]

    # 联系方式
    contact_items = []
    if data.get("phone"): contact_items.append(data["phone"])
    if data.get("email"): contact_items.append(data["email"])
    if data.get("city"): contact_items.append(data["city"])
    if data.get("age"): contact_items.append(f"{data['age']}岁")
    if contact_items:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(12)
        run2 = p2.add_run(" | ".join(contact_items))
        run2.font.size = Pt(10)
        run2.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    # ── 教育背景 ──
    education = data.get("education", [])
    if education:
        add_section_header(doc, "教育背景", theme["primary"])
        for edu in education:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(2)
            run_school = p.add_run(f"{edu.get('school','')}  ")
            run_school.font.bold = True
            run_school.font.size = Pt(11)
            run_major = p.add_run(f"{edu.get('major','')}  {edu.get('degree','')}")
            run_major.font.size = Pt(11)
            p2 = doc.add_paragraph()
            run_date = p2.add_run(f"{edu.get('start','')} - {edu.get('end','')}")
            run_date.font.size = Pt(10)
            run_date.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
            if edu.get("gpa"):
                run_gpa = p2.add_run(f"  |  GPA: {edu['gpa']}")
                run_gpa.font.size = Pt(10)
                run_gpa.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    # ── 实习/项目经历 ──
    experiences = data.get("experiences", [])
    if experiences:
        add_section_header(doc, "项目经历" if data.get("is_student") else "工作经历", theme["primary"])
        for exp in experiences:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            run_role = p.add_run(f"{exp.get('role','')}  ")
            run_role.font.bold = True
            run_role.font.size = Pt(11)
            run_org = p.add_run(f"@ {exp.get('organization','')}")
            run_org.font.size = Pt(11)
            run_org.font.color.rgb = theme["primary"]
            p2 = doc.add_paragraph()
            run_date = p2.add_run(f"{exp.get('start','')} - {exp.get('end','')}")
            run_date.font.size = Pt(10)
            run_date.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
            for detail in exp.get("details", []):
                add_bullet(doc, detail)

    # ── 技能 ──
    skills = data.get("skills", [])
    if skills:
        add_section_header(doc, "专业技能", theme["primary"])
        for sk in skills:
            add_bullet(doc, sk.get("detail", ""), sk.get("name", ""))

    # ── 荣誉奖项 ──
    awards = data.get("awards", [])
    if awards:
        add_section_header(doc, "荣誉奖项", theme["primary"])
        for aw in awards:
            add_bullet(doc, f"{aw.get('name','')} ({aw.get('date','')})")

    # ── 自我评价 ──
    if data.get("summary"):
        add_section_header(doc, "自我评价", theme["primary"])
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.5)
        run = p.add_run(data["summary"])
        run.font.size = Pt(10.5)

    doc.save(output)
    print(f"✅ 简历已生成: {output}")
    print(f"📄 模板: {theme['name']}")
    print(f"💡 用 Word/WPS 打开后可直接打印或导出 PDF")


def interactive_mode():
    """交互式填写简历"""
    print("\n📄 简历生成器\n")

    data = {}
    data["name"] = input("姓名: ").strip()
    data["phone"] = input("电话: ").strip()
    data["email"] = input("邮箱: ").strip()
    data["city"] = input("城市: ").strip()
    data["age"] = input("年龄: ").strip()
    data["is_student"] = input("是否在校生? (y/n): ").strip().lower() == "y"

    # 教育背景
    print("\n📚 教育背景 (空行结束):")
    edu_list = []
    while True:
        school = input("  学校: ").strip()
        if not school: break
        major = input("  专业: ").strip()
        degree = input("  学位 (本科/硕士/博士): ").strip()
        start = input("  入学年份: ").strip()
        end = input("  毕业年份: ").strip()
        gpa = input("  GPA (可选): ").strip()
        edu_list.append({"school": school, "major": major, "degree": degree, "start": start, "end": end, "gpa": gpa})
    data["education"] = edu_list

    # 经历
    print("\n💼 项目/实习经历 (空行结束):")
    exp_list = []
    while True:
        role = input("  角色/职位: ").strip()
        if not role: break
        org = input("  组织/公司: ").strip()
        start = input("  开始时间: ").strip()
        end = input("  结束时间: ").strip()
        print("  工作内容 (一行一个, 空行结束):")
        details = []
        while True:
            d = input("    • ").strip()
            if not d: break
            details.append(d)
        exp_list.append({"role": role, "organization": org, "start": start, "end": end, "details": details})
    data["experiences"] = exp_list

    # 技能
    print("\n🛠️ 技能 (空行结束):")
    skills = []
    while True:
        name = input("  技能名: ").strip()
        if not name: break
        detail = input("  熟练度/描述: ").strip()
        skills.append({"name": name, "detail": detail})
    data["skills"] = skills

    # 奖项
    print("\n🏆 荣誉奖项 (空行结束):")
    awards = []
    while True:
        name = input("  奖项: ").strip()
        if not name: break
        d = input("  时间: ").strip()
        awards.append({"name": name, "date": d})
    data["awards"] = awards

    data["summary"] = input("\n📝 自我评价: ").strip()

    print("\n模板: 1=经典蓝 2=现代黑 3=暖橙")
    t = input("选择 (1/2/3, 默认1): ").strip() or "1"
    template = {"1": "classic", "2": "modern", "3": "warm"}.get(t, "classic")

    output = input("输出文件名 (默认: 个人简历.docx): ").strip() or "个人简历.docx"

    generate_resume(data, template, output)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="简历生成器")
    parser.add_argument("--from-json", "-j", help="从 JSON 文件读取数据")
    parser.add_argument("--template", "-t", default="classic", choices=["classic", "modern", "warm"])
    parser.add_argument("--output", "-o", default="个人简历.docx")
    parser.add_argument("--interactive", "-i", action="store_true")
    args = parser.parse_args()

    if args.from_json:
        with open(args.from_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        generate_resume(data, args.template, args.output)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
