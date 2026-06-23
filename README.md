# Financial Simulation Dashboard

Transforms Excel financial models into interactive, AI-powered simulation dashboards.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS · Recharts · Zustand |
| Backend | Python 3.11 · FastAPI · openpyxl · pandas |
| AI | Anthropic Claude API (claude-sonnet-4-6) |

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### 3. Tests

```bash
cd backend
pytest tests/ -v
```

## Features

- **Excel Parsing** — distinguishes static inputs from formula cells, builds full dependency graph
- **What-If Simulation** — sliders on all numeric inputs; calculated cells recalculate instantly
- **Synthetic Metrics** — auto-derives LTV/CAC, Break-Even, Cash Runway, Gross Margin when ingredients exist
- **AI Glossary** — click any cell to get a plain-English explanation via Claude
- **Interactive Charts** — Area (cashflow), Bar (revenue vs costs), Pie (budget allocation)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/upload` | Upload `.xlsx`, returns session + parsed cells |
| POST | `/api/simulate` | Apply input overrides, get recalculated values |
| GET | `/api/explain/{session_id}/{cell_id}` | AI explanation for a cell |
| GET | `/health` | Health check |

## Architecture

```
Upload .xlsx
    ↓
excel_parser.py      — openpyxl cell type detection, formula extraction
    ↓
formula_engine.py    — topological sort + safe Python eval
    ↓
metric_synthesizer.py — derive missing KPIs (LTV/CAC, BEP, Runway…)
    ↓
FastAPI routes       — session store, simulation endpoint
    ↓
React frontend       — Zustand store, real-time sliders, Recharts
    ↓
Claude API           — explain any cell on demand
```
