# MHXY AI 多账号主控台 V2

> Django + Local Worker + Monitor + Skill + Vision Automation

这是一个面向 Windows 的本地多账号游戏自动化控制台。V2 将原来的 FastAPI 主控台正式整理为 Django 项目，并把 **账号、Worker、Monitor、Skill、任务状态机、日志、Web Dashboard** 分层。

## 1. 项目定位

核心目标不是把所有逻辑塞进一个脚本，而是建立：

```text
Web UI
  ↓
账号管理 / 任务管理
  ↓
Worker Manager
  ↓
Monitor + State Machine
  ↓
Skill / Vision
  ↓
Automation Engine
  ↓
游戏窗口
```

每个账号拥有独立 Worker，Dashboard 显示账号状态、任务、进度、PID、重连次数和日志。

---

# 2. V2 功能

## 2.1 Django Web UI

- Django 5
- SQLite
- PC / 手机自适应
- 多账号卡片式 Dashboard
- 实时轮询状态
- 账号独立日志
- 启动 / 停止 Worker
- 启动日常任务

## 2.2 账号管理

添加账号时可配置：

- 显示名称
- 游戏账号
- 账号密码模式
- 扫码模式
- 游戏客户端 EXE
- 启动参数
- 窗口标题
- 自动登录开关
- 自动重连开关
- 自动日常开关

> 当前密码字段仍属于开发版存储。正式部署建议替换为 Windows Credential Manager / DPAPI。

## 2.3 Worker

每个账号对应一个 Worker：

```text
STOPPED
   ↓
STARTING
   ↓
LOGIN
   ↓
IDLE
   ↓
NAVIGATING
   ↓
BATTLE
   ↓
TASK
   ↓
IDLE
```

异常时：

```text
IDLE / TASK
    ↓
DISCONNECTED
    ↓
RECONNECTING
    ↓
LOGIN / IDLE
```

## 2.4 Monitor

Monitor 定期检查：

- 游戏窗口是否存在
- PID
- Worker 心跳
- 掉线
- 重连次数
- 当前状态

## 2.5 Skill

Skill 层用于保存：

- 地图
- 坐标
- NPC
- 路线
- 任务步骤
- 战斗规则
- UI 模板

目录：

```text
skills/
├── maps/
├── navigation/
├── battle/
├── daily/
└── templates/
```

当前 `SkillStore` 支持关键词检索以及简单 `x/y` 坐标提取。

你已有的：

```text
https://github.com/MikiVision/xyq-skills
```

可以整理到 `skills/` 中作为知识/坐标来源。

## 2.6 Vision / Automation

当前基础层提供：

- 截图
- OpenCV 模板匹配
- UI 位置检测
- 鼠标点击
- 键盘输入
- 等待

默认 `dry_run=True`，用于先验证状态机和识别流程，避免程序刚启动就执行真实输入。

---

# 3. 项目目录

```text
mhxy_ai/
│
├── config/                    # Django 配置
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── dashboard/                # Web UI / 数据模型
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/
│   ├── templates/
│   └── static/
│
├── engine/                   # 自动化核心
│   ├── manager.py             # Worker Manager
│   ├── monitor.py             # 账号监控
│   ├── state_machine.py       # 状态机
│   ├── task_runner.py         # 任务执行器
│   ├── skills.py              # Skill 数据访问
│   ├── automation.py          # OpenCV / 鼠标 / 键盘
│   └── window_manager.py      # Windows 游戏窗口
│
├── skills/                   # Skill 数据
├── tasks/                    # 任务定义
├── accounts/                 # 本地账号数据目录预留
├── logs/                     # 日志目录预留
├── screenshots/              # 截图目录预留
├── manage.py
├── run.py
├── start.bat
└── requirements.txt
```

---

# 4. 环境要求

推荐：

```text
Windows 10 / 11
Python 3.14 x64
```

当前依赖已经针对你之前遇到的 Python 3.14 / Pydantic / NumPy / OpenCV 问题进行了整理。

主要版本：

```text
Django              5.2.5
OpenCV              4.12.0.88
NumPy               2.2.6
Pillow              11.3.0
PyAutoGUI           0.9.54
pywin32             311
```

---

# 5. 第一次安装

进入项目目录：

```bat
cd D:\project\python\mhxy_ai
```

