# 梦幻西游 AI 多账号主控系统

> 本地 AI 思维 / 多账号 Worker / Windows 窗口自动化 / 状态机 / 掉线重连 / 任务调度 / 日志监控

这是一个面向 Windows 桌面自动化测试的梦幻西游多账号主控框架。项目采用本地结构化 Agent 决策，不调用外部 AI API，也不需要 API Key。

## ⚠️ 使用前说明

- 第一次必须使用 `dry_run=true` 做测试。
- 自动化行为可能违反游戏运营方服务条款或账号规则，请自行确认风险。
- 本项目不实现封包伪造、协议篡改、进程注入或反作弊绕过。
- 不要把账号密码、Cookie、Token 等敏感信息提交到 Git。

## 1. 项目架构

```text
游戏窗口
   ↓
截图 / 模板识别
   ↓
结构化观测
   ↓
LocalReasoningEngine
   ↓
候选动作评分
   ↓
历史失败降权 / 重复动作抑制
   ↓
执行动作
   ↓
结果验证与记忆
   ↓
下一轮
```

每个账号拥有独立 Worker；Monitor 负责健康检查，Scheduler 负责调度，SQLite 与文件日志负责记录运行过程。

## 2. 目录结构

```text
mhxy_ai/
├─ app/                 # API、状态机、服务、Worker
├─ assets/templates/    # OpenCV 模板图片
├─ config/              # 全局参数与账号配置
├─ knowledge/           # 可选 xyq-skills 知识库
├─ tasks/               # JSON 任务
├─ templates/           # Web 页面
├─ static/              # Web 静态资源
├─ tests/               # 测试
├─ logs/                # 运行日志
├─ screenshots/         # 异常/手动截图
├─ data/                # SQLite 数据库
├─ requirements.txt
├─ run.py
└─ start.bat
```

## 3. 环境要求

推荐：

- Windows 10 / 11
- Python 3.11
- Git
- 梦幻西游客户端

检查 Python：

```bat
python --version
```

## 4. 安装

```bat
cd mhxy_ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

或者：

```bat
start.bat
```

启动后访问：

```text
http://127.0.0.1:8000
```

## 5. 第一次测试：dry-run

打开：

```text
config/config.json
```

保持：

```json
{
  "dry_run": true
}
```

先确认窗口枚举、截图、模板识别、状态机、Worker 和日志全部正常，再进行后续测试。

## 6. 多账号配置

编辑：

```text
config/accounts.json
```

一个账号对应一个 Worker，例如：

```json
[
  {"account_id":"A01", "enabled":true, "window_title":"梦幻西游"},
  {"account_id":"A02", "enabled":true, "window_title":"梦幻西游"}
]
```

如果已经知道 HWND，可以直接配置；否则 Worker 会按窗口标题寻找。

推荐顺序：

```text
1 个窗口 → A01 稳定 → 2 个窗口 → 测试掉线恢复 → 再增加账号
```

## 7. 模板识别

模板放在：

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

制作模板时使用当前实际客户端截图，尽量只截取稳定 UI 元素。开发、测试和运行环境建议保持相同分辨率与 Windows DPI 缩放；例如 100% 改成 125% 可能导致模板匹配失败。

## 8. 本地 AI 思维

核心文件：

```text
app/services/ai.py
```

没有任何外部 AI API。决策闭环是：

```text
感知
 ↓
当前状态
 ↓
任务目标
 ↓
生成候选动作
 ↓
条件/置信度评分
 ↓
历史失败动作降权
 ↓
连续重复动作抑制
 ↓
选择动作
 ↓
执行
 ↓
验证结果
 ↓
记忆结果
 ↓
下一轮
```

当前候选动作包括：

```text
RECONNECT
TASK_COMPLETE
BATTLE_ACTION
WAIT_BATTLE
HANDLE_DIALOG
CONTINUE_TASK
WAIT
```

例如发现 `connected=false` 时，`RECONNECT` 会获得最高优先级；某动作连续失败时，该动作下一轮会被降权，从而避免简单死循环。

> 这里的“AI 思维”是可审计的本地结构化 Agent 决策，不是云端大模型隐藏思维链。

## 9. Worker 状态机

正常流程：

```text
STOPPED → STARTING → LOGIN → IDLE → RUNNING → BATTLE
```

异常状态：

```text
DISCONNECTED
RECONNECTING
ERROR
MANUAL_REQUIRED
```

核心文件：

```text
app/core/state_machine.py
app/core/models.py
```

## 10. 掉线检测与重连

典型流程：

```text
正常运行
 ↓
