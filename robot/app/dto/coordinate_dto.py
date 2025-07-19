from datetime import datetime
import json
from typing import Dict, Any, Optional

class CoordinateDTO:
    """
    Data Transfer Object for validating and parsing incoming coordinate commands.
    
    Schema:
    {
      "robotId": "rob-1",
      "printerId": "printer-1",
      "x": 120,
      "y": 45,
      "z": 10,
      "speed": 200,          // optional
      "timestamp": "2025-06-15T08:32:05Z"
    }
    """
    
    def __init__(self, robot_id: str, printer_id: str, x: float, y: float, z: float, 
                 timestamp: str, speed: Optional[float] = None):
        self.robot_id = robot_id
        self.printer_id = printer_id
        self.x = x
        self.y = y
        self.z = z
        self.speed = speed
        self.timestamp = timestamp
    
    @classmethod
    def from_json(cls, json_data: str) -> 'CoordinateDTO':
        """Parse and validate coordinate command from JSON string"""
        try:
            data = json.loads(json_data)
            return cls.from_dict(data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CoordinateDTO':
        """Parse and validate coordinate command from dictionary"""
        # Required fields
        required_fields = ["robotId", "printerId", "x", "y", "z", "timestamp"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Type validation
        if not isinstance(data["x"], (int, float)) or not isinstance(data["y"], (int, float)) or not isinstance(data["z"], (int, float)):
            raise ValueError("Coordinates must be numeric values")
        
        # Optional speed field
        speed = data.get("speed")
        if speed is not None and not isinstance(speed, (int, float)):
            raise ValueError("Speed must be a numeric value")
        
        # Timestamp validation
        try:
            datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise ValueError("Invalid timestamp format. Expected ISO 8601 format.")
        
        return cls(
            robot_id=data["robotId"],
            printer_id=data["printerId"],
            x=float(data["x"]),
            y=float(data["y"]),
            z=float(data["z"]),
            speed=float(speed) if speed is not None else None,
            timestamp=data["timestamp"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the DTO to a dictionary"""
        result = {
            "robotId": self.robot_id,
            "printerId": self.printer_id,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "timestamp": self.timestamp
        }
        if self.speed is not None:
            result["speed"] = self.speed
        return result
    
    def to_json(self) -> str:
        """Convert the DTO to a JSON string"""
        return json.dumps(self.to_dict())
