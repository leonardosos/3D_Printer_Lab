from dataclasses import dataclass

@dataclass
class StatusDTO:
    heatLevel: int
    timestamp: str
