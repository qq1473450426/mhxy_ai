# CHANGELOG

## Unreleased - 2026-08-26

### Added

- 新增 `skills/leveling/new_server_fast_leveling.md` 中文新区快速练级 Skill。
- 新增 `engine/leveling.py`，提供按等级阶段、经验收益、移动成本、失败风险和连续执行能力进行任务评分的策略选择器。
- `TaskRunner` 接入新区快速练级策略层，保持原有 Dry Run 默认行为。
- 新增 `GET/POST /api/leveling/strategy/` 策略决策接口，便于 Dashboard 或后续 Worker 调用。
- 新增 `engine/perception.py`，提供 OCR/OpenCV/模板匹配的只读感知接口。
- 新增 `engine/navigation.py`，提供地图路点、路线规划和移动执行接口。
- 新增 `engine/economy.py`，提供任务单位时间收益的基础决策模型。
- 新增 `engine/team.py`、`engine/team_coordinator.py`，提供五开队伍编排、异常暂停和恢复计划。
- 新增 `engine/operations_scheduler.py`，提供每日次数、等级、时间窗口和队伍条件的任务调度。
- 新增 `engine/operations_controller.py`，将每日调度、五开同步和实际 Executor 串成单步安全闭环。
- 新增 `engine/credential_store.py`，使用 Fernet 加密游戏账号密码，API 不返回明文密码。
- 新增 `engine/reconnect.py` 与 `engine/multibox_monitor.py`，支持掉线检测、多次重连和备用账号切换。
- 新增 `dashboard/account_api.py`，提供账号 CRUD、备用账号配置、多开健康检查和手动登录接口。
- 新增 `/api/multibox/health/`，用于检查全部或指定多开账号。
- 前端 `frontend/src/Accounts.tsx` 支持添加、编辑、删除、登录、重连、重连参数和备用账号配置。
- 新增 `engine/login.py`，支持标准登录表单的窗口相对坐标执行，并从后端解密凭据后输入账号密码。
- 新增 `tests/test_login.py` 登录布局配置测试。
- 新增 MySQL 配置支持与 `requirements-mysql.txt`。
- 新增 `docs/多开账号与重连系统.md`、`docs/客户端自动登录.md` 中文部署和安全说明。
- 新增账号安全、重连策略和登录布局测试。

### Design

- 0～69级采用分阶段练级策略，69级默认进入卡级停止状态。
- 每个 `tick()` 只做一次决策或一次执行，禁止在控制器内部无限重试。
- 任务只有收到 `completed=true` 才会增加每日次数，禁止伪造任务完成。
- Skill 只负责知识、条件与任务选择；Windows 自动化继续由 `engine/automation.py` 负责。
- 游戏具体地图、坐标、UI 模板不硬编码到策略层，继续放入地图/导航/战斗 Skill。
- 五开健康检查发现任一账号窗口异常时，默认返回 `PAUSE`，避免其他账号继续执行任务。
- 单账号默认最多重连 3 次，达到上限后按备用账号顺序切换；参数均可在账号配置中修改。
- 密码数据库只保存 Fernet 密文；生产环境必须通过 `MHXY_CREDENTIAL_KEY` 提供独立密钥。
- MySQL 通过环境变量启用，未配置时仍保留 SQLite 本地开发模式。
- 自动登录不处理验证码、滑块或其他安全验证；出现此类状态必须暂停并人工处理。
- `LOGIN_SUBMITTED` 只表示登录按钮已提交，不代表已经进入角色或游戏世界，后续必须由 Perception 层确认登录成功。
- 当前任务次数和收益参数属于可配置的初始模型，不视为服务器实时规则或固定收益承诺；后续应使用真实运行数据校准。

## 2.3.0 - 2026-08-25

### Added

- React + TypeScript + Vite frontend under `frontend/`.
- Figma-aligned GM task dashboard.
- Responsive desktop/tablet/mobile layout.
- KPI cards, filters, task table, status badges, progress bars, pagination.
- Task trend chart and task-type donut chart.
- System announcement panel.
- Vite development proxy from `/api/*` to Django `http://127.0.0.1:8000`.
- Frontend README with installation and development instructions.

### Fixed

- Restored the missing default export from `frontend/src/App.tsx`.
- Restored the `frontend/src/styles.css` entry point used by `main.tsx`.
- Kept `npm run build` compatible with the TypeScript/Vite configuration.

### Notes

- The first dashboard screen keeps deterministic demo task rows for visual comparison with the Figma reference.
- `/api/status/` is probed every two seconds to show backend availability.
- Backend Account/Worker/Task API binding will be added without changing the visual component layer.
