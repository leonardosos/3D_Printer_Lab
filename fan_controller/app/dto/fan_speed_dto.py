from dataclasses import dataclass

@dataclass
class FanSpeedDTO:
    fanId: str
    speed: int
    actual: int
    timestamp: str