# CHANGELOG

## V2.1.0-dev — 2026-08-25

### UI
- 新增 GM 任务管理后台风格 Dashboard。
- 左侧固定导航、顶部用户区、任务筛选、统计卡片、任务列表、趋势图、类型分布、系统公告。
- 新增手机端响应式布局和侧边栏折叠。
- 新增 `dashboard/static/gm_dashboard.css`，避免修改旧兼容样式文件。

### Dashboard
- 保留现有 Django Dashboard 数据来源。
- `/api/status/` 每 2 秒刷新账号/Worker 状态。
- 任务列表展示账号、任务、状态、进度、消息和重连次数。

### 工程规范
- `main` 作为稳定基线。
- `dev` 作为开发分支。
- 开发版本统一标记 `V2.x.x-dev`。
- README 增加分支、版本、Commit 和验证规范。

### 兼容性
- 继续使用 Django 唯一 Web 框架。
- 不引入 FastAPI、Uvicorn、Jinja2、Pydantic。
- Windows GUI 模块继续通过 `pywin32` 提供，不使用独立 `win32gui` 包。

### 验证
- UI 代码基于当前 `main` 无报错基线开发。
- 后续合并 `main` 前必须执行：
  - `python manage.py check`
  - `python manage.py migrate`
  - 浏览器访问 Dashboard
  - 手机局域网访问 Dashboard

## 版本记录规则

每次 `dev` 修改必须追加版本记录，并说明：

- 修改内容
- 影响范围
- 依赖变化
- 数据库 migration 变化
- 验证方式
- 已知限制
