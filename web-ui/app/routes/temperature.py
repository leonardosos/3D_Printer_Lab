from flask import Blueprint, render_template
from app.services.temperature_service import get_global_temperature

temperature_bp = Blueprint('temperature', __name__)

@temperature_bp.route('/temperature')
def temperature_page():
    readings = get_global_temperature()
    sensors = [
        {
            "name": r.sourceId if hasattr(r, "sourceId") else "Unknown",
            "value": r.temperature if hasattr(r, "temperature") else "N/A",
            "last_updated": r.timestamp if hasattr(r, "timestamp") else "N/A"
        }
        for r in readings
    ]
    return render_template('temperature.html', sensors=sensors)