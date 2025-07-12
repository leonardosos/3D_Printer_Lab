from dataclasses import dataclass, asdict
from typing import List, Optional
import json

@dataclass
class PrinterStatusDTO:
    printerId: str
    status: str
    currentJobId: Optional[str] = None
    progress: Optional[float] = None
    temperature: Optional[float] = None
    lastUpdated: str = ""

@dataclass
class PrinterStatusResponseDTO:
    printers: List[PrinterStatusDTO]

    def to_json(self):
        return json.dumps({
            "printers": [asdict(p) for p in self.printers]
        })