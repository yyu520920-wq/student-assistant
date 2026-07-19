#!/usr/bin/env python3
"""
大学生助手 v1.1 - PPT 生成引擎
AI 对话触发，自动生成学术汇报/社团展示/课堂报告 PPT

用法：
  python3 generate_ppt.py "主题" --type academic -o 汇报.pptx
  python3 generate_ppt.py --interactive  # 交互式输入

模板类型：
  academic  - 学术汇报（蓝色）
  club      - 社团展示（紫色）
  class     - 课堂报告（绿色）
"""

import sys
import os
from datetime import date
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ── 配色方案 ──
THEMES = {
    "academic": {"primary": RGBColor(0x1A, 0x56, 0xDB), "secondary": RGBColor(0xE8, 0xF0, 0xFE), "bg": RGBColor(0xFF, 0xFF, 0xFF)},
    "club": {"primary": RGBColor(0x7C, 0x3A, 0xED), "secondary": RGBColor(0xF3, 0xE8, 0xFF), "bg": RGBColor(0xFF, 0xFF, 0xFF)},
    "class": {"primary": RGBColor(0x05, 0x9A, 0x69), "secondary": RGBColor(0xEC, 0xFD, 0xF5), "bg": RGBColor(0xFF, 0xFF, 0xFF)},
}


def add_slide(prs, layout_idx=1):
    """添加空白幻灯片"""
    layout = prs.slide_layouts[layout_idx]
    return prs.slides.add_slide(layout)


def add_title_slide(prs, title, subtitle, theme):
    """封面页"""
    slide = add_slide(prs, 6)  # blank
    # 背景色块
    left, top, width, height = Inches(0), Inches(0), Inches(10), Inches(7.5)
    shape = slide.shapes.add_shape(1, left, top, width, height)  # rectangle
    shape.fill.solid()
    shape.fill.fore_color.rgb = theme["primary"]
    shape.line.fill.background()

    # 标题
    txBox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p.alignment = PP_ALIGN.CENTER

    # 副标题
    txBox2 = slide.shapes.add_textbox(Inches(1), Inches(4.2), Inches(8), Inches(1))
    tf2 = txBox2.text_frame
    p2 = tf2.paragraphs[0]
    p2.text = subtitle
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(0xE0, 0xE0, 0xFF)
    p2.alignment = PP_ALIGN.CENTER

    # 日期
    txBox3 = slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(8), Inches(0.5))
    tf3 = txBox3.text_frame
    p3 = tf3.paragraphs[0]
    p3.text = date.today().strftime("%Y年%m月%d日")
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(0xC0, 0xC0, 0xE0)
    p3.alignment = PP_ALIGN.CENTER


def add_toc_slide(prs, items, theme):
    """目录页"""
    slide = add_slide(prs, 6)
    txBox = slide.shapes.add_textbox(Inches(1), Inches(0.5), Inches(8), Inches(1))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "目录"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = theme["primary"]

    for i, item in enumerate(items):
        txBox2 = slide.shapes.add_textbox(Inches(1.5), Inches(1.8 + i * 0.8), Inches(7), Inches(0.6))
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = f"{i + 1:02d}  {item}"
        p2.font.size = Pt(20)
        p2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)


def add_content_slide(prs, title, bullets, theme):
    """内容页"""
    slide = add_slide(prs, 6)
    # 顶部色条
    shape = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.08))
    shape.fill.solid()
    shape.fill.fore_color.rgb = theme["primary"]
    shape.line.fill.background()

    # 标题
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(0.8))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = theme["primary"]

    # 要点
    txBox2 = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True

    for i, bullet in enumerate(bullets):
        if i == 0:
            p = tf2.paragraphs[0]
        else:
            p = tf2.add_paragraph()
        p.text = f"• {bullet}"
        p.font.size = Pt(18)
        p.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        p.space_after = Pt(12)


