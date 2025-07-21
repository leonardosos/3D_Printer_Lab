from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import uuid

@dataclass
class Job:
    id: str
    modelId: str
    assignedPrinterId: Optional[str] = None
    priority: int = 0
    status: str = "pending"
    submittedAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    def __post_init__(self):
        if self.submittedAt is None:
            self.submittedAt = datetime.utcnow()
        if self.updatedAt is None:
            self.updatedAt = datetime.utcnow()
    
    @classmethod
    def create_new(cls, model_id: str, printer_id: Optional[str] = None, priority: int = 0):
        """Create a new job with auto-generated ID and timestamps"""
        job_id = f"job-{str(uuid.uuid4())[:8]}"
        return cls(
            id=job_id,
            modelId=model_id,
            assignedPrinterId=printer_id,
            priority=priority
        )
    
    def update_priority(self, new_priority: int):
        """Update job priority and timestamp"""
        self.priority = new_priority
        self.updatedAt = datetime.utcnow()
    
    def assign_printer(self, printer_id: str):
        """Assign printer to job"""
        self.assignedPrinterId = printer_id
        self.updatedAt = datetime.utcnow()
    
    def update_status(self, new_status: str):
        """Update job status"""
        self.status = new_status
        self.updatedAt = datetime.utcnow()