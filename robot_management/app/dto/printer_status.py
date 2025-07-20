"""
DTO for printer status messages received from the device/printers topic.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class PrinterItemDTO:
    """
    DTO for an individual printer status item.
    Example: { "printerId": "printer-1", "status": "work", "timestamp": "2025-07-09T10:00:00Z" }
    """
    VALID_STATUSES = ["work", "finish"]

    def __init__(self, printer_id: str, status: str, timestamp: str):
        self.printer_id = printer_id
        self.status = status
        self.timestamp = timestamp

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['PrinterItemDTO']:
        """
        Create a PrinterItemDTO from a dictionary.
        Returns None if validation fails.
        """
        if not cls.validate(data):
            return None

        return cls(
            printer_id=data["printerId"],
            status=data["status"],
            timestamp=data["timestamp"]
        )

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> bool:
        """
        Validate that the printer item data has the correct format.
        """
        if not isinstance(data, dict):
            return False

        # Check required fields
        if not all(key in data for key in ["printerId", "status", "timestamp"]):
            return False

        # Validate printer ID
        if not isinstance(data["printerId"], str) or not data["printerId"].strip():
            return False

        # Validate status
        if data["status"] not in cls.VALID_STATUSES:
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
        return {
            "printerId": self.printer_id,
            "status": self.status,
            "timestamp": self.timestamp
        }


class PrinterStatusDTO:
    """
    DTO for the complete printer status message.
    Example: {"printers": [{"printerId": "printer-1", "status": "work", "timestamp": "2025-07-09T10:00:00Z"}, ...]}
    """
    def __init__(self, printers: List[PrinterItemDTO]):
        self.printers = printers

    @classmethod
    def from_json(cls, json_str: str) -> Optional['PrinterStatusDTO']:
        """
        Create a PrinterStatusDTO from a JSON string.
        Returns None if validation or parsing fails.
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError:
            return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['PrinterStatusDTO']:
        """
        Create a PrinterStatusDTO from a dictionary.
        Returns None if validation fails.
        """
        if not cls.validate(data):
            return None

        printers = []
        for printer_item in data["printers"]:
            printer_dto = PrinterItemDTO.from_dict(printer_item)
            if printer_dto:
                printers.append(printer_dto)

        return cls(printers=printers)

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> bool:
        """
        Validate that the printer status data has the correct format.
        """
        if not isinstance(data, dict):
            return False

        # Check required fields
        if "printers" not in data:
            return False

        # Validate printers list
        if not isinstance(data["printers"], list) or not data["printers"]:
            return False

        # Validate each printer item
        for printer_item in data["printers"]:
            if not PrinterItemDTO.validate(printer_item):
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert DTO to dictionary.
        """
        return {
            "printers": [printer.to_dict() for printer in self.printers]
        }

    def to_json(self) -> str:
        """
        Convert DTO to JSON string.
        """
        return json.dumps(self.to_dict())

    def get_finished_printers(self) -> List[PrinterItemDTO]:
        """
        Get a list of printers with 'finish' status.
        """
        return [printer for printer in self.printers if printer.status == "finish"]
