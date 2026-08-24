# 梦幻西游 AI 多账号主控台（Django）

当前主程序已经从 FastAPI 切换到 Django。主控台采用响应式布局，电脑和手机浏览器均可访问。

## 已完成

- Django Web 主控台
- 手机/电脑自适应仪表盘
- 添加账号
- 账号密码登录配置
- 扫码登录模式配置
- 游戏客户端 EXE 路径
- 自动启动客户端基础流程
- 游戏窗口枚举 / HWND
- 每账号 Worker 状态
- 当前任务 / 进度 / 重连次数
- 每账号独立日志
- SQLite 数据库
- OpenCV / pyautogui / Windows 自动化依赖
- `skills/` 知识与坐标层预留
- Python 3.14 依赖兼容组合

## 安装

Windows：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

电脑访问：

```text
http://127.0.0.1:8000
```

手机与电脑在同一局域网时：

```text
http://电脑IP:8000
```

也可以运行：

```bat
start.bat
```

## 添加账号

点击「添加账号」：

- 显示名称
- 游戏账号
- 登录方式
- 密码
- 游戏客户端 EXE
- 窗口标题

> 密码字段目前是开发版存储。正式使用建议接 Windows Credential Manager / DPAPI，不要把真实密码长期明文保存。

## 扫码登录

主控台保留扫码登录模式和二维码保存能力的接口位置。

真实的梦幻西游登录二维码应由游戏客户端或官方登录流程产生。本项目不伪造网易登录协议，也不通过封包模拟登录。

后续可以接入：

```text
客户端二维码
      ↓
主控台捕获/读取
      ↓
Web UI 显示
      ↓
手机长按/下载
      ↓
保存到相册
```

## 自动登录

当前 Worker 的基础流程：

```text
启动 Worker
 ↓
检查已有游戏窗口
 ↓
没有窗口 → 启动配置的 EXE
 ↓
等待窗口出现
 ↓
进入 LOGIN
 ↓
进入 IDLE
 ↓
持续监控
```

如果客户端已经打开，后续版本应按客户端实际支持方式创建/选择登录窗口，而不是重复启动已有客户端。

## 游戏自动化架构

目标架构：

```text
Django Dashboard
        │
        ├── Account Manager
        ├── Worker Manager
        ├── Monitor
        ├── Scheduler
        └── Log Manager
                │
                ▼
          Local Agent
                │
        ┌───────┴────────┐
        ▼                ▼
      Vision            Skill
        │                │
        └───────┬────────┘
                ▼
          Automation Engine
                │
                ▼
          游戏窗口 / 客户端
```

本地 Agent 采用结构化决策：

```text
感知
 ↓
状态
 ↓
任务目标
 ↓
Skill 查询
 ↓
候选动作
 ↓
评分
 ↓
执行
 ↓
结果验证
 ↓
记忆
```

## Skill

你提供的：

```text
https://github.com/MikiVision/xyq-skills
```

建议作为 `skills/` 下的知识库。

可以利用其中的位置、NPC、任务、地图、战斗等信息构建：

```text
地图坐标
NPC 坐标
任务目标
寻路节点
战斗状态
日常任务步骤
```

后续自动寻路可以采用：

```text
当前位置
 ↓
目标位置
 ↓
Skill 获取路径节点
 ↓
窗口坐标/画面识别
 ↓
逐节点移动
 ↓
到达确认
```

自动打怪：

```text
寻找目标
 ↓
进入战斗
 ↓
识别战斗 UI
 ↓
选择技能/普通攻击
 ↓
等待回合结果
 ↓
战斗结束检测
 ↓
继续任务
```

自动日常：

```text
任务选择
 ↓
领取
 ↓
寻路
 ↓
交互
 ↓
战斗
 ↓
奖励/完成检测
 ↓
下一环
```

## 重要边界

本项目的自动化执行层采用窗口、截图、模板、坐标和正常用户输入。

不实现：

- 游戏进程注入
- 封包伪造
- 网络协议篡改
- 绕过反作弊
- 破解客户端
- 伪造官方登录协议

## 当前状态

Django 主控台和账号管理基础已经迁移到 `main`。

下一阶段重点：

1. Monitor 后台线程
2. 自动重连
3. 自动换号
4. Skill 坐标解析
5. 自动寻路
6. 战斗 UI 状态机
7. 日常任务编排
8. WebSocket 实时状态
9. 二维码真实客户端登录流程接入
10. 密码使用 Windows Credential Manager / DPAPI 加密
