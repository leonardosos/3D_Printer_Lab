"""
DTO for robot progress messages received from the device/robot/robot{id}/progress topic.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json


class RobotProgressDTO:
    """
    DTO for robot progress messages.
    Example: { "robotId": "rob-1", "printerId": "printer-1", "action": "pick", "status": "in_progress", "timestamp": "2025-06-15T08:32:10Z" }
    """
    VALID_ACTIONS = ["pick", "place", "idle"]
    VALID_STATUSES = ["in_progress", "completed", "error"]

    def __init__(
        self, 
        robot_id: str, 
        printer_id: str, 
        action: str, 
        status: str,
        timestamp: str,
        job_id: Optional[str] = None
    ):
        self.robot_id = robot_id
        self.printer_id = printer_id
        self.action = action
        self.status = status
        self.timestamp = timestamp
        self.job_id = job_id

    @classmethod
    def from_json(cls, json_str: str) -> Optional['RobotProgressDTO']:
        """
        Create a RobotProgressDTO from a JSON string.
        Returns None if validation or parsing fails.
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError:
            return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['RobotProgressDTO']:
        """
        Create a RobotProgressDTO from a dictionary.
        Returns None if validation fails.
        """
        if not cls.validate(data):
            return None

        return cls(
            robot_id=data["robotId"],
            printer_id=data["printerId"],
            action=data["action"],
            status=data["status"],
            timestamp=data["timestamp"],
            job_id=data.get("jobId")  # Optional field
        )

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> bool:
        """
        Validate that the robot progress data has the correct format.
        """
        if not isinstance(data, dict):
            return False

        # Check required fields
        required_fields = ["robotId", "printerId", "action", "status", "timestamp"]
        if not all(key in data for key in required_fields):
            return False

        # Validate IDs
        if not isinstance(data["robotId"], str) or not data["robotId"].strip():
            return False
        if not isinstance(data["printerId"], str) or not data["printerId"].strip():
            return False

        # Validate action
        if data["action"] not in cls.VALID_ACTIONS:
            return False

        # Validate status
        if data["status"] not in cls.VALID_STATUSES:
            return False

        # Validate optional job ID
        if "jobId" in data and (not isinstance(data["jobId"], str) or not data["jobId"].strip()):
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
            "action": self.action,
            "status": self.status,
            "timestamp": self.timestamp
        }
        
        # Add optional fields if present
        if self.job_id:
            result["jobId"] = self.job_id
            
        return result

    def to_json(self) -> str:
        """
        Convert DTO to JSON string.
        """
        return json.dumps(self.to_dict())

    def is_completed(self) -> bool:
        """
        Check if the robot has completed its action.
        """
        return self.status == "completed"

    def is_error(self) -> bool:
        """
        Check if the robot has encountered an error.
        """
        return self.status == "error"
