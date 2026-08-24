# MHXY AI Dashboard Frontend

React + TypeScript + Vite frontend for `mhxy_ai`.

## Tech

- React
- TypeScript
- Vite
- Recharts
- Lucide React

## Start

From the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/api/*` to Django at `http://127.0.0.1:8000`.

## Production build

```powershell
npm run build
```

The generated files are in `frontend/dist`.

## Design baseline

The Dashboard is implemented from the provided Figma reference in file `Vqhmaum8paI2X0b1wSyh8C`, using the `3:4` / `4:2` reference screens as the desktop visual baseline.

The UI intentionally keeps the 1440px desktop proportions while adding responsive layouts for tablets and phones.

## Backend integration

The first screen uses local demo data for visual stability. The status polling already probes:

```text
/api/status/
```

The next integration step is to replace demo task data with Django task/account/worker endpoints without changing the visual component structure.
