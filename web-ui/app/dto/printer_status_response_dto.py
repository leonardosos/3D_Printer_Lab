from dataclasses import dataclass, asdict
from typing import List, Optional
import json

@dataclass
class PrinterStatusDTO:
    printerId: str
    status: str  # "idle" | "printing" | "error"
    currentJobId: Optional[str] = None
    modelUrl: Optional[str] = None
    progress: Optional[int] = None  # 0–100
    temperature: Optional[float] = None
    lastUpdated: str = ""  # ISO 8601

@dataclass
class PrinterStatusResponseDTO:
    printers: List[PrinterStatusDTO]

    def to_json(self):
        return json.dumps({
            "printers": [asdict(p) for p in self.printers]
        })