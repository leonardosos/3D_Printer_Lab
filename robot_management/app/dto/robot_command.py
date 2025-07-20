"""
DTO for robot command messages published to the device/robot/robot{id}/coordinates topic.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json


class RobotCommandDTO:
    """
    DTO for robot command messages.
    Example: { "robotId": "rob-1", "printerId": "printer-1", "x": 120, "y": 45, "z": 10, "speed": 200, "timestamp": "2025-06-15T08:32:05Z" }
    """
    def __init__(
        self, 
        robot_id: str, 
        printer_id: str, 
        x: int, 
        y: int, 
        z: int,
        timestamp: str,
        speed: Optional[int] = None
    ):
        self.robot_id = robot_id
        self.printer_id = printer_id
        self.x = x
        self.y = y
        self.z = z
        self.timestamp = timestamp
        self.speed = speed

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['RobotCommandDTO']:
        """
        Create a RobotCommandDTO from a dictionary.
        Returns None if validation fails.
        """
        if not cls.validate(data):
            return None

        return cls(
            robot_id=data["robotId"],
            printer_id=data["printerId"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            timestamp=data["timestamp"],
            speed=data.get("speed")  # Optional field
        )

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> bool:
        """
        Validate that the robot command data has the correct format.
        """
        if not isinstance(data, dict):
            return False

        # Check required fields
        required_fields = ["robotId", "printerId", "x", "y", "z", "timestamp"]
        if not all(key in data for key in required_fields):
            return False

        # Validate IDs
        if not isinstance(data["robotId"], str) or not data["robotId"].strip():
            return False
        if not isinstance(data["printerId"], str) or not data["printerId"].strip():
            return False

        # Validate coordinates
        for coord in ["x", "y", "z"]:
            if not isinstance(data[coord], (int, float)):
                return False

        # Validate optional speed
        if "speed" in data and not isinstance(data["speed"], (int, float)):
            return False

        # Validate timestamp
        try:
            datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert DTO to dictionary.
        """
        result = {
            "robotId": self.robot_id,
            "printerId": self.printer_id,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "timestamp": self.timestamp
        }
        
        # Add optional fields if present
        if self.speed is not None:
            result["speed"] = self.speed
            
        return result

    def to_json(self) -> str:
        """
        Convert DTO to JSON string.
        """
        return json.dumps(self.to_dict())
