from flask import Blueprint, render_template
from app.services.printer_service import get_printer_status

printers_bp = Blueprint('printers', __name__)

@printers_bp.route('/printers')
def printers_page():
    printers = get_printer_status()
    return render_template('printers.html', printers=printers)

