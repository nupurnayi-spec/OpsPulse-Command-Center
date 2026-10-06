from flask import Flask, render_template, jsonify, redirect, url_for, flash, Response
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3, csv, io, psutil

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "opspulse.db"
app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-in-production"

def db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS assets(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, asset_type TEXT,
            location TEXT, status TEXT, health INTEGER, criticality TEXT, last_event TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS incidents(
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, severity TEXT,
            asset TEXT, status TEXT, created_at TEXT)""")
        if conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0] == 0:
            rows = [
                ("Substation Alpha","Substation","Zone A","Healthy",96,"Critical","No active issue"),
                ("Transformer T-204","Transformer","Zone A","Warning",78,"Critical","Temperature rising"),
                ("CVT-17","CVT","Zone B","Healthy",91,"High","Inspection completed"),
                ("Isolator I-08","Isolator","Zone B","Critical",54,"High","AHI threshold exceeded"),
                ("Transmission Line L-12","Transmission Line","Zone C","Healthy",94,"Medium","Visual inspection passed"),
                ("Protection Panel P-09","Protection","Zone C","Healthy",89,"High","No active issue")]
            conn.executemany("INSERT INTO assets(name,asset_type,location,status,health,criticality,last_event) VALUES(?,?,?,?,?,?,?)", rows)
        if conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0] == 0:
            now = datetime.now()
            rows = [
                ("Isolator health below threshold","Critical","Isolator I-08","Open"),
                ("Transformer temperature trend rising","Warning","Transformer T-204","Investigating"),
                ("Scheduled inspection completed","Info","CVT-17","Closed")]
            conn.executemany("INSERT INTO incidents(title,severity,asset,status,created_at) VALUES(?,?,?,?,?)",
                [(a,b,c,d,(now-timedelta(hours=i*3)).strftime("%Y-%m-%d %H:%M")) for i,(a,b,c,d) in enumerate(rows)])

def system_snapshot():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    return {"cpu": round(psutil.cpu_percent(interval=.15),1),
            "memory": round(mem.percent,1), "disk": round(disk.percent,1),
            "processes": len(psutil.pids()),
            "network_sent_mb": round(net.bytes_sent/1024**2,1),
            "network_recv_mb": round(net.bytes_recv/1024**2,1),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@app.route("/")
def dashboard():
    with db() as conn:
        assets = conn.execute("SELECT * FROM assets ORDER BY health ASC").fetchall()
        incidents = conn.execute("SELECT * FROM incidents ORDER BY id DESC LIMIT 5").fetchall()
    avg = round(sum(a["health"] for a in assets)/len(assets),1) if assets else 0
    return render_template("dashboard.html", assets=assets, incidents=incidents,
                           snapshot=system_snapshot(), avg_health=avg)

@app.route("/assets")
def assets():
    with db() as conn: rows = conn.execute("SELECT * FROM assets ORDER BY health ASC").fetchall()
    return render_template("assets.html", assets=rows)

@app.route("/incidents")
def incidents():
    with db() as conn: rows = conn.execute("SELECT * FROM incidents ORDER BY id DESC").fetchall()
    return render_template("incidents.html", incidents=rows)

@app.route("/analytics")
def analytics():
    with db() as conn: assets = conn.execute("SELECT * FROM assets").fetchall()
    avg = round(sum(a["health"] for a in assets)/len(assets),1)
    return render_template("analytics.html", assets=assets, avg_health=avg)

@app.route("/reports")
def reports(): return render_template("reports.html")

@app.route("/reports/assets.csv")
def asset_report():
    with db() as conn: rows = conn.execute("SELECT name,asset_type,location,status,health,criticality,last_event FROM assets").fetchall()
    out = io.StringIO(); writer = csv.writer(out)
    writer.writerow(["Asset","Type","Location","Status","Health","Criticality","Last Event"])
    writer.writerows([tuple(r) for r in rows])
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment; filename=opspulse_asset_health.csv"})

@app.route("/api/overview")
def api_overview():
    with db() as conn:
        assets = conn.execute("SELECT * FROM assets").fetchall()
        incidents = conn.execute("SELECT * FROM incidents").fetchall()
    return jsonify({"generated_at": datetime.now().isoformat(), "system": system_snapshot(),
        "asset_count": len(assets),
        "average_asset_health": round(sum(a["health"] for a in assets)/len(assets),1),
        "critical_assets": sum(a["status"]=="Critical" for a in assets),
        "open_incidents": sum(i["status"]!="Closed" for i in incidents)})

@app.post("/incidents/<int:incident_id>/close")
def close_incident(incident_id):
    with db() as conn: conn.execute("UPDATE incidents SET status='Closed' WHERE id=?", (incident_id,))
    flash("Incident marked as closed.","success")
    return redirect(url_for("incidents"))

@app.route("/settings")
def settings(): return render_template("settings.html")

init_db()
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
