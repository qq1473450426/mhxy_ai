# MHXY AI 多账号主控台

> Django 本地多账号管理与自动化控制框架。
>
> 当前项目定位为：**本地 Web 控制台 + Windows 游戏窗口管理 + Worker/Monitor + Skill/Task 分层**。不包含协议伪造、进程注入或反作弊绕过。

## 0. 当前开发版本

- `main`：稳定基线，只接受验证后的版本。
- `dev`：日常开发分支。
- 当前开发版本：**V2.1.0-dev**。
- UI 基于用户提供的 GM 任务管理后台截图重新实现：深色运营后台、左侧导航、任务筛选、统计卡片、任务表格、趋势图、类型分布、公告区，并针对手机端做响应式折叠。

每次开发修改都必须：

1. 修改前确认当前基线可以运行。
2. 在 `dev` 分支开发，不直接修改 `main`。
3. 提交信息包含 `feat/fix/refactor/docs` 类型和版本号。
4. README 或 `CHANGELOG.md` 记录版本、修改内容和验证结果。
5. 通过 `python manage.py check` 后再进入下一项功能。
6. 稳定后再合并到 `main`。

## 1. 项目简介

项目使用 Django 作为唯一 Web 框架，SQLite 作为默认数据库，Windows 自动化能力放在 `engine/`，游戏知识和坐标放在 `skills/`，具体任务放在 `tasks/`。

核心目标：

- 多账号统一管理
- 电脑端 / 手机端自适应 Web UI
- 游戏客户端启动与窗口检测
- 每账号独立 Worker
- Monitor 心跳与掉线检测
- Skill 驱动的导航、战斗和日常任务框架
- 每账号状态、任务进度和日志
- OpenCV/Pillow/MSS/pywin32 自动化基础能力

## 2. 技术栈

| 模块 | 技术 |
|---|---|
| Web | Django 5.2 LTS |
| 数据库 | SQLite |
| 图像识别 | OpenCV + Pillow |
| 屏幕采集 | MSS |
| Windows | pywin32 |
| 鼠标键盘 | PyAutoGUI |
| 二维码 | qrcode |
| Python | 推荐 3.13/3.14 x64 |

**注意：不要安装 `win32gui` 包。** `win32gui`、`win32con`、`win32process` 等模块来自 `pywin32`。

## 3. 标准项目结构

```text
mhxy_ai/
├── manage.py                 # Django 唯一管理入口
├── config/                   # Django 项目配置
├── dashboard/                # Django 主应用 / Dashboard
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── engine/                   # Windows / Worker / Monitor / 自动化
├── skills/                   # 地图、坐标、模板、知识 Skill
├── tasks/                    # Task 状态机
├── assets/                   # 图片、模板等资源
├── tests/                    # 测试
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

旧 FastAPI `app/api`、Uvicorn `run.py` 等不再作为运行入口。**标准启动入口只有 `manage.py`。**

## 4. 环境要求

Windows 10/11 64 位。

建议 Python 3.13/3.14 x64。安装后先确认：

```powershell
python --version
```

## 5. 全新安装

```powershell
cd D:\project\python
```

如果本地已有旧环境，建议重新克隆：

```powershell
git clone https://github.com/qq1473450426/mhxy_ai.git
cd mhxy_ai
git checkout dev
```

创建虚拟环境：

```powershell
python -m venv .venv
```

PowerShell 激活：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

确认 Python 来自项目：

```powershell
where.exe python
python -c "import sys; print(sys.executable)"
```

必须优先看到：

```text
D:\project\python\mhxy_ai\.venv\Scripts\python.exe
```

安装依赖：

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 6. Django 初始化

检查：

```powershell
python manage.py check
```

数据库初始化：

```powershell
python manage.py migrate
```

查看 Dashboard migration：

```powershell
python manage.py showmigrations dashboard
```

已应用的 migration 应显示 `[X]`。

如果是全新测试环境且数据库可以丢弃，可删除根目录 `data.sqlite3` 后重新执行：

```powershell
python manage.py migrate
```

创建管理员（可选）：

```powershell
python manage.py createsuperuser
```

## 7. 启动项目

本机访问：

```powershell
python manage.py runserver 127.0.0.1:8000
```

手机/局域网访问：

```powershell
python manage.py runserver 0.0.0.0:8000
```

电脑：

```text
http://127.0.0.1:8000/
```

手机与电脑处于同一局域网：

```text
http://电脑局域网IP:8000/
```

如果手机无法访问，检查 Windows 防火墙是否允许 TCP 8000，以及手机和电脑是否在同一网段。

## 8. GM Dashboard UI

### 8.1 UI 设计目标

V2.1.0-dev 的 Dashboard 参考用户提供的 GM 任务管理后台截图，采用：

- 深色蓝黑运营后台风格
- 左侧固定导航
- 顶部用户/消息区
- 任务筛选条
- 五项统计卡片
- 多账号任务表格
- 进度条和状态标签
- 趋势图
- 环形任务类型分布
- 系统公告
- 手机端侧边栏折叠
- 800px / 520px 断点响应式布局

主要 UI 文件：

```text
dashboard/templates/dashboard.html
dashboard/static/gm_dashboard.css
```

旧 `dashboard.css` 保留为兼容资源，但新 Dashboard 使用 `gm_dashboard.css`。

### 8.2 实时状态

Dashboard 每 2 秒读取：

```text
/api/status/
```

显示：

- 账号数量
- Worker 状态
- 当前任务
- 任务进度
- PID
- 重连次数
- 当前消息

## 9. 添加账号

Dashboard → 创建任务 / 添加账号。

账号模型目前支持：

- 显示名称
- 游戏账号
- 登录模式
- 密码
- 游戏客户端 EXE
- 启动参数
- 窗口标题
- 自动登录
- 自动重连
- 自动日常任务

### 密码安全

默认 SQLite 方案只适合本地测试。真实账号密码不要长期明文保存。

正式版本建议使用 Windows Credential Manager / DPAPI，在 Worker 启动期间短时读取。

## 10. Worker 工作流程

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
```

