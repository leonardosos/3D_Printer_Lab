from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

# This Dto module defines the GET jobs (both request and response)
@dataclass
class JobDTO:
    """DTO representing a job in the queue"""
    id: str
    modelId: str
    assignedPrinterId: Optional[str] = None
    priority: int = 0
    status: str = "pending"
    submittedAt: str = None
    updatedAt: str = None

    def __post_init__(self):
        # Set default timestamps if not provided
        if self.submittedAt is None:
            self.submittedAt = datetime.utcnow().isoformat() + "Z"
        if self.updatedAt is None:
            self.updatedAt = self.submittedAt

@dataclass
class JobsResponseDTO:
    """DTO representing a list of jobs response"""
    jobs: List[JobDTO]
