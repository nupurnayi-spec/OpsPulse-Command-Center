# OpsPulse Command Center

A portfolio-grade industrial operations dashboard built with Python and Flask.

> Uses synthetic/demo asset data plus local machine telemetry. No proprietary company data is included.

## Features
- Asset Health Index-style scoring
- Asset inventory and criticality
- Incident management
- CPU, memory, disk, process and network telemetry
- Operations dashboard
- Analytics
- REST API
- CSV reporting
- SQLite persistence
- Responsive dark enterprise UI

## Architecture

```text
Browser
   |
   v
Flask Application
   +---- Asset & Incident Data ---- SQLite
   +---- Local Telemetry ---------- psutil
   +---- REST API ----------------- JSON
   +---- Reporting ---------------- CSV
```

## Run

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## API
GET `/api/overview`

## Future enterprise upgrades
Authentication/RBAC, PostgreSQL, historical telemetry, WebSockets, remote agents, notifications, audit logs, Docker and CI/CD.
