"""
Data Transfer Object for robot progress updates sent via MQTT.
"""
from dataclasses import dataclass
from datetime import datetime
import json
from enum import Enum, auto

class RobotAction(str, Enum):
    """Possible robot actions."""
    IDLE = "idle"
    PICK = "pick"
    PLACE = "place"

class ActionStatus(str, Enum):
    """Possible status of robot actions."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class ProgressDTO:
    """
    DTO representing progress update messages sent by the robot.
    These messages inform about the robot's current action and status.
    """
    robotId: str
    printerId: str
    action: str  # Using string to be JSON-friendly, should be a RobotAction value
    status: str  # Using string to be JSON-friendly, should be an ActionStatus value
    timestamp: str
    
    @classmethod
    def create_completion_message(cls, robot_id: str, printer_id: str) -> 'ProgressDTO':
        """
        Create a progress DTO indicating the robot has completed its cycle and is idle.
        
        Args:
            robot_id: The ID of the robot
            printer_id: The ID of the printer that was serviced
            
        Returns:
            ProgressDTO instance with idle action and completed status
        """
        return cls(
            robotId=robot_id,
            printerId=printer_id,
            action=RobotAction.IDLE.value,
            status=ActionStatus.COMPLETED.value,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def validate(self) -> None:
        """
        Validate that the progress data is well-formed.
        
        Raises:
            ValueError: If any validation check fails
        """
        if not self.robotId or not isinstance(self.robotId, str):
            raise ValueError("robotId must be a non-empty string")
        
        if not self.printerId or not isinstance(self.printerId, str):
            raise ValueError("printerId must be a non-empty string")
        
        # Validate action
        if self.action not in [a.value for a in RobotAction]:
            raise ValueError(f"action must be one of {[a.value for a in RobotAction]}")
        
        # Validate status
        if self.status not in [s.value for s in ActionStatus]:
            raise ValueError(f"status must be one of {[s.value for s in ActionStatus]}")
        
        # Validate timestamp format (ISO 8601)
        try:
            datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("timestamp must be in ISO 8601 format")
    
    def to_json(self) -> str:
        """
        Convert the DTO to a JSON string.
        
        Returns:
            JSON string representation of the DTO
        """
        return json.dumps({
            'robotId': self.robotId,
            'printerId': self.printerId,
            'action': self.action,
            'status': self.status,
            'timestamp': self.timestamp
        })
    
    def to_dict(self) -> dict:
        """
        Convert the DTO to a dictionary.
        
        Returns:
            Dictionary representation of the DTO
        """
        return {
            'robotId': self.robotId,
            'printerId': self.printerId,
            'action': self.action,
            'status': self.status,
            'timestamp': self.timestamp
        }