发现窗口/画面异常
 ↓
DISCONNECTED
 ↓
RECONNECTING
 ↓
LOGIN
 ↓
恢复 IDLE/RUNNING
```

连续失败时进入 `MANUAL_REQUIRED`，避免无限重试。

## 11. 自动换号

Scheduler 可以根据 Worker 状态管理备用账号。推荐逻辑：

```text
A01 掉线
 ↓
尝试重连
 ↓
连续失败
 ↓
标记异常
 ↓
Scheduler 调度备用 Worker
```

建议配置合理的失败次数、冷却时间和人工确认条件。

## 12. 任务系统

任务放在：

```text
tasks/
```

基础动作包括：

```text
wait
key
click
find_click
screenshot
```

示例：

```json
{
  "task_name":"demo",
  "steps":[
    {"action":"wait", "seconds":1},
    {"action":"screenshot", "name":"before"}
  ]
}
```

建议从最简单的任务开始，再增加视觉判断与结果验证。

## 13. Web 主控面板

启动后访问：

```text
http://127.0.0.1:8000
```

基础 API：

```text
GET  /api/status
GET  /api/windows
GET  /api/logs
GET  /api/knowledge/search?q=...

POST /api/account/{id}/start
POST /api/account/{id}/stop
POST /api/account/{id}/task
POST /api/account/{id}/screenshot
POST /api/account/{id}/simulate-disconnect
```

## 14. 日志与排障

日志：

```text
logs/controller.log
logs/account_A01.log
logs/account_A02.log
```

数据库：

```text
data/mhxy.db
```

截图：

```text
screenshots/
```

重点搜索：

```text
LOCAL_AI_DECISION
DISCONNECTED
RECONNECT
TASK_COMPLETE
ERROR
```

例如：

```text
LOCAL_AI_DECISION | action=RECONNECT confidence=1.00 reason=连接异常优先恢复
```

如果 Worker 一直 `WAIT`，先检查“截图 → 模板识别 → observation → LOCAL_AI_DECISION”。如果一直重连，检查 `DISCONNECTED → RECONNECTING → LOGIN` 的状态迁移以及对应账号日志。

## 15. xyq-skills 知识库

项目预留：

```text
knowledge/xyq-skills/
```

可以使用你提供的梦幻西游知识库：

```bat
git clone https://github.com/MikiVision/xyq-skills.git knowledge/xyq-skills
```

知识库用于辅助任务层理解游戏系统，与底层窗口控制、视觉识别和状态机解耦。

## 16. 推荐开发流程

### Phase 1：框架

```text
主控启动 → Web 面板 → 窗口枚举 → 截图 → 模板匹配
```

### Phase 2：单账号

```text
A01 → Worker → 简单任务 → 日志
```

### Phase 3：故障恢复

```text
模拟掉线 → Monitor → RECONNECT → 验证结果
```

### Phase 4：多账号

```text
A01 + A02 → 独立 Worker → 独立状态 → 独立日志
```

### Phase 5：本地 Agent

```text
状态 → 候选动作 → 评分 → 历史反馈 → 策略调整
```

## 17. Git 版本管理

推荐：

```text
main/master
 ├─ develop
 ├─ feature/local-ai
 ├─ feature/vision
 ├─ feature/reconnect
 └─ feature/scheduler
```

提交：

```bash
git add .
git commit -m "feat: improve local reasoning"
git push
```

不要提交：

```text
.venv/
*.db
*.log
screenshots/
真实账号密码
Token / Cookie
```

## 18. 后续开发建议

1. 稳定窗口绑定。
2. 统一 Vision 接口。
3. 增加 OCR 状态识别。
4. 完善任务状态机。
5. 增加动作结果验证。
6. 增加 Worker 心跳与超时检测。
7. 完善 Scheduler 冷却/重试策略。
8. 将 Agent 评分参数配置化。
9. 增加历史任务结果统计。
10. 使用 `xyq-skills` 做知识检索辅助任务规划。

## License / Disclaimer

本项目用于个人研究、软件工程和桌面自动化技术测试。请遵守相关软件许可、游戏服务条款以及当地法律法规。
