from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Job:
    id: str
    modelId: str
    assignedPrinterId: Optional[str]
    priority: int
    status: str
    submittedAt: datetime
    updatedAt: datetime