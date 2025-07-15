import time
import requests
import json

# 1.2.1) get response for global temperature readings

from dataclasses import dataclass, asdict
from typing import List
import json

@dataclass
class TemperatureReadingDTO:
    temperature: float
    source: str
    sourceId: str
    timestamp: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            temperature=data.get("temperature"),
            source=data.get("source"),
            sourceId=data.get("sourceId"),
            timestamp=data.get("timestamp")
        )

@dataclass
class GlobalTemperatureResponseDTO:
    temperatures: List[TemperatureReadingDTO]
    lastUpdated: str

    @classmethod
    def from_dict(cls, data):
        temps = [TemperatureReadingDTO.from_dict(t) for t in data.get("temperatures", [])]
        return cls(
            temperatures=temps,
            lastUpdated=data.get("lastUpdated", "")
        )

    def to_json(self) -> str:
        return json.dumps({
            "temperatures": [asdict(t) for t in self.temperatures],
            "lastUpdated": self.lastUpdated
        })



API_URL = "http://127.0.0.1:8100/temperature"  # Change to your desired address if needed

def pretty_print_response(response):
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Raw Payload: {json.dumps(response.json(), indent=2)}")

        data = response.json()
        temp_data = data.get("temperature", {})
        dto = GlobalTemperatureResponseDTO.from_dict(temp_data)

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Status: {response.status_code}")
        print("Temperatures:")
        for t in dto.temperatures:
            print(f"  - Source: {t.source}, ID: {t.sourceId}, Temp: {t.temperature}°C, Time: {t.timestamp}")
        print(f"Last Updated: {dto.lastUpdated}\n")
    except Exception:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Status: {response.status_code}, Raw Response: {response.text}")

def main():
    while True:
        try:
            response = requests.get(API_URL)
            pretty_print_response(response)
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: {e}")
        time.sleep(40)

if __name__ == "__main__":
    main()