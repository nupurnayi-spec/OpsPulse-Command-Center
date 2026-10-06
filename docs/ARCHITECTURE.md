# OpsPulse Architecture

Presentation: Jinja templates in `templates/`.

Application: Flask routes in `app.py`.

Telemetry: `psutil` for local operating-system metrics.

Persistence: SQLite for asset and incident state.

Reporting: CSV export.

API: `/api/overview` exposes operational KPIs as JSON.

```text
Telemetry + Asset Data
        |
        v
      Flask
     /  |  \
Dashboard API Reports
   |
Incidents
```
