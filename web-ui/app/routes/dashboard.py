from flask import Blueprint, render_template
from datetime import datetime
from app.services.dashboard_service import (
    get_latest_room_temperature,
    get_printers_online_count,
    get_jobs_in_queue_count
)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/")
def dashboard():
    global_temp = get_latest_room_temperature()
    printers_online = get_printers_online_count()
    jobs_in_queue = get_jobs_in_queue_count()
    year = datetime.now().year
    return render_template(
        "dashboard.html",
        global_temp=global_temp,
        printers_online=printers_online,
        jobs_in_queue=jobs_in_queue,
        year=year
    )