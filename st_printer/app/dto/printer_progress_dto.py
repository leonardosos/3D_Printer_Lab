# 2.2.2) PrinterProgress.

from dataclasses import dataclass, asdict
import json

@dataclass
class PrinterProgressDTO:
    printerId: str
    jobId: str
    status: str  # "printing"|"idle"|"completed"|"error"
    progress: float
    timestamp: str

    def to_json(self) -> str:
        return json.dumps(asdict(self))