# 2.2.3) PrinterAssignment

from dataclasses import dataclass, asdict
import json

@dataclass
class AssignmentParameters:
    layerHeight: float
    infill: float
    nozzleTemp: float

@dataclass
class PrinterAssignmentDTO:
    jobId: str
    modelUrl: str
    filamentType: str
    estimatedTime: int
    priority: int
    assignedAt: str
    parameters: AssignmentParameters

    def to_json(self) -> str:
        # Serialize nested dataclass
        data = asdict(self)
        data['parameters'] = asdict(self.parameters)  # Serialize parameters
        return json.dumps(data)