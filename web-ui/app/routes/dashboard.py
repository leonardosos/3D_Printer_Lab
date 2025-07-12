from flask import Blueprint, render_template
import requests
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

def get_room_temperature():
    # Fetch all temperature readings
    resp = requests.get("http://localhost:8080/temperature/global")
    data = resp.json()
    # Find the latest room temperature
    room_temps = [t for t in data["temperatures"] if t["source"] == "room"]
    # Get the most recent by timestamp
    if room_temps:
        latest = max(room_temps, key=lambda t: t["timestamp"])
        return latest["temperature"]
    return None

def get_printers_online():
    # Fetch printer statuses
    resp = requests.get("http://localhost:8080/printers/status")
    data = resp.json()
    # Count printers with status 'online' or 'idle' or 'printing'
    online = [p for p in data["printers"] if p["status"] in ("online", "idle", "printing")]
    return len(online)

def get_jobs_in_queue():
    # Fetch jobs in the queue
    resp = requests.get("http://localhost:8080/jobs")
    data = resp.json()
    # Return the number of jobs
    return len(data.get("jobs", []))

@dashboard_bp.route("/")
def dashboard():
    global_temp = get_room_temperature()
    printers_online = get_printers_online()
    jobs_in_queue = get_jobs_in_queue()
    year = datetime.now().year
    return render_template(
        "dashboard.html",
        global_temp=global_temp,
        printers_online=printers_online,
        jobs_in_queue=jobs_in_queue,
        year=year
    )