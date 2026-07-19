# 大学生全能助手 v1.1 🎓

> 课表 · 作业 · 考试 · 期末复习 · 成长记录 · 目标管理 · 数据仪表盘 · Excel报表 · PPT生成

## 功能一览

| 模块 | 功能 |
|------|------|
| 📅 **课表管理** | JSON/CSV导入、OCR截图识别、Web可视化 |
| 📝 **作业管理** | 添加、查看、标记完成、紧急提醒 |
| ⏰ **考试倒计时** | 可视化进度条、临近自动提醒 |
| 📖 **期末复习** | 知识点清单、刷题追踪、错题本、复习计划自动生成 |
| 🌱 **成长记录** | 每日打卡（学习/阅读/运动/早起）、心情日记、连续打卡统计 |
| 🎯 **目标管理** | 长期/短期/每日目标、进度追踪、里程碑 |
| 📊 **数据仪表盘** | Web端可视化图表：复习进度、学习趋势、目标完成率 |
| 📥 **Excel 导出** | 一键导出7个Sheet：课表/作业/考试/复习/成长/目标/刷题 |
| 🎨 **PPT 生成** | AI对话触发，3种模板：学术汇报/社团展示/课堂报告 |
| 🔔 **桌面通知** | 后台常驻，作业/考试自动弹窗 |
| 🔍 **OCR 识别** | 拍课表截图自动识别导入 |
| 📚 **多学期** | 创建切换学期，数据隔离 |
| 📤 **iCal 导出** | 导出 .ics 导入系统日历 |

## 快速开始

```bash
git clone https://github.com/你的用户名/student-assistant.git
cd student-assistant
bash install.sh
python3 server.py
```

浏览器打开 http://localhost:5000，六个 Tab 随便用。

## 怎么用

### Web 界面（最推荐）
```bash
python3 server.py
# 浏览器打开 localhost:5000
```

### 命令行
```bash
python3 scripts/engine.py remind              # 今日提醒
python3 scripts/engine.py review knowledge list  # 复习进度
python3 scripts/engine.py daily stats         # 成长统计
python3 scripts/engine.py goal list           # 目标列表
python3 scripts/export_excel.py               # 导出Excel
python3 scripts/generate_ppt.py "主题"        # 生成PPT
```

### AI 对话
对 AI 说"今天有什么课"、"复习进度"、"今日打卡"、"帮我做PPT"等。

## 项目结构

```
student-assistant/
├── SKILL.md / README.md / install.sh / server.py / index.html
├── scripts/
│   ├── engine.py          # 核心引擎（课表/作业/考试/复习/成长/目标）
│   ├── export_excel.py    # Excel 报表导出
│   ├── generate_ppt.py    # PPT 生成（3种模板）
│   ├── notifier.py        # 桌面通知
│   ├── ocr_schedule.py    # OCR 识别
│   └── test.py            # 自动化测试
└── references/
```

## 许可证
MIT License
