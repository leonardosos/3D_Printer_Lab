import os
import yaml
import logging
from app.utils.request_forwarder import forward_request

logger = logging.getLogger('api-gateway')

def _get_config():
    """Load configuration for queue service"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['services']['priority_queue']

def get_all_jobs():
    """Get all jobs from the Priority Queue Manager microservice"""
    config = _get_config()
    service_url = config['base_url']
    endpoint = config['endpoints']['get_jobs']
    
    logger.info(f"Forwarding request to Priority Queue Manager service: GET {service_url}{endpoint}")
    
    # Forward the GET request to the queue microservice
    response_data = forward_request(
        method='GET',
        url=f"{service_url}{endpoint}"
    )
    
    return response_data

def create_job(job_data):
    """Create a new job in the Priority Queue Manager microservice"""
    config = _get_config()
    service_url = config['base_url']
    endpoint = config['endpoints']['add_job']
    
    logger.info(f"Forwarding request to Priority Queue Manager service: POST {service_url}{endpoint}")
    
    # Forward the POST request to the queue microservice
    response_data = forward_request(
        method='POST',
        url=f"{service_url}{endpoint}",
        json=job_data
    )
    
    return response_data

def update_job(job_id, job_data):
    """Update a job in the Priority Queue Manager microservice"""
    config = _get_config()
    service_url = config['base_url']
    endpoint = config['endpoints']['update_job'].replace('{job_id}', job_id)
    
    logger.info(f"Forwarding request to Priority Queue Manager service: PUT {service_url}{endpoint}")
    
    # Forward the PUT request to the queue microservice
    response_data = forward_request(
        method='PUT',
        url=f"{service_url}{endpoint}",
        json=job_data
    )
    
    return response_data

def delete_job(job_id):
    """Delete a job from the Priority Queue Manager microservice"""
    config = _get_config()
    service_url = config['base_url']
    endpoint = config['endpoints']['delete_job'].replace('{job_id}', job_id)
    
    logger.info(f"Forwarding request to Priority Queue Manager service: DELETE {service_url}{endpoint}")
    
    # Forward the DELETE request to the queue microservice
    forward_request(
        method='DELETE',
        url=f"{service_url}{endpoint}"
    )
    
    return None
