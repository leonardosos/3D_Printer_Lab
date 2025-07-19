from datetime import datetime
import json
from typing import Dict, Any, Literal

class ProgressDTO:
    """
    Data Transfer Object for formatting outgoing progress messages.
    
    Schema:
    {
      "robotId": "rob-1",
      "printerId": "printer-1",
      "action": "idle",      // "pick" | "place" | "idle"
      "status": "completed", // "in_progress" | "completed" | "error"
      "timestamp": "2025-06-15T08:35:45Z"
    }
    """
    
    # Define valid actions and statuses
    ACTION_TYPES = Literal["pick", "place", "idle"]
    STATUS_TYPES = Literal["in_progress", "completed", "error"]
    
    def __init__(self, robot_id: str, printer_id: str, 
                 action: ACTION_TYPES, status: STATUS_TYPES,
                 timestamp: str = None):
        self.robot_id = robot_id
        self.printer_id = printer_id
        
        # Validate action and status
        if action not in ["pick", "place", "idle"]:
            raise ValueError(f"Invalid action: {action}. Must be 'pick', 'place', or 'idle'")
        self.action = action
        
        if status not in ["in_progress", "completed", "error"]:
            raise ValueError(f"Invalid status: {status}. Must be 'in_progress', 'completed', or 'error'")
        self.status = status
        
        # Set timestamp to current time if not provided
        self.timestamp = timestamp or datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressDTO':
        """Parse and validate progress message from dictionary"""
        required_fields = ["robotId", "printerId", "action", "status"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return cls(
            robot_id=data["robotId"],
            printer_id=data["printerId"],
            action=data["action"],
            status=data["status"],
            timestamp=data.get("timestamp")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the DTO to a dictionary"""
        return {
            "robotId": self.robot_id,
            "printerId": self.printer_id,
            "action": self.action,
            "status": self.status,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert the DTO to a JSON string"""
        return json.dumps(self.to_dict())
