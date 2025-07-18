from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

@dataclass
class EmergencyAlert:
    alert_id: str                # Unique alert identifier
    source: str                  # "printer" | "room"
    source_id: str               # printerId or sensorId
    alert_type: str              # "overheat" | "thermal_runaway"
    timestamp: str               # ISO 8601 string
    resolved: bool = False       # True if alert has been resolved
    details: Optional[Any] = None  # Optional extra

    def mark_resolved(self):
        """Mark the alert as resolved."""
        self.resolved = True

    def is_active(self) -> bool:
        """Check if the alert is still active (not resolved)."""
        return not self.resolved

    def is_reentrant(self, other: "EmergencyAlert") -> bool:
        """
        Check if another alert is considered a reentrant (same source, source_id, and alert_type).
        """
        return (
            self.source == other.source and
            self.source_id == other.source_id and
            self.alert_type == other.alert_type and
            not self.resolved
        )

    def to_dict(self) -> dict:
        """Convert the alert to a dictionary."""
        return {
            "alert_id": self.alert_id,
            "source": self.source,
            "source_id": self.source_id,
            "alert_type": self.alert_type,
            "timestamp": self.timestamp,
            "resolved": self.resolved,
            "details": self.details,
        }