import time
import threading
import logging
import requests
from dataclasses import asdict
import numpy as np
from typing import Optional
from app.persistence.repository import JobHandlerRepository
from app.dto.job_dto import Job
from app.dto.assignment_dto import Assignment
from app.dto.printer_progress_dto import PrinterProgress
from app.dto.robot_progress_dto import RobotProgress
from app.dto.printer_list_dto import PrintersList, PrinterStatus
from app.mqtt.publisher import MQTTPublisher
from app.mqtt.subscriber import MQTTSubscriber

class JobHandler:
    def __init__(self, broker_host: str, broker_port: int, queue_manager_url: str):
        self.repo = JobHandlerRepository()
        self.publisher = MQTTPublisher(broker_host, broker_port)
        self.subscriber = MQTTSubscriber(
            broker_host, broker_port,
            self.on_printer_progress,
            self.on_robot_progress
        )
        self.queue_manager_url = queue_manager_url
        self.discovery_time = 30  # seconds

    def start(self):
        logging.info("Starting JobHandler...")
        self.subscriber.connect()
        self.discovery_phase()
        self.main_loop()

    def discovery_phase(self):
        logging.info(f"Discovery phase started for {self.discovery_time} seconds.")
        start_time = time.time()
        while time.time() - start_time < self.discovery_time:
            # The on_printer_progress callback will populate available printers
            time.sleep(1)
        logging.info(f"Discovery phase ended. Available printers: {self.repo.get_available_printers()}")

    def main_loop(self):
        logging.info("Entering main job assignment loop.")
        while True:
            available_printers = self.repo.get_available_printers()
            if not available_printers:
                time.sleep(2)
                continue
            for printer_id in available_printers:
                job = self.request_job()
                if job:
                    self.assign_job_to_printer(printer_id, job)
                else:
                    break  # No more jobs available
            time.sleep(2)

    def request_job(self) -> Optional[Job]:
        try:
            resp = requests.get(f"{self.queue_manager_url}/prioritary_job")
            if resp.status_code == 200:
                job_data = resp.json()
                job = Job(**job_data)
                logging.info(f"Received job from queue manager: {job}")
                return job
            else:
                logging.info("No jobs available from queue manager.")
                return None
        except Exception as e:
            logging.error(f"Error requesting job: {e}")
            return None

    def assign_job_to_printer(self, printer_id: str, job: Job):
        # Build assignment DTO (fill with real data as needed)
        assignment = Assignment(
            jobId=job.id,
            modelUrl=f"models/{job.modelId}.gcode",
            filamentType="PLA",  # Example, adjust as needed
            estimatedTime=np.random.randint(3300, 3900),
            priority=job.priority,
            assignedAt=job.submittedAt.isoformat(),
            parameters={"layerHeight": 0.2, "infill": 20, "nozzleTemp": 210, "bedTemp": 60}
        )
        self.publisher.publish_assignment(printer_id, assignment)
        self.repo.mark_printer_busy(printer_id, job)
        logging.info(f"Assigned job {job.id} to printer {printer_id}")

    def on_printer_progress(self, progress: PrinterProgress):
        if progress.status == "idle" and progress.progress == 100:
            # Job completed, notify robot manager
            self.repo.mark_printer_awaiting_cleaning(progress.printerId)
            printers_list = PrintersList(
                printers=[PrinterStatus(printerId=progress.printerId, status="idle", timestamp=progress.timestamp)]
            )
            self.publisher.publish_printers_list(printers_list)
            logging.info(f"Printer {progress.printerId} completed job, published to robot manager.")
        elif progress.status == "idle":
            # Printer is idle and not assigned, add to available
            self.repo.add_available_printer(progress.printerId)
        elif progress.status == "printing":
            # Printer is busy, ensure it's not in available
            self.repo.busy_printers.add(progress.printerId)
            self.repo.available_printers.discard(progress.printerId)

    def on_robot_progress(self, progress: RobotProgress):
        if progress.status == "completed":
            # Cleaning done, mark printer as available
            self.repo.mark_printer_available(progress.printerId)
            logging.info(f"Printer {progress.printerId} cleaned and available.")

    def stop(self):
        self.subscriber.disconnect()
        self.publisher.disconnect()
        logging.info("JobHandler stopped.")