from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FanSpeedMessage(BaseModel):
    """Data Transfer Object for fan speed messages."""
    fanId: str
    speed: int = Field(..., ge=0, le=100)  # Speed between 0 and 100
    actual: Optional[int] = None
    timestamp: str
    
    class Config:
        """Pydantic configuration."""
        extra = "ignore"  # Ignore extra fields
