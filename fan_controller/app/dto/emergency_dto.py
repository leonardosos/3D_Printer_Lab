from dataclasses import dataclass

@dataclass
class EmergencyDTO:
    action: str
    type: str
    source: str
    id: str
    timestamp: str