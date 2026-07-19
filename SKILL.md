---
name: student-assistant
description: |
  大学生全能助手 v1.0 — 课表导入、作业管理、考试倒计时、每日提醒。
  触发词：课表 | 导入课表 | 我的课表 | 今天有什么课 | 作业 | 添加作业 | 我的作业 |
  标记完成 | 考试 | 添加考试 | 考试倒计时 | 还有多久考试 | 倒计时 | 提醒 | 今日提醒 |
  今天要做什么 | 初始化 | init
---

# 大学生全能助手 v1.0

> **核心原则**：先理解用户意图 → 匹配对应命令 → 执行命令 → 展示结果 → 给出下一步建议

## 场景速查表

| 用户说 | 执行命令 | 说明 |
|--------|----------|------|
| 初始化 / 第一次用 | `python3 scripts/student_engine.py init` | 创建示例数据 |
| 导入课表 | `python3 scripts/student_engine.py schedule import <文件>` | 支持 .json / .csv |
| 我的课表 / 查看课表 | `python3 scripts/student_engine.py schedule show` | 完整周课表 |
| 今天有什么课 | `python3 scripts/student_engine.py schedule today` | 今日课程 |
| 添加作业 | `python3 scripts/student_engine.py homework add` | 交互式输入 |
| 我的作业 / 查看作业 | `python3 scripts/student_engine.py homework list` | 待完成作业 |
| 标记完成 / 做完了 | `python3 scripts/student_engine.py homework done <id>` | 标记作业完成 |
| 删除作业 | `python3 scripts/student_engine.py homework delete <id>` | 移除作业 |
| 添加考试 | `python3 scripts/student_engine.py exam add` | 交互式输入 |
| 考试列表 | `python3 scripts/student_engine.py exam list` | 所有考试 |
| 考试倒计时 / 还有多久 | `python3 scripts/student_engine.py exam countdown` | 可视化倒计时 |
| 删除考试 | `python3 scripts/student_engine.py exam delete <id>` | 移除考试 |
| 今日提醒 / 今天做什么 | `python3 scripts/student_engine.py remind` | 课程+作业+考试汇总 |

## 全局规则

1. **先初始化**：用户第一次使用时，必须先运行 `init` 创建数据目录
2. **命令即答案**：Skill 的本质是帮用户执行命令，不要自己瞎编数据
3. **展示结果后给建议**：每次执行完命令，附带 1 个下一步操作建议
4. **不编造信息**：课表、作业、考试日期必须以用户提供或已存储的数据为准
5. **路径正确**：始终在项目根目录（SKILL.md 所在目录）执行脚本

## 详细工作流

### 工作流 1：课表导入

```
用户说"导入课表"
  ├── 情况A：用户提供了文件路径
  │     └── 执行 schedule import <文件路径>
  │     └── 导入后自动执行 schedule show 让用户确认
  ├── 情况B：用户没有文件，想手动输入
  │     └── 引导用户按 JSON 格式提供课程信息
  │     └── 帮用户生成 JSON 文件
  │     └── 执行 schedule import
  └── 情况C：用户从教务系统导出了 CSV/Excel
        └── 引导用户调整格式（参考 references/schedule-guide.md）
        └── 执行导入
```

### 工作流 2：作业管理

```
用户说"添加作业"
  ├── 用户已提供完整信息（课程+标题+截止日期）
  │     └── 直接帮用户构造 JSON 写入 homework.json
  │     └── 显示添加结果
  ├── 用户只说了部分信息（如"高数作业周五交"）
  │     └── 提取已知信息，追问缺失字段
  │     └── 补全后添加
  └── 用户没有具体信息
        └── 运行 homework add 交互式输入

用户说"我的作业"
  └── 执行 homework list
  └── 对 🔴 标记的紧急作业给出额外提醒
```

### 工作流 3：考试倒计时

```
用户说"考试倒计时"
  └── 执行 exam countdown
  └── 对 3 天内的考试用 🔴 特别警示
  └── 建议用户设置复习计划
```

### 工作流 4：每日提醒

```
用户说"今日提醒"
  └── 执行 remind
  └── 汇总三类信息：课程、作业、考试
  └── 如果全部清空（无课+无作业+无考试），恭喜用户
```

## 输出标准

- **课表展示**：按天分组，按时间排序，包含时间/课程/教师/地点/周次
- **作业列表**：按截止日期排序，用 🔴(≤1天) 🟡(≤3天) 🟢(>3天) 标识紧急度
- **考试倒计时**：可视化进度条 `▓▓▓░░░`，标注剩余天数
- **每日提醒**：三个板块（课程/作业/考试），每板块显示数量统计

## 常见陷阱

- **不要**在未初始化时直接执行其他命令（会提示数据为空，这是正常的）
- **不要**编造用户的课表、作业、考试信息
- **不要**修改 `~/.student-assistant/` 下的 JSON 文件结构
- **提醒**用户：首次使用务必运行 `init`
- **提醒**用户：每天早晨运行 `remind` 查看今日安排

## 参考文档

| 文档 | 内容 | 何时加载 |
|------|------|----------|
| `references/schedule-guide.md` | 课表导入格式详解（JSON/CSV 字段说明） | 用户导入课表遇到格式问题时 |
