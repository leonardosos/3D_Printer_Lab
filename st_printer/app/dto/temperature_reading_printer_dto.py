# 2.1.2) TemperatureReadingPrinter

from dataclasses import dataclass, asdict
import json

@dataclass
class TemperatureReadingPrinterDTO:
    printerId: str
    temperature: float
    unit: str
    timestamp: str

    def to_json(self) -> str:
        return json.dumps(asdict(self))