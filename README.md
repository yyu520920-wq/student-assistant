# 🎓 大学生全能助手 v1.1

> 基于**滴答清单**深度定制 — 专为大学生打造的时间管理与学习助手

## ✨ 功能模块

### 📝 任务管理（对标滴答清单）
- **任务 CRUD**：添加、查看、完成、删除
- **子任务**：每个任务支持多级子任务，可单独标记完成
- **优先级**：🔴高 / 🟡中 / 🟢低 / ⚪无
- **标签**：自由标签分类，如 `#数学` `#作业` `#社团`
- **截止日期 & 提醒**：支持设置截止时间和提醒时间
- **重复任务**：支持 daily/weekly/monthly/yearly 重复

### 📋 清单分类
- 默认 4 个清单：📥收集箱 / 📚学习 / 🏠生活 / 🚀项目
- 支持自定义创建新清单，每个清单独立图标和颜色

### 🔲 四象限视图（Eisenhower 矩阵）
- 🔥 重要且紧急 → 立即做
- ⭐ 重要不紧急 → 计划做
- ⏰ 不重要紧急 → 委托做
- 💤 不重要不紧急 → 尽量不做

### 🔍 智能过滤器
- 今天要做的事
- 最近 7 天到期
- 高优先级任务
- 按标签筛选

### ✅ 习惯打卡
- 每日/每周习惯设定
- 🔥 连续天数统计
- 打卡日历追踪
- 3 个示例习惯：早起、阅读、运动

### 🍅 番茄专注
- 25/45/15 分钟可选
- 关联具体任务
- 统计总次数和总时长
- 今日番茄数统计

### 🎯 倒数日
- 考试、假期、生日等倒计时
- 支持每年重复（如生日）
- 🔴🟡🟢 颜色标识紧急度

### 🏫 课表管理
- JSON/CSV 格式导入
- 按天分组查看
- 今日课程快速查看
- 9 门示例课程预置

### 📝 作业管理
- 添加/查看/标记完成
- 按截止日期排序
- 剩余天数标识

### 📅 考试管理
- 添加/查看考试
- 可视化倒计时进度条 `▓▓▓░░░`
- 临近考试自动提醒

### 📊 今日概览
- 今日课程汇总
- 今日待办任务
- 习惯打卡状态
- 临近考试提醒（14天内）

### 🔄 多学期管理
- 创建/切换学期
- 数据完全隔离
- 默认学期预置

### 📦 数据导出
- 一键导出全部数据为 JSON
- 含任务、清单、习惯、番茄、倒数日、课表、作业、考试

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/yyu520920-wq/student-assistant.git
cd student-assistant
```

### 2. 初始化
```bash
python3 scripts/engine.py init
```
自动创建示例数据：4个清单、4个任务、3个习惯、3个倒数日、9门课、2个作业、2场考试

### 3. 开始使用

#### CLI 命令行
```bash
# 今日概览
python3 scripts/engine.py today

# 查看任务
python3 scripts/engine.py task list

# 添加任务（交互式）
python3 scripts/engine.py task add

# 四象限视图
python3 scripts/engine.py eisenhower

# 习惯打卡
python3 scripts/engine.py habit list

# 番茄专注 25 分钟
python3 scripts/engine.py pomodoro start

# 倒数日
python3 scripts/engine.py countdown list

# 今日课表
python3 scripts/engine.py schedule today

# 考试倒计时
python3 scripts/engine.py exam countdown

# 导出全部数据
python3 scripts/engine.py export
```

#### Web 可视化界面
```bash
# 安装依赖
pip3 install flask

# 启动服务
python3 web/server.py

# 浏览器访问
# http://localhost:5000
```

Web 界面包含：
- 📅 今日概览（统计卡片 + 课程/任务/习惯/考试）
- 📝 任务管理（添加/筛选/完成/删除）
- 📆 日历视图
- 📋 看板视图（按清单分列）
- 🔲 四象限视图
- ✅ 习惯打卡
- 🍅 番茄专注（含倒计时动画）
- 🎯 倒数日
- 🏫 课表
- 📊 数据仪表盘（趋势图）

## 📁 项目结构

```
student-assistant/
├── SKILL.md              # AI Skill 入口（8 个问题标准）
├── README.md             # 项目说明（本文件）
├── LICENSE               # MIT 许可证
├── scripts/
│   └── engine.py         # 核心引擎（600+ 行，纯标准库）
├── web/
│   ├── server.py         # Flask Web API 服务（15+ REST 端点）
│   ├── templates/
│   │   └── index.html    # Web 前端页面
│   └── static/
│       ├── css/style.css # 滴答清单风格 UI
│       └── js/app.js     # 前端 JS SPA 应用
├── references/           # 参考文档
└── assets/               # 素材资源
```

## 📊 数据存储

所有数据存储在 `~/.student-assistant/` 目录下：

```
~/.student-assistant/
├── current.json              # 当前学期
└── semesters/
    └── 默认学期/
        ├── tasks.json        # 任务数据
        ├── lists.json        # 清单数据
        ├── habits.json       # 习惯数据
        ├── pomodoro.json     # 番茄记录
        ├── countdowns.json   # 倒数日
        ├── schedule.json     # 课表
        ├── homework.json     # 作业
        └── exam.json         # 考试
```

## 🔧 技术栈

- **Python 3.11+**（纯标准库，零依赖即可运行 CLI）
- **Flask**（Web 界面依赖）
- **JSON** 文件存储（无需数据库）
- 原生 **HTML/CSS/JS**（Web 前端）

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)
