from dataclasses import dataclass
from typing import Optional

@dataclass
class JobRequestDTO:
    modelId: str
    printerId: Optional[str] = None
    priority: int = 0