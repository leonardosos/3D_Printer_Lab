from dataclasses import dataclass, asdict
from typing import Optional
import json

@dataclass
class JobRequestDTO:
    modelId: str
    printerId: Optional[str] = None
    priority: Optional[int] = 0

    def to_json(self):
        return json.dumps(asdict(self))