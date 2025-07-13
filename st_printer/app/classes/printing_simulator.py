import time
import threading
import requests

from app.dto.printer_progress_dto import PrinterProgressDTO
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO

class PrintingSimulator:
    def __init__(self, printer, print_job, publisher, on_job_finished, debug=False):
        self.printer = printer              # Printer object being simulated
        self.print_job = print_job          # PrintJob object for the current job
        self.publisher = publisher          # MQTTPublisher for sending updates
        self.running = False                # Flag to control simulation loop
        self.on_job_finished = on_job_finished  # Callback for when job is finished
        self.debug = debug                  # Debug flag

    def simulate_print(self):
        if self.debug:
            print(f"[SIMULATOR DEBUG] Starting print simulation for job {self.print_job.job_id} on printer {self.printer.printer_id}")
        
        # Start the printing simulation and set running flag
        self.running = True
        self.printer.update_status("printing")
        self.print_job.update_status("printing")
        total_time = self.print_job.estimated_time
        target_temp = self.print_job.nozzle_temp

        # Publish print progress - initial progress at 0%, Status is "printing"
        self.print_job.update_progress(0)
        progress_dto = PrinterProgressDTO(
            printerId=self.printer.printer_id,
            jobId=self.print_job.job_id,
            status=self.print_job.status,
            progress=0,
            timestamp=str(time.time())
        )
        self.publisher.mqtt_client.publish(
            f"device/printer/{self.printer.printer_id}/progress",
            progress_dto.to_json()
        )     

        # Simulate GCODE download (model file handling)
        gcode_url = self.print_job.model_url
        if self.debug:
            print(f"[SIMULATOR DEBUG] Simulating GCODE download from {gcode_url}")

        ######### HEATING SIMULATION #########
        # Ramp up nozzle temperature to target
        for t in range(int(self.printer.current_temp), int(target_temp), int(self.printer.temp_rate)):
            # Set printer temperature each step
            self.printer.set_temperature(t)

            # Debug print for temperature ramping 
            if self.debug and t % 50 == 0:
                print(f"[SIMULATOR DEBUG] Nozzle temperature ramping up: {t}C")

            # Publish temperature reading
            temp_dto = TemperatureReadingPrinterDTO(
                printerId=self.printer.printer_id,
                temperature=t,
                unit="C",
                timestamp=str(time.time())
            )
            self.publisher.mqtt_client.publish(
                f"device/printer/{self.printer.printer_id}/temperature",
                temp_dto.to_json()
            )
            time.sleep(0.5)

        # Finalize temperature setting before printing
        self.printer.set_temperature(target_temp)
        if self.debug:
            print(f"[SIMULATOR DEBUG] Nozzle reached target temperature: {target_temp}C")
            print("[SIMULATOR DEBUG] Starting printing process...")

        ######### PRINTING SIMULATION #########
        # Simulate printing process with temperature fluctuation and progress
        for i in range(1, 101):
            
            # Update print job progress each iteration
            self.print_job.update_progress(i)

            # Debug print for progress 
            if self.debug and i % 20 == 0:
                print(f"[SIMULATOR DEBUG] Print progress: {i}%")

            # Simulate temperature fluctuation
            fluctuation = target_temp + (2 * ((i % 10) - 5))
            self.printer.set_temperature(fluctuation)

            # Publish temperature reading
            temp_dto = TemperatureReadingPrinterDTO(
                printerId=self.printer.printer_id,
                temperature=fluctuation,
                unit="C",
                timestamp=str(time.time())
            )
            self.publisher.mqtt_client.publish(
                f"device/printer/{self.printer.printer_id}/temperature",
                temp_dto.to_json()
            )

            # Publish print progress
            progress_dto = PrinterProgressDTO(
                printerId=self.printer.printer_id,
                jobId=self.print_job.job_id,
                status=self.print_job.status,
                progress=i,
                timestamp=str(time.time())
            )
            self.publisher.mqtt_client.publish(
                f"device/printer/{self.printer.printer_id}/progress",
                progress_dto.to_json()
            )

            # Simulate time taken for each percentage of print
            time.sleep(total_time / 100)

        ######### COOLING SIMULATION #########
        # Cool down nozzle after printing
        for t in range(int(target_temp), 25, -int(self.printer.temp_rate)):
            
            # Set printer temperature each step
            self.printer.set_temperature(t)

            if self.debug and t % 50 == 0:
                print(f"[SIMULATOR DEBUG] Nozzle cooling down: {t}C")

            # Publish temperature reading
            temp_dto = TemperatureReadingPrinterDTO(
                printerId=self.printer.printer_id,
                temperature=t,
                unit="C",
                timestamp=str(time.time())
            )
            self.publisher.mqtt_client.publish(
                f"device/printer/{self.printer.printer_id}/temperature",
                temp_dto.to_json()
            )

            time.sleep(0.5)
        
        # Publish print progress - final progress at 100%, Status is "printing"
        self.print_job.update_progress(100)
        progress_dto = PrinterProgressDTO(
            printerId=self.printer.printer_id,
            jobId=self.print_job.job_id,
            status=self.print_job.status,
            progress=100,
            timestamp=str(time.time())
        )
        self.publisher.mqtt_client.publish(
            f"device/printer/{self.printer.printer_id}/progress",
            progress_dto.to_json()
        )        

        # Finalize cooling down
        self.printer.set_temperature(25)
        if self.debug:
            print("[SIMULATOR DEBUG] Nozzle cooled down to 25C")
        
        # Update printer and job status to completed
        self.printer.update_status("completed")
        self.print_job.update_status("completed")

        # Publish final status update
        progress_dto = PrinterProgressDTO(
            printerId=self.printer.printer_id,
            jobId=self.print_job.job_id,
            status="completed",
            progress=100,
            timestamp=str(time.time())
        )
        self.publisher.mqtt_client.publish(
            f"device/printer/{self.printer.printer_id}/progress",
            progress_dto.to_json()
        )

        if self.debug:
            print("[SIMULATOR DEBUG] Print job completed")
        
        # Call the job finished callback
        self.on_job_finished()
        self.running = False

    def start(self):
        # Start the print simulation in a separate thread
        threading.Thread(target=self.simulate_print).start()

    def stop(self):
        # Stop the print simulation
        self.running = False

