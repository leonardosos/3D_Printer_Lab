# No request body for GET /temperature/global, but you may want a placeholder for future query params.
from dataclasses import dataclass, asdict
import json

@dataclass
class TemperatureReadingRequestDTO:
    # Example: could add filters here in future
    def to_json(self):
        return json.dumps(asdict(self))