import requests
import yaml
from app.dto.printer_status_response_dto import PrinterStatusDTO

def get_api_base_url():
    with open('app/web_conf.yaml') as f:
        config = yaml.safe_load(f)
    return config['api_gateway']['base_url']

def get_printer_status():
    base_url = get_api_base_url()
    try:
        response = requests.get(f'{base_url}/printers/status', timeout=5)
        response.raise_for_status()
        data = response.json()
        # Create a list of PrinterStatusDTO from the response data
        return [PrinterStatusDTO(**item) for item in data.get('printers', [])]
    except (requests.RequestException, ValueError, KeyError):
        return []