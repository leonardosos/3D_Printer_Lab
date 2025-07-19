# DTO for 2.4.3) EmergencyCommand (device/fan/controller/emergency)

from dataclasses import dataclass, asdict
import json

@dataclass
class EmergencyCommandDTO:
    action: str            # "emergency" | "emergency_finished"
    type: str              # "overheat" | "thermal_runaway"
    source: str            # "printer" | "room"
    id: str                # printerId or sensorId
    timestamp: str         # ISO 8601

    def to_json(self) -> str:
        """Convert the EmergencyCommandDTO to a JSON string."""
        return json.dumps(asdict(self))
