from flask import Blueprint, jsonify, request
from app.services.printer_service import get_printers_status
from app.dto.printer_status_dto import PrinterStatusDTO, PrinterStatusResponseDTO
from app.utils.error_handler import handle_service_error

printers_bp = Blueprint('printers', __name__)

@printers_bp.route('/printers/status', methods=['GET'])
@handle_service_error
def printer_status():
    """Get status of all printers"""
    # Call the service to get printer status
    printers_data = get_printers_status()
    
    # Convert raw data to DTOs for validation and transformation
    printer_dtos = [
        PrinterStatusDTO(
            printerId=printer['printerId'],
            status=printer['status'],
            currentJobId=printer.get('currentJobId'),
            progress=printer.get('progress'),
            temperature=printer.get('temperature'),
            lastUpdated=printer['lastUpdated']
        ) for printer in printers_data.get('printers', [])
    ]
    
    # Create the response DTO
    response_dto = PrinterStatusResponseDTO(printers=printer_dtos)
    
    # Return the validated data
    return jsonify({
        'printers': [vars(printer) for printer in response_dto.printers]
    })
