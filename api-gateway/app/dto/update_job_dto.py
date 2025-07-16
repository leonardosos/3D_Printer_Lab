from dataclasses import dataclass
from typing import Optional
from .job_dto import JobDTO

@dataclass
class UpdateJobRequestDTO:
    """DTO for job update request"""
    priority: Optional[int] = None
    
    def validate(self):
        """Validate the request data"""
        if self.priority is not None and not isinstance(self.priority, int):
            raise ValueError("priority must be an integer if provided")
        
        # At least one field must be provided for update
        if self.priority is None:
            raise ValueError("At least one field (priority) must be provided for update")

@dataclass
class UpdateJobResponseDTO:
    """DTO for job update response"""
    job: JobDTO
