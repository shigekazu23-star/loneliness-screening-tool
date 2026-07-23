# Configuration and Setup Guide

Technical manual for deploying and maintaining the Loneliness Screening
and Visualization Tool. The repository `README.md` is the quick-start
entry point for developers; this document is the authoritative reference
for configuration, so that any deployment can be reproduced from a clean
checkout and maintained without undocumented knowledge (reproducibility
and maintenance are the two goals of this document).

Audience: a developer or administrator deploying the prototype.
Baseline: release v0.2.0 or later.

## 1. Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Operating system | Windows 10/11, macOS, or Linux | Developed on Windows 11; CI proves the stack on Ubuntu |
| Python | 3.12 or newer | CI pins 3.12 |
| Node.js + npm | Node 20 or newer | CI pins Node 22 |
| Git | any recent | version control and rollback |

Python dependencies (installed from `src/backend/requirements.txt`):
`flask`, `flask-cors`, `bcrypt`, `PyJWT`, `pytest`, `pytest-cov`.

Frontend dependencies are locked in `src/frontend/package-lock.json`
(React 18, Vite 5) and installed with `npm ci` for reproducible builds.

## 2. Environment variables and configuration

| Variable | Default | Purpose | Production requirement |
|---|---|---|---|
| `LST_JWT_SECRET` | development-only placeholder in `modules/auth.py` | Signs and verifies JWT session tokens | **Must** be set to a random secret of 32+ characters; never deploy the default |
| `LST_DB_PATH` | `src/backend/data/lst.db` | Location of the SQLite database file | Set to a path on a persistent, backed-up volume |

Other configuration points:

- **Dev API proxy**: the Vite dev server proxies `/api` to
  `http://localhost:5000` (`src/frontend/vite.config.js`). This applies
  to development only; in production the built frontend is served as
  static files and the API is reached same-origin through the web server.
- **CORS**: enabled broadly for development in `app.py`. Restrict the
  allowed origin to the deployed frontend URL in production.
- **Port**: the backend listens on 5000 (`flask run --port 5000`).

## 3. Installation (clean checkout)

```bash
git clone https://github.com/shigekazu23-star/loneliness-screening-tool.git
cd loneliness-screening-tool

# Backend
cd src/backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # Windows
# source .venv/bin/activate && pip install -r requirements.txt  # macOS/Linux
.venv/Scripts/python seed_simulation.py            # optional demo data

# Frontend (second terminal, repo root)
cd src/frontend
npm ci
```

The database schema is created automatically on first backend start
(`repo.init_db`); no manual migration step is required for the prototype.

## 4. Build commands

```bash
cd src/frontend
npm run build        # production bundle -> src/frontend/dist/
```

The backend requires no build step (interpreted Python).

## 5. Run and deploy commands

Development (two terminals):

```bash
cd src/backend && .venv/Scripts/python -m flask --app app run --port 5000
cd src/frontend && npm run dev        # http://localhost:5173
```

Production baseline (single host; the Flask dev server is not for
production use):

```bash
pip install gunicorn                   # deployment-time dependency (Linux host)
export LST_JWT_SECRET="<random 32+ char secret>"
export LST_DB_PATH="/var/lib/lst/lst.db"
gunicorn --workers 2 --bind 127.0.0.1:5000 "app:app"
# Serve src/frontend/dist/ as static files from the web server (nginx or
# equivalent) and reverse-proxy /api to 127.0.0.1:5000.
```

The planned deployment target (Unit 6 deployment plan) is a Docker
container on a PaaS: the container image captures the Python version,
dependencies, and environment defaults so the same artifact runs
identically in every environment, and the two variables above remain the
only per-environment configuration.

## 6. Verification after setup or deploy

```bash
python -m pytest tests -v --cov=src/backend --cov-report=term   # 24 tests pass
curl http://127.0.0.1:5000/api/health                            # {"status": "ok"}
python scripts/evaluate_flag_metrics.py    # reproduces flag reliability numbers
python scripts/measure_latency.py          # latency check against the running server
```

## 7. Maintenance notes

- **Baselines and rollback**: releases are tagged (`v0.1.0`, `v0.2.0`)
  with generated release notes. Roll back by checking out the previous
  tag and redeploying; the SQLite file is independent of the code tree.
- **Change control**: all changes reach `main` through pull requests
  with the CI gate (backend tests + frontend build) green.
- **Backups**: back up the file at `LST_DB_PATH`; it contains all users,
  consents, responses, and flags.
- **Secret rotation**: rotating `LST_JWT_SECRET` invalidates all active
  sessions (users simply log in again); no data is affected.
