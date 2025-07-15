import yaml
import json
from app.models.printer import Printer
from app.models.print_job import PrintJob
from app.models.printer_assignment import PrinterAssignment
from app.mqtt.client import MQTTClient
from app.mqtt.publisher import MQTTPublisher
from app.mqtt.subscriber import MQTTSubscriber
from app.classes.printing_simulator import PrintingSimulator
from app.dto.printer_assignment_dto import PrinterAssignmentDTO, AssignmentParameters
from app.dto.printer_progress_dto import PrinterProgressDTO
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO
import os
import yaml
import threading
import time


class PrintingService:
    def __init__(self, config_path, mqtt_config_path, debug=True):
        
        # Initialize the printer service 
        
        # load id form environment variable or use default
        printer_id = os.getenv("PRINTER_ID", "printer_001")

        if debug:
            print(f"[SERVICE DEBUG] Initializing PrintingService for printer ID: {printer_id}")

        # Load printer configuration from YAML file
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            if debug:
                print(f"[SERVICE DEBUG] Loaded printer configuration: {config_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        # Create Printer instance with loaded configuration
        self.printer = Printer(printer_id=printer_id, **config)

        # Initialize MQTT client and publisher/subscriber
        self.mqtt_client = MQTTClient(mqtt_config_path, debug=debug)
        self.publisher = MQTTPublisher(self.mqtt_client)
        self.subscriber = MQTTSubscriber(self.mqtt_client)

        # Initialize printing simulator
        self.simulator = None                          

        # Job handling
        self.current_job = None     # Currently active print job
        self.next_job = None        # Next job to be processed 
        self.last_job_id = None     # Last job ID processed

        # Debug flag to enable/disable debug prints
        self.debug = debug  # Enable debug prints if True

        # Start idle status thread to publish idle status periodically
        self._idle_thread_running = False  # Change to False initially
        self.idle_status_thread = None     # Initialize as None
        self._idle_timer = 30  # seconds

    def on_assignment(self, client, userdata, assignment_dto):
        # Callback for when a print job assignment is received via MQTT
        if self.debug:
            print(f"\n[SERVICE DEBUG] Received assignment for job: {assignment_dto.jobId}")

        # Ignore job if it was already processed
        if assignment_dto.jobId == self.last_job_id:
            if self.debug:
                print(f"[SERVICE DEBUG] [next = last] Job {assignment_dto.jobId} was already processed. Ignoring assignment.\n")
            return

        # Deserialize the assignment DTO
        job = PrintJob(
            job_id=assignment_dto.jobId,
            model_url=assignment_dto.modelUrl,
            filament_type=assignment_dto.filamentType,
            estimated_time=assignment_dto.estimatedTime,
            priority=assignment_dto.priority,
            assigned_at=assignment_dto.assignedAt,
            layer_height=assignment_dto.parameters.layerHeight,
            infill=assignment_dto.parameters.infill,
            nozzle_temp=assignment_dto.parameters.nozzleTemp
        )

        # Only set as next job if not already set and not already processed
        if self.next_job is None or self.next_job.job_id != job.job_id:
            self.next_job = job
            if self.debug:
                print(f"[SERVICE DEBUG] Next job set: {self.next_job.job_id}\n")
        else:
            if self.debug:
                print(f"[SERVICE DEBUG] [next = current] Job {job.job_id} is already set as next job, ignoring assignment.\n")

        # Try to start the next job immediately if possible
        self.try_start_next_job()

    def _publish_idle_status_periodically(self):
    # Publish idle status periodically 
        # This thread runs in the background to publish:
        # - idle status every 30 seconds
        # - temperature reading every 30 seconds
        #
        # It checks if the printer is idle and publishes the status accordingly
        # --> looking if exists a current job or not

        if self.debug:
            print(f"[SERVICE DEBUG] Idle status thread started for printer {self.printer.printer_id} every {self._idle_timer} seconds")

        while self._idle_thread_running:
            if self.current_job is None:
                self.publisher.publish_progress(self.printer.printer_id, status="idle", progress=100.0, job_id="")
                self.publisher.publish_temperature(self.printer.printer_id, 25.0)  # idle (ambient) temperature
            else:
                # Stop publishing idle status once a print starts
                break
            time.sleep(self._idle_timer)  # publish every 30 seconds

    def try_start_next_job(self):
        # Start next job if printer is idle
        if self.current_job is None and self.next_job is not None:
            # Stop the idle status thread when a print starts
            self._idle_thread_running = False
            
            # Variable turn cycle from next_job to current_job
            self.current_job = self.next_job
            self.next_job = None
            
            # Create a new PrintingSimulator instance for the current job
            self.simulator = PrintingSimulator(self.printer, self.current_job, self.publisher, self.on_job_finished, debug=self.debug)
            if self.debug:
                print(f"[SERVICE DEBUG] Starting job: {self.current_job.job_id} on printer {self.printer.printer_id}\n")
            # Start the printing simulator
            self.simulator.start()
        
    def on_job_finished(self):
        # Called when the current job is finished inside the simulator

        if self.debug:
            print(f"\n[SERVICE DEBUG] Job finished: {self.current_job.job_id} on printer {self.printer.printer_id}")

        # Save last job id to prevent repeats
        self.last_job_id = self.current_job.job_id

        # Clean up the simulator and reset current job
        self.current_job = None
        self.simulator = None

        # try to start the next job if available
        self.try_start_next_job()

        # Start idle status thread after MQTT connection
        self._idle_thread_running = True
        self.idle_status_thread = threading.Thread(target=self._publish_idle_status_periodically, daemon=True)
        self.idle_status_thread.start()

    def start(self):
        # Start the printer service and begin listening for assignments
        self.mqtt_client.connect()
        self.subscriber.subscribe_assignment(self.printer.printer_id, self.on_assignment)
        self.mqtt_client.loop_start()
        if self.debug:
            print(f"[SERVICE DEBUG] Printer [{self.printer.printer_id}] service started and waiting for assignments...")
        
        # Start idle status thread after MQTT connection
        self._idle_thread_running = True
        self.idle_status_thread = threading.Thread(target=self._publish_idle_status_periodically, daemon=True)
        self.idle_status_thread.start()


if __name__ == "__main__":
    # Example usage for testing
    #
    #from st_printer directory:
    #
    #    cd /home/leonardo/iot/IoT_Project/st_printer
    #    python -m app.classes.printing_service
    #
    CONFIG_PATH = "app/printer_config.yaml"
    MQTT_CONFIG_PATH = "app/printer_mqtt_config.yaml"
    service = PrintingService(CONFIG_PATH, MQTT_CONFIG_PATH, debug=True)
    service.start()
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting subscriber...")