创建虚拟环境：

```bat
python -m venv .venv
```

激活：

```bat
.venv\Scripts\activate
```

升级 pip：

```bat
python -m pip install --upgrade pip
```

安装依赖：

```bat
pip install -r requirements.txt
```

初始化数据库：

```bat
python manage.py migrate
```

启动：

```bat
python manage.py runserver 0.0.0.0:8000
```

或者：

```bat
start.bat
```

---

# 6. 打开 Web UI

电脑本机：

```text
http://127.0.0.1:8000
```

局域网手机：

```text
http://电脑局域网IP:8000
```

例如电脑 IP 是：

```text
192.168.1.100
```

手机访问：

```text
http://192.168.1.100:8000
```

如果 Windows 防火墙拦截，需要允许 Python/Django 使用对应端口。

---

# 7. 添加账号

点击：

```text
＋ 添加账号
```

填写：

```text
显示名称
游戏账号
登录方式
密码
游戏客户端 EXE
启动参数
窗口标题
```

例如：

```text
显示名称：大唐1号
账号：example
客户端：D:\Games\MHXY\game.exe
窗口标题：梦幻西游
```

如果客户端已经打开，Worker 会先尝试通过窗口标题查找现有窗口，而不是立即重复启动。

---

# 8. 启动账号 Worker

Dashboard 点击：

```text
启动
```

流程：

```text
检查窗口
   │
   ├── 找到 → LOGIN / IDLE
   │
   └── 没找到
          ↓
       启动 EXE
          ↓
       等待窗口
          ↓
       LOGIN
          ↓
       IDLE
```

如果 EXE 路径不存在，会在账号日志中显示错误，而不是让整个 Django 服务崩溃。

---

# 9. Monitor

打开 Dashboard 后 Monitor 自动启动。

默认每约 2 秒检查一次账号窗口。

状态包括：

```text
STOPPED
STARTING
LOGIN
IDLE
NAVIGATING
BATTLE
TASK
DISCONNECTED
RECONNECTING
ERROR
```

Dashboard 每 2 秒刷新状态。

---

# 10. Skill 使用方法

将 Skill 放入：

```text
skills/
```

推荐：

```text
skills/
├── maps/
│   ├── changan.yaml
│   └── jianye.yaml
├── navigation/
│   └── daily_route.yaml
├── battle/
│   └── normal_battle.yaml
└── daily/
    └── demo_daily.yaml
```

简单示例：

```yaml
name: demo_daily
world: 示例场景
route:
  - {x: 100, y: 200, action: move}
  - {x: 120, y: 220, action: interact}
```

当前任务执行器会首先查找 Skill，再进入状态机；没有匹配 Skill 时不会继续执行危险输入。

---

# 11. 自动寻路架构

正式接入地图 Skill 后：

```text
当前位置
    ↓
目标位置
    ↓
Skill 路线
    ↓
路径节点
    ↓
视觉/坐标确认
    ↓
移动
    ↓
节点到达确认
    ↓
下一个节点
```

建议不要只依赖固定屏幕坐标，应同时保存：

```text
地图坐标
屏幕坐标
窗口偏移
分辨率
UI 状态
到达判断
```

这样换窗口位置或分辨率时更容易适配。

---

# 12. 自动战斗架构

战斗 Worker 应采用状态机：

```text
非战斗
 ↓
战斗检测
 ↓
进入战斗
 ↓
识别战斗 UI
 ↓
选择动作
 ↓
执行
 ↓
等待回合结果
 ↓
再次识别
 ↓
战斗结束
 ↓
返回任务
```

建议所有动作都有：

```text
识别 → 执行 → 验证
```

而不是无条件连续点击。

---

# 13. 自动日常任务

任务建议定义成步骤：

```text
领取任务
 ↓
检查目标
 ↓
寻路
 ↓
NPC 交互
 ↓
战斗
 ↓
奖励检测
 ↓
下一环
 ↓
完成
```

Dashboard 可以通过「日常任务」按钮触发任务 Runner。

当前 V2 的任务 Runner 已完成状态流转和 Skill 检查；真正的游戏 UI 操作需要根据实际客户端画面继续配置模板/Skill。

---

# 14. 日志

每个账号都有独立日志。

例如：

