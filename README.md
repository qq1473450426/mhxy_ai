# MHXY AI GM 任务管理系统

> React + TypeScript 前端与 Django API 后端分离的本地运营控制台。
>
> 当前项目定位为**本地 Web 控制台 + Windows 游戏窗口管理 + Skill/任务执行框架**。不包含协议伪造、进程注入或反作弊绕过。

## 1. 项目简介

项目使用 React + TypeScript 作为前端、Django 仅提供 JSON API，SQLite 作为默认数据库。Windows 客户端自动化能力位于 `engine/`；`xyq-skills/` 提供梦幻西游玩法知识，并可在创建任务时直接检索。

核心目标：

- 多账号统一管理
- 电脑端 / 手机端自适应 Web UI
- 游戏客户端启动与窗口检测
- 每账号独立 Worker
- Monitor 心跳与掉线检测
- Skill 驱动的导航、战斗和日常任务框架
- 每账号实时状态、任务进度和日志
- 后续可以继续接入 OCR、OpenCV 模板识别和更完整的任务状态机

## 2. 技术栈

| 模块 | 技术 |
|---|---|
| Frontend | React + TypeScript + Vite |
| Backend API | Django 5.2 LTS |
| 数据库 | SQLite |
| 图像识别 | OpenCV + Pillow |
| 屏幕采集 | MSS |
| Windows | pywin32 |
| 鼠标键盘 | PyAutoGUI |
| 二维码 | qrcode |
| Python | 推荐 3.13/3.14 x64 |

## 3. 标准项目结构

```text
mhxy_ai/
├── manage.py                 # Django 唯一管理入口
├── config/                   # Django 项目配置
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── dashboard/                # Django 主应用
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── engine/                   # Windows 自动化与运行时
│   ├── automation.py
│   ├── manager.py
│   ├── skills.py
│   └── window_manager.py
├── skills/                   # 地图、坐标、UI 模板、知识 Skill
├── tasks/                    # 任务状态机
├── templates/                # 可扩展的全局模板资源
├── static/                   # 可扩展的全局静态资源
├── assets/                   # 项目资源
├── tests/                    # 测试
├── requirements.txt
└── README.md
```

### 已移除的旧结构

旧 FastAPI 路径 `app/api`、旧 Uvicorn 启动方式 `run.py`、重复的 `start.bat` 等不再作为 Django 运行入口。

**唯一标准启动入口是 `manage.py`。**

## 4. 环境要求

Windows 10/11 64 位。

建议使用 Python 3.13 或 3.14 64 位。

检查：

```bat
python --version
```

## 5. 全新安装

在项目目录执行：

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

## 6. Django 初始化

执行系统检查：

```bat
python manage.py check
```

正确结果：

```text
System check identified no issues (0 silenced).
```

初始化数据库：

```bat
python manage.py migrate
```

创建管理员（可选）：

```bat
python manage.py createsuperuser
```

## 7. 启动项目

分别启动后端 API：

```bat
python manage.py runserver 127.0.0.1:8000
```

允许局域网手机访问：

```bat
python manage.py runserver 0.0.0.0:8000
```

再启动 TypeScript 前端：

```bat
cd frontend
npm install
npm run dev
```

电脑打开：

```text
http://127.0.0.1:5173/
```

手机与电脑处于同一局域网时：

```text
http://电脑局域网IP:8000/
```

例如：

```text
http://192.168.1.100:8000/
```

## 8. 管理后台

如果创建了超级管理员，可以进入：

```text
http://127.0.0.1:8000/admin/
```

Django Admin 用于数据库级管理；日常操作建议使用项目自己的 Dashboard。

## 9. 添加账号

Dashboard → 添加账号。

填写：

- 显示名称
- 游戏账号
- 登录模式
- 密码（如果使用账号密码模式）
- 游戏客户端 EXE
- 启动参数
- 窗口标题
- 自动登录
- 自动重连
- 自动日常任务

### 密码安全

默认数据库方案用于本地测试。正式使用不要把真实密码长期明文保存到 SQLite。

推荐后续改成 Windows Credential Manager 或 DPAPI，并只在 Worker 运行期间解密。

## 10. Worker 工作流程

每一个账号对应一个 Worker：

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

客户端窗口消失：

```text
DISCONNECTED
   ↓
RECONNECTING
   ↓
LOGIN
```

Worker 负责：

- 启动客户端
- 查找窗口
- 保存 PID/HWND
- 心跳
- 状态更新
- 任务进度
- 掉线检测
- 日志

## 11. Monitor

Monitor 不直接决定游戏策略，而是负责观察 Worker：

- Window/HWND 是否存在
- PID 是否存在
- Worker 心跳是否正常
- 当前状态
- 当前任务
- 当前进度
- 重连次数
- 最近错误

Dashboard 会定期刷新状态。

