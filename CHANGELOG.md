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
- 新增 `skills/operations/daily_schedule.json` 与 `docs/新区运营调度.md`，记录新区五开运营的初始配置和中文开发规范。
- 新增每日调度、五开同步相关测试。

### Design

- 0～69级采用分阶段练级策略，69级默认进入卡级停止状态。
- 每个 `tick()` 只做一次决策或一次执行，禁止在控制器内部无限重试。
- 任务只有收到 `completed=true` 才会增加每日次数，禁止伪造任务完成。
- Skill 只负责知识、条件与任务选择；Windows 自动化继续由 `engine/automation.py` 负责。
- 游戏具体地图、坐标、UI 模板不硬编码到策略层，继续放入地图/导航/战斗 Skill。
- 五开中任一账号出现掉线、卡死、窗口丢失或错误状态时，默认暂停队伍并生成恢复计划。
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
