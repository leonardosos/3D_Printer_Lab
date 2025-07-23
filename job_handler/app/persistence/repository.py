from typing import Dict, Optional, Set
from app.dto.job_dto import Job

class JobHandlerRepository:
    def __init__(self):
        # Set of printerIds that are available for assignment
        self.available_printers: Set[str] = set()
        # Set of printerIds that are currently busy (printing or awaiting cleaning)
        self.busy_printers: Set[str] = set()
        # Map of printerId to the current job assigned
        self.printer_jobs: Dict[str, Job] = {}
        # Set of printerIds that are awaiting cleaning
        self.awaiting_cleaning: Set[str] = set()

    def add_available_printer(self, printer_id: str):
        self.available_printers.add(printer_id)
        self.busy_printers.discard(printer_id)
        self.awaiting_cleaning.discard(printer_id)

    def mark_printer_busy(self, printer_id: str, job: Job):
        self.busy_printers.add(printer_id)
        self.available_printers.discard(printer_id)
        self.awaiting_cleaning.discard(printer_id)
        self.printer_jobs[printer_id] = job

    def mark_printer_awaiting_cleaning(self, printer_id: str):
        self.awaiting_cleaning.add(printer_id)
        self.busy_printers.add(printer_id)
        self.available_printers.discard(printer_id)

    def mark_printer_available(self, printer_id: str):
        self.add_available_printer(printer_id)
        if printer_id in self.printer_jobs:
            del self.printer_jobs[printer_id]

    def get_available_printers(self):
        return list(self.available_printers)

    def get_busy_printers(self):
        return list(self.busy_printers)

    def get_awaiting_cleaning_printers(self):
        return list(self.awaiting_cleaning)

    def get_job_for_printer(self, printer_id: str) -> Optional[Job]:
        return self.printer_jobs.get(printer_id)