掉线：

```text
DISCONNECTED
   ↓
RECONNECTING
   ↓
LOGIN
```

Worker 负责：

- 客户端启动
- 窗口绑定
- PID/HWND
- 状态机
- 心跳
- 任务调度
- 进度
- 日志

## 11. Monitor

Monitor 只负责观察，不直接决定任务策略：

- Window/HWND
- PID
- Worker 心跳
- 当前状态
- 当前任务
- 当前进度
- 重连次数
- 错误状态

一个账号异常不应阻塞其他账号。

## 12. Skill 系统

`skills/` 是知识与执行配置层。

推荐：

```text
skills/
├── maps/
├── navigation/
│   ├── routes/
│   └── coordinates/
├── battle/
│   ├── templates/
│   └── actions/
├── daily/
└── common/
```

Skill 应尽量包含：

```text
目标
前置条件
识别条件
动作
成功条件
失败条件
超时
重试策略
坐标/模板
```

## 13. 自动寻路

采用状态机，而不是固定点击脚本：

```text
读取当前地图
    ↓
读取当前位置
    ↓
查询路线 Skill
    ↓
执行下一节点
    ↓
验证位置变化
    ↓
失败 → 重定位 / 重试
    ↓
成功 → 下一节点
```

地图和坐标变化时优先修改 Skill 数据，不修改 Worker 核心逻辑。

## 14. 战斗与日常任务

战斗建议拆成：

```text
战斗检测
 ↓
状态识别
 ↓
动作选择
 ↓
执行
 ↓
结果验证
```

日常任务放在 `tasks/`，Worker 只负责调度：

```text
Task
 ↓
Skill
 ↓
Window
 ↓
Automation
 ↓
Verification
```

开发阶段建议先启用 Dry Run，确认识别、坐标和状态机正确后再执行实际输入。

## 15. 日志

每账号独立记录：

- 启动/停止
- 登录
- 窗口检测
- 掉线/重连
- 寻路
- 战斗
- 任务
- Skill
- 错误

后续可继续增加实时日志流、搜索、导出和错误截图。

## 16. 多账号架构

```text
Account 1
 ├── Window
 ├── Worker
 ├── Monitor
 ├── Task
 └── Log

Account 2
 ├── Window
 ├── Worker
 ├── Monitor
 ├── Task
 └── Log
```

## 17. Git 分支与版本规范

### 分支

```text
main  = 稳定版本
  ↑
 dev  = 开发版本
```

开发只进入 `dev`：

```powershell
git checkout dev
git pull origin dev
```

验证完成后再合并：

```text
dev → Pull Request → main
```

### 版本号

采用：

```text
V主版本.功能版本.修复版本[-dev]
```

例如：

```text
V2.1.0-dev
V2.1.1-dev
V2.2.0-dev
V2.2.0
```

### Commit

建议：

```text
feat(ui): add GM dashboard v2.1.0-dev
fix(engine): repair window detection v2.1.1-dev
refactor(worker): split monitor state v2.2.0-dev
docs: update setup guide v2.2.0-dev
```

## 18. 更新项目

更新开发分支：

```powershell
git fetch origin
git checkout dev
git pull origin dev
```

依赖更新后：

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
```

启动：

```powershell
python manage.py runserver 0.0.0.0:8000
```

## 19. 常见问题

### `no such table: dashboard_account`

数据库 migration 未执行或使用了不同的 SQLite 文件：

```powershell
python manage.py migrate
python manage.py showmigrations dashboard
```

### `No module named 'win32gui'`

不要安装 `win32gui` 包。使用：

```powershell
python -m pip install pywin32
python -m pywin32_postinstall -install
python -c "import win32gui; print('win32gui OK')"
```

### 使用了系统 Python

确认：

```powershell
where.exe python
python -c "import sys; print(sys.executable)"
```

如果不是 `.venv\\Scripts\\python.exe`，重新：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 手机打不开

必须使用：

```powershell
python manage.py runserver 0.0.0.0:8000
```

而不是 `127.0.0.1:8000`。

同时检查 Windows 防火墙 TCP 8000。

### `pydantic-core` / FastAPI / Jinja2 报错

这些属于旧架构残留。当前标准项目使用 Django，不需要 FastAPI/Uvicorn/Jinja2/Pydantic。

## 20. 当前版本边界

当前版本完成 Django 基础架构、账号/Worker/Monitor/Skill/Task 分层和 GM Dashboard UI。游戏客户端具体地图、UI 模板、任务流程和坐标仍需要根据实际客户端版本、窗口尺寸和 Skill 数据进行适配。

项目不提供协议伪造、进程注入或反作弊绕过功能。

## 21. License

本项目用于本地软件自动化研究、工程测试和学习。使用者需要自行遵守相关软件服务条款和适用法律。
