import requests

QUEUE_MANAGER_URL = "http://localhost:8090"

def forward_get_jobs():
    response = requests.get(f"{QUEUE_MANAGER_URL}/jobs")
    return (response.content, response.status_code, response.headers.items())

def forward_post_job(payload):
    response = requests.post(f"{QUEUE_MANAGER_URL}/jobs", json=payload)
    return (response.content, response.status_code, response.headers.items())

def forward_put_job(job_id, payload):
    response = requests.put(f"{QUEUE_MANAGER_URL}/jobs/{job_id}", json=payload)
    return (response.content, response.status_code, response.headers.items())
