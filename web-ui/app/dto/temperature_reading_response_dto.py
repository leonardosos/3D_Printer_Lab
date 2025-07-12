from dataclasses import dataclass, asdict
from typing import List
import json

@dataclass
class TemperatureReadingDTO:
    temperature: float
    source: str
    sourceId: str
    timestamp: str

@dataclass
class TemperatureReadingResponseDTO:
    temperatures: List[TemperatureReadingDTO]
    lastUpdated: str

    def to_json(self):
        return json.dumps({
            "temperatures": [asdict(t) for t in self.temperatures],
            "lastUpdated": self.lastUpdated
        })