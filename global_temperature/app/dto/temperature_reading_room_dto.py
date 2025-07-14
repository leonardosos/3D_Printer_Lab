# 2.1.1) TemperatureReadingRoom

from dataclasses import dataclass, asdict
import json

@dataclass
class TemperatureReadingRoomDTO:
    sensorId: str
    temperature: float
    unit: str  # "C"
    timestamp: str

    def to_json(self) -> str:
        return json.dumps(asdict(self))
