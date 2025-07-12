import requests
import yaml
from app.model.printer import PrinterStatus

def get_api_base_url():
    with open('app/web_conf.yaml') as f:
        config = yaml.safe_load(f)
    return config['api_gateway']['base_url']

def get_printer_status():
    base_url = get_api_base_url()
    response = requests.get(f'{base_url}/printers/status')
    response.raise_for_status()
    data = response.json()
    # Extract the list of printers
    return [PrinterStatus(**item) for item in data.get('printers', [])]