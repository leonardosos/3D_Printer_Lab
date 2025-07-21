from dataclasses import dataclass

@dataclass
class PrinterProgress:
    printerId: str
    jobId: str
    status: str
    progress: int
    timestamp: str  # or datetime