## 12. Skill 系统

`skills/` 是项目的知识和执行配置层。

建议按照以下方式组织：

```text
skills/
├── maps/
│   ├── 大唐官府/
│   ├── 长安城/
│   └── 其他地图/
├── navigation/
│   ├── routes/
│   └── coordinates/
├── battle/
│   ├── templates/
│   └── actions/
├── daily/
│   ├── task_routes/
│   └── task_conditions/
└── common/
```

一个 Skill 应尽量包含：

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

例如：

```yaml
name: 长安城到大唐官府
start: 长安城
end: 大唐官府
steps:
  - type: coordinate
    x: 100
    y: 200
  - type: template
    file: templates/入口.png
  - type: verify
    template: templates/大唐官府.png
```

## 13. 自动寻路

寻路不要设计成单纯的：

```text
点击 A → 点击 B → 点击 C
```

推荐状态机：

```text
读取当前地图
    ↓
读取当前位置
    ↓
查询 Skill 路线
    ↓
执行下一节点
    ↓
验证位置是否改变
    ↓
失败 → 重试/重新定位
    ↓
成功 → 下一节点
```

这样地图坐标变化时只需要更新 Skill，而不用修改 Worker。

## 14. 战斗引擎

战斗模块建议采用：

```text
战斗检测
   ↓
读取战斗状态
   ↓
识别可用技能/目标
   ↓
选择动作
   ↓
执行
   ↓
验证回合结束
   ↓
继续 / 战斗结束
```

OpenCV 模板识别基础已经位于 `engine/automation.py`。

## 15. 日常任务

日常任务应该作为独立 Task，而不是全部写进 Worker：

```text
tasks/
├── base.py
├── daily.py
├── navigation.py
└── battle.py
```

Worker 只负责运行 Task。

Task 再调用：

```text
Skill
 ↓
Window
 ↓
Automation
 ↓
Verification
```

## 16. 日志

每个账号独立记录：

- 启动
- 停止
- 登录
- 窗口检测
- 掉线
- 重连
- 寻路
- 战斗
- 任务
- Skill
- 错误

Dashboard 可以查看单账号日志。

后续可以增加：

- 日志等级过滤
- 实时日志流
- 日志搜索
- 日志导出
- Worker 错误截图

## 17. 多账号运行原则

每个账号应该保持独立运行上下文：

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

一个账号异常不应该阻塞其他账号。

## 18. 调试模式

自动化执行层建议开发阶段使用 Dry Run：

```text
识别 → 输出动作 → 不实际点击
```

确认识别准确后再开启实际动作。

这样可以先验证 Skill、坐标、模板和状态机。

## 19. 常见问题

### `No module named 'bin'`

当前标准 Django 项目不使用 `bin.settings` 或 `bin.*`。

检查：

```bat
echo %DJANGO_SETTINGS_MODULE%
```

正常应为空或：

```text
config.settings
```

并执行：

```bat
python manage.py check
```

### `jinja2 must be installed`

这是旧 FastAPI/Starlette 版本留下的问题。

当前项目已经完全使用 Django Template，不需要 `Jinja2Templates`。

### `pydantic-core` 编译失败

当前 Django 版本不依赖 Pydantic，不应该再出现这个安装问题。

如果仍然出现，说明本地虚拟环境残留。删除 `.venv` 后重新安装：

```bat
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### OpenCV / NumPy 冲突

当前固定：

```text
opencv-python 4.12.0.88
numpy 2.2.6
```

不要再单独安装 `numpy==2.3.x`。

## 20. 更新项目

以后 GitHub 更新后，在本地执行：

```bat
git fetch origin
git reset --hard origin/main
git clean -fd
```

如果依赖发生变化：

```bat
pip install -r requirements.txt
python manage.py migrate
```

然后：

```bat
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

## 21. 开发原则

### Web 层

只处理：

- 页面
- API
- 账号
- 状态展示

### Worker 层

只处理：

- 生命周期
- 状态机
- Task 调度

### Engine 层

只处理：

- Windows
- Screenshot
- OCR/模板
- Mouse/Keyboard

### Skill 层

只处理：

- 地图
- 坐标
- 识别规则
- 路线
- 任务知识

### Task 层

只处理：

- 具体任务流程
- 成功/失败
- 重试
- 超时

这样可以避免把所有逻辑塞进一个巨大脚本。

## 22. 当前版本边界

当前版本已经完成 Django 基础架构、账号/Worker/Monitor/Skill/任务的分层基础，但游戏客户端的具体地图、UI 模板和任务流程必须根据实际客户端版本、分辨率和 Skill 数据进行适配。

项目不提供协议伪造、进程注入或反作弊绕过功能。

## 23. License

本项目仅用于本地软件自动化研究、工程测试和学习。使用者需要自行遵守相关软件的服务条款和适用法律。
