from flask import Blueprint, render_template
from app.services.printer_service import get_printer_status
from datetime import datetime

printers_bp = Blueprint('printers', __name__)

@printers_bp.route('/printers')
def printers_page():
    printers = get_printer_status()
    for printer in printers:
        if printer.lastUpdated:
            try:
                dt = datetime.fromisoformat(printer.lastUpdated)
                printer.lastUpdated = dt.strftime('%d %b %Y, %H:%M')
            except Exception:
                pass  # fallback to raw string if parsing fails
    return render_template('printers.html', printers=printers)

