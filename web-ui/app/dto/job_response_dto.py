from dataclasses import dataclass, asdict
from typing import Optional, List
import json

@dataclass
class JobDTO:
    id: str
    modelId: str
    assignedPrinterId: Optional[str] = None
    priority: int = 0
    status: str = "pending"
    submittedAt: str = ""
    updatedAt: str = ""

@dataclass
class JobsResponseDTO:
    jobs: List[JobDTO]

    def to_json(self):
        return json.dumps({
            "jobs": [asdict(j) for j in self.jobs]
        })

@dataclass
class JobResponseDTO:
    job: JobDTO

    def to_json(self):
        return json.dumps({"job": asdict(self.job)})