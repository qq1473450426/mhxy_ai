# CHANGELOG

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
