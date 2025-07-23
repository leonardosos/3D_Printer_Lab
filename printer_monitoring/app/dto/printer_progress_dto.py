from dataclasses import dataclass

@dataclass
class PrinterProgressDTO:
    printerId: str
    jobId: str
    status: str
    progress: int
    timestamp: float
