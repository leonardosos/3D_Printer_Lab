from dataclasses import dataclass
from typing import Optional, List

@dataclass
class PrinterStatusDTO:
    """DTO representing a printer status"""
    printerId: str
    status: str  # 'idle', 'printing', 'error', etc.
    currentJobId: Optional[str] = None
    progress: Optional[int] = None
    temperature: Optional[float] = None
    lastUpdated: str
    
    def validate(self):
        """Validate the printer status data"""
        if not self.printerId or not isinstance(self.printerId, str):
            raise ValueError("printerId must be a non-empty string")
        
        valid_statuses = ['idle', 'printing', 'error', 'maintenance']
        if self.status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")
        
        if self.progress is not None and not (isinstance(self.progress, int) and 0 <= self.progress <= 100):
            raise ValueError("progress must be an integer between 0 and 100")
        
        if self.temperature is not None and not isinstance(self.temperature, (int, float)):
            raise ValueError("temperature must be a number")
        
        if not self.lastUpdated or not isinstance(self.lastUpdated, str):
            raise ValueError("lastUpdated must be a non-empty string")

@dataclass
class PrinterStatusResponseDTO:
    """DTO representing the printer status response"""
    printers: List[PrinterStatusDTO]
