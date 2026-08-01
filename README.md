# Loneliness Screening and Visualization Tool for Older Adults

An MSIT Capstone project. A web application that administers the validated
Three-Item Loneliness Scale (Hughes et al., 2004), computes a score,
visualizes the trend over time, and raises a flag when loneliness is
sustained or worsening, so that an authorized caregiver can respond.
Screening, not diagnosis.

## Tech stack

- Frontend: React (Vite), Japanese-first UI with externalized strings
- Backend: Flask (Python), REST API, JWT sessions, bcrypt hashing, RBAC
- Database: SQLite behind a repository layer (replaceable by PostgreSQL)
- CI: GitHub Actions (pytest + frontend build on every push and PR)

## Architecture

Three layers with isolated core logic, per the Unit 3 design
(`design/unit3-figure1-architecture.png`):

| Layer | Code | Modules |
|---|---|---|
| Presentation | `src/frontend/` | Auth, Consent, Questionnaire, Dashboard, Caregiver view |
| Application / Logic | `src/backend/app.py`, `modules/`, `core/` | M1 auth, M2 consent, M3 validation, M4 scoring, M6 trend and flag |
| Data | `src/backend/data/` | M5 repository on SQLite (users, consents, responses, flags) |

`core/` (M4 scoring, M6 trend and flag) imports neither Flask nor SQLite,
so the screening logic stays testable and framework-independent.

## Setup and run (development)

Backend (Python 3.12+):

```
cd src/backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Windows
.venv\Scripts\python seed_simulation.py          # optional demo data
.venv\Scripts\python -m flask --app app run --port 5000
```

Frontend (Node 20+), in a second terminal:

```
cd src/frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` to Flask.

Full prerequisites, environment variables (`LST_JWT_SECRET`,
`LST_DB_PATH`), build and deployment commands, and maintenance notes:
see [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

Demo accounts created by `seed_simulation.py` (password `Passw0rd!demo`):

| Username | Role | Simulated trajectory |
|---|---|---|
| `tanaka` | older adult | stable (no flag) |
| `sato` | older adult | worsening (flag fires) |
| `suzuki` | older adult | improving (no flag) |
| `kaigo` | caregiver | linked to all three |

## Tests

```
python -m pytest tests -v
```

24 tests cover the scoring rules, the trend-linked flag (including the
requirement that a single high score never fires), the consent gate,
role-based access, and immediate effect of consent revocation.

## Repository structure

- `src/`     source code (React frontend, Flask backend)
- `docs/`    documentation (SRS, technical report, configuration guide, figures)
- `design/`  design files (architecture diagram)
- `tests/`   test code
- `scripts/` evaluation scripts (flag reliability metrics, API latency, figures)
- `.github/workflows/`  continuous integration

## Branches

- `main`        stable, demoable build
- `development` integration of new work before merging into main

## Status

Initial implementation (Unit 4): working prototype with auth, revocable
consent, questionnaire, scoring, trend visualization, risk flag, and
caregiver view, validated against simulated trajectories.
