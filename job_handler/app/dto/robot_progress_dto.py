from dataclasses import dataclass

@dataclass
class RobotProgress:
    robotId: str
    printerId: str
    action: str
    status: str
    timestamp: str  # or datetime