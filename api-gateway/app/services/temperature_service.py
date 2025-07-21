import os
import yaml
import logging
from app.utils.request_forwarder import forward_request

logger = logging.getLogger('api-gateway')

def _get_config():
    """Load configuration for temperature service"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['services']['global_temperature']

def get_global_temperature():
    """Get global temperature data from the Global Temperature microservice"""
    config = _get_config()
    service_url = config['base_url']
    endpoint = config['endpoints']['get_temperatures']
    
    logger.info(f"Forwarding request to Global Temperature service: GET {service_url}{endpoint}")
    
    # Forward the GET request to the temperature microservice
    response_data = forward_request(
        method='GET',
        url=f"{service_url}{endpoint}"
    )
    
    return response_data
