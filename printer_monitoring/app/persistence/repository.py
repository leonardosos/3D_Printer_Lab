from app.dto.printer_progress_dto import PrinterProgressDTO
from app.dto.job_dto import JobDTO
from typing import List, Optional, Tuple

class PrinterMonitoringRepository:
    def __init__(self):
        self._printers: List[PrinterProgressDTO] = []
        self._jobs: List[JobDTO] = []
        self._printer_history: List[PrinterProgressDTO] = []
        self._job_history: List[JobDTO] = []

    # Printer methods
    def add_or_update_printer(self, printer: PrinterProgressDTO):
        # If a new jobId is assigned to a printer, archive the old one
        for idx, p in enumerate(self._printers):
            if p.printerId == printer.printerId and p.jobId != printer.jobId:
                self._printer_history.append(self._printers[idx])
                self._printers.pop(idx)
                break
            if p.printerId == printer.printerId and p.jobId == printer.jobId:
                self._printers[idx] = printer
                return
        self._printers.append(printer)

    def get_printers(self) -> List[PrinterProgressDTO]:
        return self._printers

    def get_printer_by_job(self, job_id: str) -> Optional[PrinterProgressDTO]:
        for p in self._printers:
            if p.jobId == job_id:
                return p
        return None

    # Job methods
    def add_or_update_job(self, job: JobDTO):
        # Archive old job if a new jobId is assigned to the same printer
        for idx, j in enumerate(self._jobs):
            if j.jobId == job.jobId:
                self._jobs[idx] = job
                return
        self._jobs.append(job)

    def get_jobs(self) -> List[JobDTO]:
        return self._jobs

    def get_job(self, job_id: str) -> Optional[JobDTO]:
        for j in self._jobs:
            if j.jobId == job_id:
                return j
        return None

    # Cleanup methods
    def cleanup_completed_jobs(self):
        # Move completed printers/jobs (progress == 100) to history
        completed: List[Tuple[PrinterProgressDTO, JobDTO]] = []
        for p in self._printers[:]:
            if p.progress == 100:
                job = self.get_job(p.jobId)
                if job:
                    self._printer_history.append(p)
                    self._job_history.append(job)
                    self._printers.remove(p)
                    self._jobs.remove(job)

    def remove_printer_by_job(self, job_id: str):
        self._printers = [p for p in self._printers if p.jobId != job_id]

    def remove_job(self, job_id: str):
        self._jobs = [j for j in self._jobs if j.jobId != job_id]

    # History accessors
    def get_printer_history(self) -> List[PrinterProgressDTO]:
        return self._printer_history

    def get_job_history(self) -> List[JobDTO]:
        return self._job_history