def add_summary_slide(prs, main_point, theme):
    """总结页"""
    slide = add_slide(prs, 6)
    shape = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(7.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = theme["primary"]
    shape.line.fill.background()

    txBox = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(1))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "总结"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p.alignment = PP_ALIGN.CENTER

    txBox2 = slide.shapes.add_textbox(Inches(1), Inches(3), Inches(8), Inches(2))
    tf2 = txBox2.text_frame
    p2 = tf2.paragraphs[0]
    p2.text = main_point
    p2.font.size = Pt(24)
    p2.font.color.rgb = RGBColor(0xE0, 0xE0, 0xFF)
    p2.alignment = PP_ALIGN.CENTER

    txBox3 = slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(8), Inches(0.5))
    tf3 = txBox3.text_frame
    p3 = tf3.paragraphs[0]
    p3.text = "感谢聆听  ·  欢迎提问"
    p3.font.size = Pt(18)
    p3.font.color.rgb = RGBColor(0xC0, 0xC0, 0xE0)
    p3.alignment = PP_ALIGN.CENTER


def generate_ppt(title: str, subtitle: str, toc_items: list, content_slides: list, summary: str, ppt_type: str, output: str):
    """生成完整 PPT"""
    theme = THEMES.get(ppt_type, THEMES["academic"])
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # 封面
    add_title_slide(prs, title, subtitle, theme)

    # 目录
    if toc_items:
        add_toc_slide(prs, toc_items, theme)

    # 内容页
    for cs in content_slides:
        add_content_slide(prs, cs.get("title", ""), cs.get("bullets", []), theme)

    # 总结
    if summary:
        add_summary_slide(prs, summary, theme)

    prs.save(output)
    print(f"✅ PPT 已生成: {output}")
    print(f"📊 共 {len(prs.slides)} 页")


def interactive_mode():
    """交互式创建 PPT"""
    print("\n🎨 PPT 生成器")
    title = input("PPT 标题: ").strip()
    subtitle = input("副标题 (可选): ").strip()
    print("\n模板类型: 1=学术汇报 2=社团展示 3=课堂报告")
    t = input("选择 (1/2/3, 默认1): ").strip() or "1"
    ppt_type = {"1": "academic", "2": "club", "3": "class"}.get(t, "academic")

    print("\n目录项 (一行一个, 空行结束):")
    toc = []
    while True:
        line = input().strip()
        if not line:
            break
        toc.append(line)

    print("\n内容页 (每页先输入标题, 再输入要点, 空行进入下一页, 输入 'done' 结束):")
    content = []
    while True:
        page_title = input("页面标题 (或 'done' 结束): ").strip()
        if page_title.lower() == "done":
            break
        bullets = []
        print(f"  要点 (空行结束):")
        while True:
            b = input("    • ").strip()
            if not b:
                break
            bullets.append(b)
        content.append({"title": page_title, "bullets": bullets})

    summary = input("\n总结语: ").strip()
    output = input("输出文件名 (默认: 演示文稿.pptx): ").strip() or "演示文稿.pptx"

    generate_ppt(title, subtitle, toc, content, summary, ppt_type, output)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="PPT 生成器")
    parser.add_argument("title", nargs="?", help="PPT 标题")
    parser.add_argument("--type", "-t", default="academic", choices=["academic", "club", "class"], help="模板类型")
    parser.add_argument("--output", "-o", default="演示文稿.pptx", help="输出文件名")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式模式")
    args = parser.parse_args()

    if args.interactive or not args.title:
        interactive_mode()
        return

    # 快速模式：只给标题，生成简单结构
    generate_ppt(
        title=args.title,
        subtitle="",
        toc_items=["背景介绍", "主要内容", "总结展望"],
        content_slides=[
            {"title": "背景介绍", "bullets": ["研究背景与意义", "国内外研究现状", "研究目标"]},
            {"title": "主要内容", "bullets": ["核心观点一", "核心观点二", "核心观点三", "数据与案例支撑"]},
            {"title": "总结展望", "bullets": ["主要结论", "创新点", "未来展望"]},
        ],
        summary="感谢各位的聆听，欢迎提出宝贵意见！",
        ppt_type=args.type,
        output=args.output,
    )


if __name__ == "__main__":
    main()
