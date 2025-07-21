from app.persistence.repository import PrinterMonitoringRepository
from app.dto.monitoring_dto import MonitoringDTO, PrinterStatusDTO
from typing import List
import logging

class PrinterMonitoringService:
    def __init__(self, repository: PrinterMonitoringRepository):
        self.repository = repository

    def get_monitoring_dto(self) -> MonitoringDTO:
        printers = self.repository.get_printers()
        jobs = self.repository.get_jobs()
        status_list: List[PrinterStatusDTO] = []

        for printer in printers:
            job = self.repository.get_job(printer.jobId)
            if not job:
                logging.error(f"No job found for printer {printer.printerId} with jobId {printer.jobId}")
                continue  # Or raise an exception if this should never happen

            # Compose PrinterStatusDTO (add temperature and lastUpdated if available, else use defaults)
            status = PrinterStatusDTO(
                printerId=printer.printerId,
                status=printer.status,
                currentJobId=printer.jobId,
                modelUrl=job.modelUrl,  
                progress=printer.progress,
                temperature=getattr(printer, "temperature", 0.0),  # Default to 0.0 if not present
                lastUpdated=str(printer.timestamp)  # Convert float timestamp to string if needed
            )
            status_list.append(status)

        return MonitoringDTO(printers=status_list)

    def cleanup_completed(self):
        self.repository.cleanup_completed_jobs()

    def on_printer_progress(self, dto):
        self.repository.add_or_update_printer(dto)

    def on_job_assignement(self, dto):
        self.repository.add_or_update_job(dto)