```text
INFO START
INFO READY
WARN WINDOW_MISSING
WARN DISCONNECTED
INFO WINDOW_RESTORED
INFO TASK_START
WARN SKILL_MISSING
INFO TASK_DONE
ERROR WORKER_ERROR
```

Dashboard 点击：

```text
日志
```

可以查看该账号最近事件。

---

# 15. API

状态：

```text
GET /api/status/
```

窗口：

```text
GET /api/windows/
```

这些接口供 Web UI 或后续手机端/独立控制端使用。

---

# 16. 扫码登录

项目保留扫码登录的数据模型和 UI 模式。

真实扫码流程必须读取实际客户端产生的登录二维码，不应自行伪造第三方登录协议。

后续接入方式建议：

```text
客户端产生二维码
      ↓
本地 Agent 获取图片
      ↓
Django 保存临时二维码
      ↓
Dashboard 显示
      ↓
手机打开 Dashboard
      ↓
长按/下载图片
      ↓
保存到手机相册
```

---

# 17. 多账号设计

每个账号独立：

```text
Account
   │
   └── Worker
         ├── Monitor
         ├── State Machine
         ├── Task
         ├── Skill
         └── Log
```

例如：

```text
账号1 → Worker1
账号2 → Worker2
账号3 → Worker3
账号4 → Worker4
```

互不共享运行状态。

---

# 18. 自动换号

V2 已预留自动换号架构，但真正的换号动作应由账号调度器完成：

```text
账号1任务完成
      ↓
退出/回到登录界面
      ↓
Worker 状态确认
      ↓
释放窗口
      ↓
选择账号2
      ↓
登录
      ↓
进入账号2 Worker
```

不要简单地直接杀进程再启动，否则容易造成状态丢失。

---

# 19. 安全与稳定性

默认建议：

```text
DRY RUN
 ↓
截图验证
 ↓
模板匹配验证
 ↓
单账号测试
 ↓
小任务测试
 ↓
多账号测试
```

正式运行前不要直接开启大量账号。

账号密码不要提交到 GitHub。

建议加入 `.gitignore`：

```text
.venv/
*.sqlite3
accounts/
logs/
screenshots/
qr/
.env
```

---

# 20. 常见问题

## 20.1 pydantic-core 编译失败

V2 已经不再依赖之前 FastAPI 版本的 Pydantic 配置。如果仍然出现旧环境缓存问题：

```bat
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 20.2 OpenCV / NumPy 冲突

当前固定：

```text
opencv-python==4.12.0.88
numpy==2.2.6
```

不要手动升级 NumPy 到与 OpenCV 不兼容的版本。

## 20.3 找不到游戏窗口

检查：

1. 游戏是否已经启动
2. 窗口标题是否正确
3. EXE 路径是否正确
4. Python 是否有权限访问窗口
5. `GET /api/windows/` 是否能看到窗口

## 20.4 手机无法打开

确认：

```text
手机和电脑处于同一个局域网
```

并用：

```text
http://电脑IP:8000
```

而不是 `127.0.0.1`。

---

# 21. 开发路线

### V2 已完成基础

- [x] Django
- [x] Dashboard
- [x] 响应式 UI
- [x] 账号管理
- [x] Worker
- [x] Monitor
- [x] 状态机
- [x] SkillStore
- [x] OpenCV 自动化层
- [x] 日志
- [x] 日常任务 Runner 基础

### V2 后续

- [ ] WebSocket 实时推送
- [ ] 真正的任务调度器
- [ ] 自动重连完整流程
- [ ] 自动换号调度器
- [ ] Skill YAML/JSON 标准化
- [ ] 地图路径规划
- [ ] 战斗 UI 模板库
- [ ] 日常任务编排器
- [ ] 客户端二维码采集
- [ ] Windows Credential Manager / DPAPI
- [ ] 多窗口布局管理
- [ ] Worker 崩溃自动恢复
- [ ] 运行截图与录像

---

# 22. 运行原则

这个项目的游戏交互层以正常窗口、截图、视觉识别、坐标和正常用户输入为基础。

不会在项目中加入：

- 进程注入
- 封包伪造
- 网络协议篡改
- 客户端破解
- 反作弊绕过
- 伪造官方登录协议

这样可以把账号管理、任务编排、视觉自动化和 Skill 知识层保持解耦，也方便后续测试和维护。
