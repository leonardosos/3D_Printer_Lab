from dataclasses import dataclass
from typing import Optional
from .job_dto import JobDTO

# This Dto module defines the UPDATE job priority (both request and response)
@dataclass
class UpdateJobRequestDTO:
    """DTO for job update request"""
    priority: Optional[int] = None
    
    def validate(self):
        """Validate the request data"""

        # At least one field must be provided for update
        if self.priority is None:
            raise ValueError("At least one field (priority) must be provided for update")

@dataclass
class UpdateJobResponseDTO:
    """DTO for job update response"""
    job: JobDTO
