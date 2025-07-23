from dataclasses import dataclass
from typing import List

@dataclass
class PrinterStatus:
    printerId: str
    status: str
    timestamp: str  # or datetime

@dataclass
class PrintersList:
    printers: List[PrinterStatus]