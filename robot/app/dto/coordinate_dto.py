"""
Data Transfer Object for robot coordinate commands received via MQTT.
"""
from dataclasses import dataclass
from datetime import datetime
import json
from typing import Optional

@dataclass
class CoordinateDTO:
    """
    DTO representing coordinate command messages received from Robot Management.
    These commands instruct the robot where to move.
    """
    robotId: str
    printerId: str
    x: float
    y: float
    z: float
    timestamp: str
    speed: Optional[int] = None
    
    @classmethod
    def from_json(cls, json_data: str) -> 'CoordinateDTO':
        """
        Create a CoordinateDTO instance from a JSON string.
        
        Args:
            json_data: JSON string containing coordinate command data
            
        Returns:
            CoordinateDTO instance
            
        Raises:
            ValueError: If JSON parsing fails or required fields are missing
        """
        try:
            data = json.loads(json_data)
            return cls(
                robotId=data['robotId'],
                printerId=data['printerId'],
                x=float(data['x']),
                y=float(data['y']),
                z=float(data['z']),
                timestamp=data['timestamp'],
                speed=data.get('speed')  # Optional field
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid coordinate data: {str(e)}")
    
    def validate(self) -> None:
        """
        Validate that the coordinate data is well-formed.
        
        Raises:
            ValueError: If any validation check fails
        """
        if not self.robotId or not isinstance(self.robotId, str):
            raise ValueError("robotId must be a non-empty string")
        
        if not self.printerId or not isinstance(self.printerId, str):
            raise ValueError("printerId must be a non-empty string")
        
        if not isinstance(self.x, (int, float)):
            raise ValueError("x must be a number")
        
        if not isinstance(self.y, (int, float)):
            raise ValueError("y must be a number")
        
        if not isinstance(self.z, (int, float)):
            raise ValueError("z must be a number")
        
        if self.speed is not None and not isinstance(self.speed, int):
            raise ValueError("speed must be an integer if provided")
        
        # Validate timestamp format (ISO 8601)
        try:
            datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("timestamp must be in ISO 8601 format")
    
    def to_dict(self) -> dict:
        """
        Convert the DTO to a dictionary.
        
        Returns:
            Dictionary representation of the DTO
        """
        result = {
            'robotId': self.robotId,
            'printerId': self.printerId,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'timestamp': self.timestamp
        }
        
        if self.speed is not None:
            result['speed'] = self.speed
            
        return result
