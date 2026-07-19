# 大学生全能助手 🎓

> 课表管理 · 作业追踪 · 考试倒计时 · 每日提醒
>
> 纯 Python 实现，零依赖，开箱即用

## 功能一览

| 功能 | 命令 | 说明 |
|------|------|------|
| 📅 **课表导入** | `schedule import` | 支持 JSON/CSV，从教务系统导出后直接导入 |
| 📅 **课表查看** | `schedule show / today` | 完整周课表 + 今日课程 |
| 📝 **作业管理** | `homework add/list/done` | 添加、查看、标记完成，按紧急度排序 |
| ⏰ **考试倒计时** | `exam add/list/countdown` | 可视化进度条，一目了然 |
| 🔔 **每日提醒** | `remind` | 一键汇总：课程 + 作业 + 考试 |

## 快速开始

### 环境要求

- Python 3.8 或以上版本
- 不需要安装任何第三方库（纯 Python 标准库）

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/student-assistant.git
cd student-assistant

# 2. 一键安装（创建示例数据）
bash install.sh
```

就这么简单，可以用了。

### 5 分钟体验

```bash
# 查看完整课表
python3 scripts/student_engine.py schedule show

# 查看今天有什么课
python3 scripts/student_engine.py schedule today

# 查看作业（按紧急度排序，🔴紧急 🟡注意 🟢安全）
python3 scripts/student_engine.py homework list

# 标记作业完成
python3 scripts/student_engine.py homework done 1

# 查看考试倒计时
python3 scripts/student_engine.py exam countdown

# 每日提醒（早上起床看一次就够了）
python3 scripts/student_engine.py remind
```

## 作为 AI Skill 使用

本项目同时也是一个标准的 AI Skill。把整个目录放进 AI 助手的 skills 目录，AI 就能自动帮你管理大学生活。

### 触发方式（对 AI 说）

| 你说 | AI 做的事 |
|------|----------|
| "导入课表" | 引导你导入课表文件 |
| "今天有什么课" | 显示今日课程 |
| "添加作业，高数习题，周五交" | 自动解析并添加作业 |
| "标记作业1完成" | 标记完成 |
| "考试倒计时" | 显示可视化倒计时 |
| "今日提醒" | 汇总今天所有事项 |

### Skill 目录结构

```
student-assistant/
├── SKILL.md                 ← AI Skill 入口（含工作流、规则、陷阱）
├── README.md                ← 项目说明（你正在读）
├── LICENSE                  ← MIT 开源许可
├── install.sh               ← 一键安装脚本
├── .gitignore
├── scripts/
│   ├── student_engine.py    ← 核心引擎（555行，纯标准库）
│   └── test.py              ← 自动化测试（32项）
├── references/
│   └── schedule-guide.md    ← 课表导入格式详解
└── assets/                  ← 素材目录（预留）
```

## 怎么测试好不好用

### 方法 1：自动化测试（推荐）

```bash
cd student-assistant
python3 scripts/test.py
```

会跑 32 项测试，覆盖所有功能模块 + 边界情况。看到 `🎉 全部测试通过！` 就说明一切正常。

### 方法 2：手动逐项测试

```bash
# 清空旧数据，重新初始化
rm -rf ~/.student-assistant
python3 scripts/student_engine.py init

# 测试课表
python3 scripts/student_engine.py schedule show     # 应该看到 10 门示例课程
python3 scripts/student_engine.py schedule today    # 应该看到今天的课程

# 测试作业
python3 scripts/student_engine.py homework list     # 应该看到 3 项待完成作业
python3 scripts/student_engine.py homework done 1   # 标记第1个完成
python3 scripts/student_engine.py homework list     # 只剩 2 项

# 测试考试
python3 scripts/student_engine.py exam list         # 应该看到 2 场考试
python3 scripts/student_engine.py exam countdown    # 应该看到可视化进度条

# 测试提醒
python3 scripts/student_engine.py remind            # 汇总今日所有事项

# 测试边界情况
rm -rf ~/.student-assistant
python3 scripts/student_engine.py schedule show     # 应该提示"课表为空"
python3 scripts/student_engine.py exam countdown    # 应该提示"暂无考试"
```

### 方法 3：导入你自己的课表

```bash
# 创建你的课表 JSON 文件
cat > my_schedule.json << 'EOF'
[
  {"day": 1, "time": "08:00-09:40", "course": "你的课程名", "teacher": "老师名", "location": "教室", "weeks": "1-16"}
]
EOF

# 导入
python3 scripts/student_engine.py schedule import my_schedule.json

# 确认
python3 scripts/student_engine.py schedule show
```

## 怎么分享给别人

### 方法 1：GitHub 分享（推荐）

```bash
# 在 GitHub 上创建新仓库，然后：
cd student-assistant
git init
git add .
git commit -m "🎓 大学生全能助手 v1.0：课表、作业、考试、提醒"
git branch -M main
git remote add origin https://github.com/你的用户名/student-assistant.git
git push -u origin main
```

然后把仓库链接发给别人，他们只需：
```bash
git clone https://github.com/你的用户名/student-assistant.git
cd student-assistant
bash install.sh
```

### 方法 2：打包成 zip 分享

```bash
# 在项目目录外执行
zip -r student-assistant-v1.0.zip student-assistant/ -x "*.git*"
```

把 zip 发给别人，解压后运行 `bash install.sh`。

### 方法 3：直接复制目录

把整个 `student-assistant/` 文件夹复制到 U 盘/网盘/微信发给同学即可。

## 数据在哪里

所有数据以 JSON 格式存储在 `~/.student-assistant/`：

```bash
ls ~/.student-assistant/
# schedule.json   ← 课表
# homework.json   ← 作业
# exam.json       ← 考试
```

你可以直接编辑这些文件来批量修改数据，也可以写脚本自动化处理。

## 课表文件格式

详见 `references/schedule-guide.md`。简单来说：

**JSON 格式**（推荐）：
```json
[
  {"day": 1, "time": "08:00-09:40", "course": "高等数学", "teacher": "张老师", "location": "教1-301", "weeks": "1-16"}
]
```

**CSV 格式**：
```csv
day,time,course,teacher,location,weeks
1,08:00-09:40,高等数学,张老师,教1-301,1-16
```

字段说明：
- `day`: 1=周一 ~ 7=周日（必填）
- `time`: 上课时间段（必填）
- `course`: 课程名称（必填）
- 其余字段选填

## 许可证

MIT License — 详见 [LICENSE](LICENSE)

## 计划中的功能

- [ ] 桌面通知提醒（到期前自动弹窗）
- [ ] 从教务系统截图 OCR 识别课表
- [ ] Web 可视化界面
- [ ] 多学期管理
- [ ] 导出为 iCal/Google Calendar 格式
