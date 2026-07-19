# 课表导入指南

## 支持的文件格式

### JSON 格式（推荐）

```json
[
  {
    "day": 1,
    "time": "08:00-09:40",
    "course": "高等数学",
    "teacher": "张老师",
    "location": "教1-301",
    "weeks": "1-16"
  },
  {
    "day": 2,
    "time": "10:00-11:40",
    "course": "大学英语",
    "teacher": "李老师",
    "location": "教2-205",
    "weeks": "1-16"
  }
]
```

字段说明：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| day | 数字 | ✅ | 1=周一, 2=周二... 7=周日 |
| time | 字符串 | ✅ | 上课时间段，如 "08:00-09:40" |
| course | 字符串 | ✅ | 课程名称 |
| teacher | 字符串 | ❌ | 授课教师 |
| location | 字符串 | ❌ | 上课地点 |
| weeks | 字符串 | ❌ | 上课周次，如 "1-16" |

### CSV 格式

```csv
day,time,course,teacher,location,weeks
1,08:00-09:40,高等数学,张老师,教1-301,1-16
1,10:00-11:40,大学英语,李老师,教2-205,1-16
2,08:00-09:40,线性代数,王老师,教1-201,1-16
```

**注意：CSV 文件必须有表头行（day,time,course...）**

## 导入方式

### 方式一：从教务系统导出后导入

很多学校的教务系统支持导出课表为 Excel/CSV。导出后用 Excel 调整列名为上述格式，保存为 CSV 即可导入。

### 方式二：手动创建 JSON 文件

直接用文本编辑器创建 `.json` 文件，按格式填写。

### 方式三：让 AI 助手帮你生成

对 AI 说"帮我生成这学期的课表"，AI 会帮你创建 JSON 文件。

## 导入命令

```bash
# JSON 格式
python3 student_engine.py schedule import my_schedule.json

# CSV 格式
python3 student_engine.py schedule import my_schedule.csv
```
