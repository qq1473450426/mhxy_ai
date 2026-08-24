# 梦幻西游 AI 多账号主控板

一个基于 **Windows 窗口 + 截图 + OpenCV 模板识别 + 本地 Agent 推理 + Worker 状态机 + Monitor 看门狗 + Scheduler 调度** 的多账号桌面自动化框架。

> 当前版本不调用任何外部 AI API，不需要 API Key。
>
> 不包含封包伪造、协议篡改、进程注入或反作弊绕过。

## 1. 功能

- 多账号 Worker：一个账号一个独立 Worker
- Windows 窗口枚举与 HWND 绑定
- 游戏窗口截图
- OpenCV 模板匹配
- 鼠标点击 / 键盘输入
- JSON 任务系统
- 本地 AI 思维：候选动作、评分、失败降权、重复动作抑制、记忆
- Monitor 看门狗：心跳、窗口、画面停滞检查
- 掉线检测 / 重连状态机
- 重连失败后自动寻找备用账号
- SQLite 事件日志
- 每账号独立日志
- 异常截图
- `xyq-skills` 知识库接口
- Web 主控板
- `dry_run` 安全测试模式

## 2. 环境

推荐 Windows 10/11 + Python 3.11。

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. 启动

```bat
python run.py
```

然后访问：

```text
http://127.0.0.1:8000
```

也可以双击：

```text
start.bat
```

第一次必须保持：

```json
"dry_run": true
```

确认窗口、截图、日志、任务流程正常后，再自行改为 `false`。

## 4. 配置账号

编辑：

```text
config/accounts.json
```

示例：

```json
[
  {
    "account_id": "A01",
    "name": "主号",
    "hwnd": null,
    "window_title": "梦幻西游",
    "priority": 100,
    "enabled": true
  }
]
```

如果设置 `hwnd`，Worker 优先使用 HWND；为空时按窗口标题查找。

查看当前窗口：

```text
GET http://127.0.0.1:8000/api/windows
```

## 5. 模板识别

把固定分辨率下从游戏窗口截取的按钮放进：

```text
assets/templates/
```

例如：

```text
battle_attack.png
battle_end.png
dialog.png
reconnect.png
```

模板尽量只保留按钮/图标本身，不要带大面积背景。

阈值配置：

```text
config/config.json
```

```json
"template_threshold": 0.88
```

## 6. 任务

任务文件放在：

```text
tasks/
```

示例：

```json
{
  "task_name": "测试任务",
  "loop": false,
  "steps": [
    {"type": "wait", "seconds": 2},
    {"type": "find_click", "template": "battle_attack.png", "confidence": 0.88, "timeout": 5},
    {"type": "wait", "seconds": 3}
  ]
}
```

支持：

- `wait`
- `key`
- `click`
- `find_click`
- `screenshot`

主控板的任务按钮传入任务文件名，例如 `test_task`。

## 7. 本地 AI 思维

核心文件：

```text
app/services/ai.py
```

决策闭环：

```text
截图 / 窗口状态
      ↓
结构化观测
      ↓
当前状态 + 当前任务
      ↓
生成候选动作
      ↓
条件评分
      ↓
历史失败动作降权
      ↓
连续重复动作抑制
      ↓
选择最高分动作
      ↓
执行
      ↓
记录结果
      ↓
下一轮重新判断
```

这是本地、可审计的 Agent 决策机制，不依赖云端模型。

## 8. 掉线与自动换号

Monitor 会检查：

- Worker heartbeat
- 游戏窗口是否存在
- 画面是否长期无变化
- Worker 是否进入 `DISCONNECTED/ERROR`

正常流程：

```text
RUNNING
  ↓
DISCONNECTED
  ↓
RECONNECTING
  ↓
LOGIN
  ↓
IDLE
```

超过 `max_reconnect_attempts` 后进入 `MANUAL_REQUIRED`，Scheduler 会寻找可用备用账号并尝试接管任务。

## 9. 日志

```text
logs/controller.log
logs/account_A01.log
logs/account_A02.log
```

数据库：

```text
data/mhxy.db
```

异常截图：

```text
screenshots/<account_id>/
```

主控板可以实时筛选日志，重点事件包括：

```text
STATE_CHANGE
LOCAL_AI_DECISION
TASK_STEP
TEMPLATE_MATCH
RECONNECT_ATTEMPT
RECONNECT_SUCCESS
RECONNECT_FAILED
AUTO_SWITCH
ERROR
```

## 10. xyq-skills

把你提供的知识库放到：

```text
knowledge/xyq-skills/
```

例如：

```bat
git clone https://github.com/MikiVision/xyq-skills.git knowledge/xyq-skills
```

接口：

```text
GET /api/knowledge/search?q=抓鬼
```

## 11. 推荐测试顺序

1. 安装依赖。
2. 保持 `dry_run=true`。
3. 启动梦幻西游窗口。
4. 运行 `python run.py`。
5. 打开 Web 主控板。
6. 访问 `/api/windows` 确认窗口。
7. 配置 `config/accounts.json`。
8. 准备至少一个真实模板。
9. 创建简单 JSON 测试任务。
10. 运行 1 个账号。
11. 测试日志与截图。
12. 测试模拟掉线与恢复。
13. 再增加第 2 个账号。
14. 确认稳定后再关闭 `dry_run`。

## 12. 常见问题

### 找不到窗口

先访问：

```text
/api/windows
```

查看实际 title 和 HWND。

### 模板识别失败

检查游戏分辨率、窗口缩放、DPI、模板截图是否来自同一套 UI 尺寸。

### 点击位置不对

`find_click` 会把模板在窗口中的位置转换为屏幕坐标；尽量不要用固定屏幕坐标任务。

### 游戏窗口被移动

每次动作前都会重新获取窗口位置，因此移动窗口后不需要重新计算模板坐标。

## 13. 项目结构

```text
mhxy_ai/
├── app/
│   ├── api/
│   ├── core/
│   ├── services/
│   └── workers/
├── assets/templates/
├── config/
├── tasks/
├── knowledge/
├── screenshots/
├── logs/
├── data/
├── tests/
├── requirements.txt
├── run.py
└── start.bat
```
