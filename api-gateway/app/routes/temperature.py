from flask import Blueprint, jsonify, request
from app.services.temperature_service import get_global_temperature
from app.dto.temperature_dto import TemperatureResponseDTO, TemperatureReadingDTO
from app.utils.error_handler import handle_service_error

temperature_bp = Blueprint('temperature', __name__)

@temperature_bp.route('/temperature/global', methods=['GET'])
@handle_service_error
def global_temperature():
    """Get global temperature data from all sensors"""
    # Call the service to get temperature data
    temperature_data = get_global_temperature()
    
    # Convert raw data to DTOs for validation and transformation
    temperature_readings = [
        TemperatureReadingDTO(
            temperature=reading['temperature'],
            source=reading['source'],
            sourceId=reading['sourceId'],
            timestamp=reading['timestamp']
        ) for reading in temperature_data.get('temperatures', [])
    ]
    
    # Create the response DTO
    response_dto = TemperatureResponseDTO(
        temperatures=temperature_readings,
        lastUpdated=temperature_data.get('lastUpdated', '')
    )
    
    # Return the validated data
    return jsonify({
        'temperatures': [vars(reading) for reading in response_dto.temperatures],
        'lastUpdated': response_dto.lastUpdated
    })
