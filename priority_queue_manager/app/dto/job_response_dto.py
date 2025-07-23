from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime
import json

@dataclass
class JobResponseDTO:
    id: str
    modelId: str
    assignedPrinterId: Optional[str] = None
    priority: int = 0
    status: str = "pending"
    submittedAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    def to_dict(self):
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        if self.submittedAt:
            data['submittedAt'] = self.submittedAt.isoformat() + 'Z'
        if self.updatedAt:
            data['updatedAt'] = self.updatedAt.isoformat() + 'Z'
        return data