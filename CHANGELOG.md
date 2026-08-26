# CHANGELOG

## Unreleased - 2026-08-26

### Added

- 新增 `skills/leveling/new_server_fast_leveling.md` 中文新区快速练级 Skill。
- 新增 `engine/leveling.py`，提供按等级阶段、经验收益、移动成本、失败风险和连续执行能力进行任务评分的策略选择器。
- `TaskRunner` 接入新区快速练级策略层，保持原有 Dry Run 默认行为。
- 新增 `GET/POST /api/leveling/strategy/` 策略决策接口，便于 Dashboard 或后续 Worker 调用。

### Design

- 0～69级采用分阶段练级策略，69级默认进入卡级停止状态。
- Skill 只负责知识、条件与任务选择；Windows 自动化继续由 `engine/automation.py` 负责。
- 游戏具体地图、坐标、UI 模板不硬编码到策略层，继续放入地图/导航/战斗 Skill。
- 发生窗口丢失、Skill 缺失、任务前置条件不满足或连续失败时，优先进入安全待机/异常状态。

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
