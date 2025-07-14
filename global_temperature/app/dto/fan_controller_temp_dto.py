# 2.4.1) FanControllerTemp

from dataclasses import dataclass, asdict
import json

@dataclass
class FanControllerTempDTO:
    heatLevel: int  # interpreted temperature level for fan controller
    timestamp: str

    def to_json(self) -> str:
        return json.dumps(asdict(self))
