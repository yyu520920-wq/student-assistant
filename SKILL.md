---
name: student-assistant
description: |
  大学日程计划 v3.0 — 大学生全能助手，原创设计的学习效率与日程管理工具。非交互式参数驱动，AI 可直接调用。
  任务管理、子任务、优先级、标签、清单分类、四象限、番茄专注、习惯打卡、
  倒数日、智能过滤器、今日概览、课表、作业、考试、多学期管理、数据导出。
  支持移动端 Web UI（零依赖，手机直连查看和编辑计划）。
  触发词：任务 | 清单 | 番茄 | 习惯 | 打卡 | 倒数日 | 四象限 | 课表 | 作业 | 考试 | 今日概览 | 学期 | 复习计划 | 日程
---

# 📚 大学日程计划 v3.0

> 核心原则：匹配用户意图 → 调用 engine.py（参数式，无交互）→ 展示结果 → 给下一步建议
> 优先级统一：1=高🔴 2=中🟡 3=低🟢 0=无⚪
> Web UI：零依赖，`python start.py` 一键启动，手机同 WiFi 直连访问

## 01 / Name — 能力标识

`student-assistant`（对外名称：大学日程计划）— 非交互式参数驱动 + 移动端 Web UI

## 02 / Description — 何时加载

用户提到以下任一关键词时加载：

- **任务管理**：任务、待办、子任务、优先级、标签、清单、收集箱
- **番茄专注**：番茄、番茄钟、专注、计时
- **习惯打卡**：习惯、打卡、早起、阅读、运动
- **倒数日**：倒数、倒计时、还有多少天
- **四象限**：四象限、重要紧急、Eisenhower
- **课表考试**：课表、课程、作业、考试、考试倒计时、复习计划
- **今日概览**：今天有什么、今日概览、日程
- **学期管理**：学期、切换学期
- **Web 界面**：手机看、网页版、打开界面、启动服务

## 03 / Goal — 解决什么，不解决什么

**解决**：
- ✅ 任务管理（添加/列表/完成/删除/子任务/优先级/标签/四象限）
- ✅ 清单分类（收集箱/学习/生活/项目，可自定义）
- ✅ 番茄专注（记录完成的番茄钟 + 统计，不阻塞）
- ✅ 习惯打卡（每日/每周，连续天数统计）
- ✅ 倒数日（考试/假期/生日，支持每年重复）
- ✅ 四象限视图（重要紧急矩阵）
- ✅ 智能过滤器（今天/7天内/高优先级/按标签）
- ✅ 今日概览（课程+任务+习惯+考试+作业汇总）
- ✅ 课表管理（导入 JSON/CSV/查看/今日课程）
- ✅ 作业管理（添加/查看/完成/紧急提醒）
- ✅ 考试管理（添加/列表/可视化倒计时进度条）
- ✅ 多学期管理（创建/切换/数据隔离）
- ✅ 完整数据 JSON 导出（跨平台临时目录）
- ✅ **移动端 Web UI**（零依赖，手机直连查看和编辑，底部 Tab 导航）

**不解决**：
- ❌ 不登录学校教务系统自动获取课表
- ❌ 不替用户做最终决策
- ❌ 不编造学校政策、考试日期等不确定信息
- ❌ 不做真实倒计时阻塞（番茄钟改为记录模式，避免 AI 超时）

## 04 / Workflow — 执行顺序

```
用户表达需求
  → 匹配场景速查表
  → 执行对应 engine.py 命令（全部参数式，无 input 交互）
  → 展示结果
  → 给出 1 个下一步建议
```

### 调用约定

**Python 路径**：
- Linux/macOS：`python3`
- Windows：`python` 或完整路径
- 脚本路径：`<skill目录>/scripts/engine.py`

**所有命令都是参数驱动，不存在交互式 input。** AI 可直接拼接参数执行。

### 启动 Web 界面（移动端）

当用户想"在手机上看"、"打开网页版"、"启动服务"时：

```bash
python start.py            # 一键启动（init + web server + 显示手机访问地址）
python start.py 8080       # 指定端口
```

或 Windows 双击 `start.bat`。启动后终端显示局域网 IP，手机连同一 WiFi 即可访问。

### 场景速查表（CLI）

