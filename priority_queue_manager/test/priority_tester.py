import requests
import json

BASE_URL = "http://127.0.0.1:8090"

def pretty_print(method, endpoint, status, response):
    print("="*50)
    print(f"HTTP {method} {endpoint}")
    print(f"Status: {status}")
    print("Response:")
    try:
        print(json.dumps(response, indent=2))
    except Exception:
        print(response)
    print("="*50 + "\n")

def create_job(model_id, printer_id=None, priority=0):
    payload = {
        "modelId": model_id,
        "printerId": printer_id,
        "priority": priority
    }
    resp = requests.post(f"{BASE_URL}/jobs", json=payload)
    pretty_print("POST", "/jobs", resp.status_code, resp.json())
    return resp.json()["job"]["id"]

def get_all_jobs():
    resp = requests.get(f"{BASE_URL}/jobs")
    pretty_print("GET", "/jobs", resp.status_code, resp.json())

def update_job_priority(job_id, new_priority):
    payload = {"priority": new_priority}
    resp = requests.put(f"{BASE_URL}/jobs/{job_id}", json=payload)
    pretty_print("PUT", f"/jobs/{job_id}", resp.status_code, resp.json())

def delete_job(job_id):
    resp = requests.delete(f"{BASE_URL}/jobs/{job_id}")
    try:
        response = resp.json()
    except Exception:
        response = resp.text
    pretty_print("DELETE", f"/jobs/{job_id}", resp.status_code, response)

def get_prioritary_job():
    resp = requests.get(f"{BASE_URL}/prioritary_job")
    pretty_print("GET", "/prioritary_job", resp.status_code, resp.json())

if __name__ == "__main__":
    # Create jobs
    job1 = create_job("model-001", priority=5)
    job2 = create_job("model-002", priority=10)
    job3 = create_job("model-003", priority=3)

    # List all jobs
    get_all_jobs()

    # Update priority
    update_job_priority(job1, 15)

    # Get highest priority job (and remove it)
    get_prioritary_job()

    # List all jobs again
    get_all_jobs()

    # Delete a job
    delete_job(job2)

    # List all jobs again
    get_all_jobs()