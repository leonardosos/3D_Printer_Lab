from http import client
from app.persistence.status_history import StatusHistory
from app.mqtt.subscriber import MQTTSubscriber
from app.services.discover_printers import discover_printers
import threading
import time

class PrinterMonitoringService:
    def __init__(self, mqtt_client, debug=True, discover_printers_timeout=60):

        self.debug = debug
        self.discover_printers_timeout = discover_printers_timeout

        # Initialize MQTT client
        self.mqtt_client = mqtt_client
        self.mqtt_client.connect()
        # Start MQTT client loop on separate thread
        self.mqtt_client.loop_start()
        # Initialize MQTT communication with provided client
        self.subscriber = MQTTSubscriber(self.mqtt_client)

        if self.debug:
            print("[PRINTER_MONITORING DEBUG] Initialized MQTT client and pub/sub")

        # Search all printers in the network -> blocking call
        # Any payload with printerId will be added to the discovered printers
        print(f"\033[91m[PRINTER_MONITORING DEBUG] Discovering printers with timeout {self.discover_printers_timeout} seconds...\033[0m")

        self.printers = discover_printers(self.subscriber, timeout=self.discover_printers_timeout, debug=self.debug)

        # Initialize status history
        self.history = StatusHistory(self.printers, debug=self.debug)



    def start(self):

        if self.debug:
            print(f"[PRINTER_MONITORING DEBUG] Starting PrinterMonitoringService with {len(self.printers)} discovered printers.")

        # Subscribe to room and printer temperature topics
        self.subscriber.subscribe_progress(self._on_progress)

        if self.debug:
            print("[PRINTER_MONITORING DEBUG] Subscribed to printer status topics.")

        # Start periodic CSV dump
        self.periodic_csv_dump()

        print(f"\033[92m[PRINTER_MONITORING] Service started successfully. ({len(self.printers)} printers discovered.)\033[0m")

    # Custom callbacks for MQTT messages, for store status readings
    def _on_progress(self, client, userdata, dto):
        self.history.add_status_reading(dto)


    # get all status readings for API response
    def get_status_api_response(self):
        printers_status = self.history.get_latest_status_list()

        if self.debug:
            print(f"[PRINTER_STATUS DEBUG] Latest printer statuses for API: {printers_status}")

        return printers_status


    def periodic_csv_dump(self, file_path="app/persistence/save/status_history.csv", interval=60):
        """Periodically dump the status history to a CSV file."""
        def run():
            while True:
                self.history.csv_dump(file_path)
                time.sleep(interval)
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        if self.debug:
            print(f"[PRINTER_MONITORING DEBUG] Periodic CSV dump started with interval {interval} seconds.")

