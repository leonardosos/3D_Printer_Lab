from dataclasses import dataclass
from typing import List

@dataclass
class PrinterStatusDTO:
    printerId: str
    status: str
    currentJobId: str
    modelUrl: str
    progress: int
    temperature: float
    lastUpdated: str

@dataclass
class MonitoringDTO:
    printers: List[PrinterStatusDTO]