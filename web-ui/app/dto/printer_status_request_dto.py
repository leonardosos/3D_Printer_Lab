# No request body for GET /printers/status
from dataclasses import dataclass, asdict
import json

@dataclass
class PrinterStatusRequestDTO:
    def to_json(self):
        return json.dumps(asdict(self))