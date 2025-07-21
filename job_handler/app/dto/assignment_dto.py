from dataclasses import dataclass
from typing import Dict

@dataclass
class Assignment:
    jobId: str
    modelUrl: str
    filamentType: str
    estimatedTime: int
    priority: int
    assignedAt: str  # or datetime if you want to parse it
    parameters: Dict[str, float | int]