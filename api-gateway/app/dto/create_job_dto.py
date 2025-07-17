from dataclasses import dataclass
from typing import Optional
from .job_dto import JobDTO

# This Dto module defines the POST jobs (both request and response)
@dataclass
class CreateJobRequestDTO:
    """DTO for job creation request"""
    modelId: str
    printerId: Optional[str] = None  # Optional preferred printer
    priority: int = 0  # Default priority

    def validate(self):
        """Validate the request data"""
        if not self.modelId or not isinstance(self.modelId, str):
            raise ValueError("modelId must be a non-empty string")
        
        if self.printerId is not None and not isinstance(self.printerId, str):
            raise ValueError("printerId must be a string if provided")
        
        if not isinstance(self.priority, int):
            raise ValueError("priority must be an integer")

@dataclass
class CreateJobResponseDTO:
    """DTO for job creation response"""
    modelId: str
    priority: int
