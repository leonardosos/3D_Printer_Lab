# 1.2.1) get response for global temperature readings

from dataclasses import dataclass, asdict
from typing import List
import json

@dataclass
class TemperatureReadingDTO:
    temperature: float
    source: str  # "room" | "printer"
    sourceId: str
    timestamp: str

@dataclass
class GlobalTemperatureResponseDTO:
    temperatures: List[TemperatureReadingDTO]
    lastUpdated: str

    def to_json(self) -> str:
        return json.dumps({
            "temperatures": [asdict(t) for t in self.temperatures],
            "lastUpdated": self.lastUpdated
        })
