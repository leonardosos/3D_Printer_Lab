from dataclasses import dataclass

@dataclass
class JobDTO:
    jobId: str
    modelUrl: str
    filamentType: str
    estimatedTime: int
    priority: int
    assignedAt: float 
    parameters: dict