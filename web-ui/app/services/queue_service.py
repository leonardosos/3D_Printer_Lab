import requests
import yaml
from app.dto.job_response_dto import JobDTO

def get_api_base_url():
    with open('app/web_conf.yaml') as f:
        config = yaml.safe_load(f)
    return config['api_gateway']['base_url']

def get_job_queue():
    base_url = get_api_base_url()
    response = requests.get(f'{base_url}/jobs')
    response.raise_for_status()
    data = response.json()
    return [JobDTO(**item) for item in data.get('jobs', [])]

def edit_job(job_id, new_priority, new_name=None):
    base_url = get_api_base_url()
    payload = {'priority': new_priority}
    if new_name is not None:
        payload['name'] = new_name
    response = requests.put(f'{base_url}/jobs/{job_id}', json=payload)
    response.raise_for_status()
    return response.ok

def delete_job(job_id):
    base_url = get_api_base_url()
    response = requests.delete(f'{base_url}/jobs/{job_id}')
    response.raise_for_status()
    return response.ok

def add_job(name, priority):
    base_url = get_api_base_url()
    response = requests.post(f'{base_url}/jobs', json={'name': name, 'priority': priority})
    response.raise_for_status()
    return response.ok