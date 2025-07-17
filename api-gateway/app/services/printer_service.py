import os
import yaml
import logging
from app.utils.request_forwarder import forward_request

logger = logging.getLogger('api-gateway')

def _get_config():
    """Load configuration for printer service"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['services']['printer_monitoring']

def get_printers_status():
    """Get printer status from the Printer Monitoring microservice"""
    config = _get_config()
    service_url = config['base_url']
    endpoint = config['endpoints']['get_status']
    
    logger.info(f"Forwarding request to Printer Monitoring service: GET {service_url}{endpoint}")
    
    # Forward the GET request to the printer monitoring microservice
    response_data = forward_request(
        method='GET',
        url=f"{service_url}{endpoint}"
    )
    
    return response_data
