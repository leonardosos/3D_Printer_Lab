from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TemperatureReadingDTO:
    """DTO representing a single temperature reading"""
    temperature: float
    source: str  # 'room' or 'printer'
    sourceId: str
    timestamp: str
    
    def validate(self):
        """Validate the temperature reading data"""
        if not isinstance(self.temperature, (int, float)):
            raise ValueError("temperature must be a number")
        
        if self.source not in ['room', 'printer']:
            raise ValueError("source must be either 'room' or 'printer'")
        
        if not self.sourceId or not isinstance(self.sourceId, str):
            raise ValueError("sourceId must be a non-empty string")
        
        if not self.timestamp or not isinstance(self.timestamp, str):
            raise ValueError("timestamp must be a non-empty string")

@dataclass
class TemperatureResponseDTO:
    """DTO representing the global temperature response"""
    temperatures: List[TemperatureReadingDTO]
    lastUpdated: str = ""  # Added default value here
