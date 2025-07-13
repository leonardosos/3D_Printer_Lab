import requests
import yaml
from app.dto.temperature_reading_response_dto import TemperatureReadingDTO

def get_api_base_url():
    with open('app/web_conf.yaml') as f:
        config = yaml.safe_load(f)
    return config['api_gateway']['base_url']

def get_global_temperature():
    base_url = get_api_base_url()
    response = requests.get(f'{base_url}/temperature/global')
    response.raise_for_status()
    data = response.json()
    # Create a list of TemperatureReadingDTO from the response data
    return [TemperatureReadingDTO(**r) for r in data.get('temperatures', [])]