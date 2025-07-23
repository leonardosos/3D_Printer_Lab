from flask import Blueprint, render_template
from app.services.temperature_service import get_global_temperature
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # Add this import

temperature_bp = Blueprint('temperature', __name__)

@temperature_bp.route('/temperature')
def temperature_page():
    readings = get_global_temperature()
    sensors = []
    rome_tz = ZoneInfo("Europe/Rome")  # Define Rome timezone
    for r in readings:
        last_updated = getattr(r, "timestamp", "N/A")
        formatted_date = last_updated
        if last_updated and last_updated != "N/A":
            # Try to parse as float epoch first
            try:
                epoch = float(last_updated)
                dt_utc = datetime.fromtimestamp(epoch, tz=timezone.utc)
                dt_rome = dt_utc.astimezone(rome_tz)
                formatted_date = dt_rome.strftime('%d %b %Y, %H:%M')
            except (ValueError, TypeError):
                try:
                    # Handle ISO format with Zulu time
                    iso_date = last_updated.replace("Z", "+00:00")
                    dt_utc = datetime.fromisoformat(iso_date)
                    dt_rome = dt_utc.astimezone(rome_tz)
                    formatted_date = dt_rome.strftime('%d %b %Y, %H:%M')
                except Exception:
                    pass  # fallback to raw string if parsing fails
        sensors.append({
            "name": getattr(r, "sourceId", "Unknown"),
            "value": getattr(r, "temperature", "N/A"),
            "last_updated": formatted_date
        })
    return render_template('temperature.html', sensors=sensors)