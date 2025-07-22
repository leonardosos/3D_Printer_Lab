from typing import List, Dict
from app.dto.printer_progress_dto import PrinterProgressDTO
from app.dto.monitoring_dto import PrinterStatusDTO, APIResponseDTO
import threading
import csv

class StatusHistory:
    def __init__(self, printer_ids: List[str], debug: bool = False):
        self._lock = threading.RLock()
        self.status_readings: List[PrinterProgressDTO] = []
        self.printer_ids = printer_ids

    def add_status_reading(self, reading: PrinterProgressDTO):
        with self._lock:
            self.status_readings.append(reading)

    def get_latest_status_dict(self) -> Dict[str, PrinterProgressDTO]:
        """Get the latest status for each printer ID."""
        with self._lock:
            latest_status = {}
            for printer_id in self.printer_ids:
                filtered = [r for r in self.status_readings if r.printerId == printer_id]
                if filtered:
                    latest = max(filtered, key=lambda r: r.timestamp)
                    latest_status[printer_id] = latest
            return latest_status

    def get_latest_status_list(self) -> APIResponseDTO:
        """Get the latest status for all printers as an APIResponseDTO."""
        with self._lock:
            latest_status = self.get_latest_status_dict().values()
            printers = [
                PrinterStatusDTO(
                    printerId=r.printerId,
                    status=r.status,
                    currentJobId=r.jobId,
                    modelUrl=getattr(r, "modelUrl", ""),  # Use empty string if not present
                    progress=r.progress,
                    lastUpdated=str(r.timestamp)
                )
                for r in latest_status
            ]
            return APIResponseDTO(printers=printers)

    def clear(self):
        with self._lock:
            self.status_readings.clear()

    def csv_dump(self, file_path: str):
        """Dump the status history to a CSV file."""
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="a", newline="") as csvfile:
            fieldnames = ["timestamp", "status", "progress", "printerId", "jobId"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if os.path.getsize(file_path) == 0:
                writer.writeheader()
            for reading in self.status_readings:
                writer.writerow({
                    "timestamp": reading.timestamp,
                    "status": reading.status,
                    "progress": reading.progress,
                    "printerId": reading.printerId,
                    "jobId": reading.jobId
                })