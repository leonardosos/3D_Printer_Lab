import requests
import yaml
from app.dto.temperature_reading_response_dto import TemperatureReadingDTO
from app.dto.printer_status_response_dto import PrinterStatusDTO
from app.dto.job_response_dto import JobDTO

def get_api_base_url():
    with open('app/web_conf.yaml') as f:
        config = yaml.safe_load(f)
    return config['api_gateway']['base_url']

def get_latest_room_temperature():
    base_url = get_api_base_url()
    resp = requests.get(f"{base_url}/temperature/global")
    resp.raise_for_status()
    data = resp.json()
    # Build a list of temperature readings from the response
    # for pass through to the DTO constructor
    temps = [TemperatureReadingDTO(**t) for t in data.get("temperatures", []) if t.get("source") == "room"]
    # Find the latest temperature reading
    if temps:
        latest = max(temps, key=lambda t: t.timestamp)
        return latest.temperature
    return None

def get_printers_online_count():
    base_url = get_api_base_url()
    resp = requests.get(f"{base_url}/printers/status")
    resp.raise_for_status()
    data = resp.json()
    # Do the same as above, but for printers
    printers = [PrinterStatusDTO(**p) for p in data.get("printers", [])]
    online = [p for p in printers if p.status in ("online", "idle", "printing")]
    # Count the number of online printers
    return len(online)

def get_jobs_in_queue_count():
    base_url = get_api_base_url()
    resp = requests.get(f"{base_url}/jobs")
    resp.raise_for_status()
    data = resp.json()
    # Again, build a list of jobs from the response
    jobs = [JobDTO(**j) for j in data.get("jobs", [])]
    # Count the number of jobs in the queue
    return len(jobs)