| 用户说 | 执行命令 |
|--------|----------|
| "初始化" / "开始使用" | `python scripts/engine.py init` |
| "今天有什么" / "今日概览" | `python scripts/engine.py today` |
| "添加任务 XXX" | `python scripts/engine.py task add --title "XXX" --priority 2 --due 2026-07-25 --tags 学习` |
| "查看任务" / "任务列表" | `python scripts/engine.py task list` |
| "完成任务 XXX" | `python scripts/engine.py task done <id>` |
| "删除任务 XXX" | `python scripts/engine.py task delete <id>` |
| "四象限" / "重要紧急" | `python scripts/engine.py eisenhower` |
| "今天要做的事" | `python scripts/engine.py filter --type today` |
| "7天内到期" | `python scripts/engine.py filter --type 7days` |
| "按标签 #数学" | `python scripts/engine.py filter --type tag --tag 数学` |
| "打卡" / "习惯" | `python scripts/engine.py habit list` |
| "给习惯 XXX 打卡" | `python scripts/engine.py habit checkin <id>` |
| "添加习惯 XXX" | `python scripts/engine.py habit add --name "XXX" --icon ✅ --goal daily` |
| "记录番茄 25 分钟" | `python scripts/engine.py pomodoro log --duration 25 --task "背单词"` |
| "番茄统计" | `python scripts/engine.py pomodoro stats` |
| "倒数日" / "倒计时" | `python scripts/engine.py countdown list` |
| "添加倒数日 XXX" | `python scripts/engine.py countdown add --title "XXX" --date 2026-12-25 --type exam` |
| "今天有什么课" | `python scripts/engine.py schedule today` |
| "查看课表" | `python scripts/engine.py schedule show` |
| "导入课表" | `python scripts/engine.py schedule import <file.json>` |
| "作业" | `python scripts/engine.py homework list` |
| "添加作业" | `python scripts/engine.py homework add --course "数学" --title "习题3" --deadline 2026-07-25` |
| "完成作业" | `python scripts/engine.py homework done <id>` |
| "考试" / "考试倒计时" | `python scripts/engine.py exam countdown` |
| "添加考试" | `python scripts/engine.py exam add --course "数学" --type "期中" --date 2026-08-15` |
| "清单" | `python scripts/engine.py list show` |
| "添加清单" | `python scripts/engine.py list add --name "实习" --icon 💼` |
| "导出数据" | `python scripts/engine.py export` |
| "切换学期" | `python scripts/engine.py semester switch <name>` |
| "新建学期" | `python scripts/engine.py semester new "大三上"` |
| "学期列表" | `python scripts/engine.py semester list` |
| "启动网页版" / "手机看" | `python start.py` |

### task add 完整参数

```
python scripts/engine.py task add \
  --title "任务标题"          # 必填
  --list work                 # 清单ID (inbox/work/personal/project/自定义)
  --priority 1                # 1=高🔴 2=中🟡 3=低🟢 0=无⚪ (默认2)
  --due 2026-07-25            # 截止日期 YYYY-MM-DD
  --tags SQL,数据库            # 标签逗号分隔
  --eisenhower important-urgent  # 四象限
  --repeat daily              # daily/weekly/monthly/yearly
  --note "备注"               # 备注
  --subtasks "复习笔记|做10道练习"  # 子任务用 | 分隔
```

## 05 / Rules — 必须遵守的判断

1. **先初始化**：首次使用必须先 `init`，否则数据目录为空
2. **参数式调用**：所有命令通过参数传值，禁止依赖交互式 input（engine.py 已无任何 input）
3. **展示后给建议**：每次执行完附带下一步建议
4. **不编造信息**：课表/作业/考试以用户提供或存储数据为准
5. **保护隐私**：涉及真实个人信息时提醒脱敏
6. **多学期隔离**：不同学期数据独立存储，切换学期后数据隔离
7. **优先级一致**：添加和显示统一用 1=高🔴 2=中🟡 3=低🟢 0=无⚪
8. **番茄不阻塞**：用 `pomodoro log` 记录已完成番茄，不做真实倒计时
9. **Web 零依赖**：Web 服务用 http.server 实现，无需 pip install 任何包

## 06 / Output — 怎样才算交付完成

- **任务列表**：含优先级图标（🔴🟡🟢⚪）、四象限标识、标签、子任务进度、截止日期
- **今日概览**：课程 + 今日任务 + 习惯打卡状态 + 临近考试 + 作业
- **四象限**：4 个象限分区，含任务数量和详情
- **习惯打卡**：图标 + 连续天数🔥 + 总次数 + 今日打卡状态
- **倒数日**：按日期排序，🔴🟡🟢 标识紧急度
- **考试倒计时**：可视化进度条 `▓▓▓░░░`
- **课表**：按天分组，时间排序，含课程/教师/地点/周次
- **作业**：按截止日期排序，剩余天数，🔴🟡🟢 紧急标识
- **数据导出**：完整 JSON 文件到系统临时目录，路径在输出中显示
- **Web 界面**：移动端 App 风格，底部 5 Tab（今日/任务/计划/习惯/我的）

## 07 / Gotchas — 常见陷阱

- **未初始化时执行命令** → 数据为空（正常），提示用户先 `init`
- **init 重复运行** → 已有数据不会被覆盖，安全
- **Windows 下 python3 不存在** → 用 `python` 或完整路径
- **番茄钟不要用 sleep** → v3.0 改为 `pomodoro log` 记录模式，避免 AI 调用超时
- **学期切换后数据不见** → 正常，数据按学期隔离，切回原学期即可
- **semester switch 不存在的学期** → 会报错提示先用 `semester new` 创建
- **filter --type tag 必须带 --tag** → 否则提示需要参数
- **手机访问不了 Web** → 检查：同一 WiFi、电脑防火墙放行端口、start.py 在运行
- **端口被占用** → `python start.py 8080` 换端口

## 08 / References — 细节去哪里按需读取

| 文档 | 内容 | 何时加载 |
|------|------|----------|
| `scripts/engine.py` | 核心引擎，所有 CLI 命令实现（纯标准库，零依赖） | 执行任何命令时 |
| `web/server.py` | Web API 服务（http.server，零依赖，20+ REST 端点） | 启动 Web 界面时 |
| `web/app.html` | 移动端前端单文件（HTML+CSS+JS 内联，底部 Tab 导航） | Web 界面渲染时 |
| `start.py` | 一键启动脚本（init + web server + 显示局域网 IP） | 用户要启动 Web 时 |
| `README.md` | 项目说明、小白教程、图文介绍、常见问题 | 用户了解项目时 |

> Web 界面零依赖（用 http.server 替代 Flask），下载即用。CLI 和 Web 均纯标准库实现。
