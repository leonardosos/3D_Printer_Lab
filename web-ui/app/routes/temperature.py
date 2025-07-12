from flask import Blueprint, render_template
from app.services.temperature_service import get_global_temperature

temperature_bp = Blueprint('temperature', __name__)

@temperature_bp.route('/temperature')
def temperature_page():
    readings = get_global_temperature()
    sensors = [
        {
            "name": r.get("sourceId", "Unknown"),
            "value": r.get("temperature", "N/A"),
            "last_updated": r.get("timestamp", "N/A")
        }
        for r in readings
    ]
    return render_template('temperature.html', sensors=sensors)