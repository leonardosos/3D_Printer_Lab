# mqtt_client
from app.mqtt.client import MQTTClient
from app.mqtt.subscriber import MQTTSubscriber
from app.mqtt.publisher import MQTTPublisher

# persistence
from app.models.temperature_analyzer import TemperatureAnalyzer
from app.persistence.temperature_history import TemperatureHistory
from app.persistence.alert_history import AlertHistory

# internal data models
from app.classes.emergency_model import EmergencyAlert

# DTOs
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO
from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
from app.dto.emergency_command_dto import EmergencyCommandDTO

# services
from app.services.discover_printers import discover_printers

# standard libraries
import yaml
import os
import threading
import time
from typing import List

da sistemare quando arriva il messaggio, e gia DTO, 
sistemare prev and next
fare alert gestion
fare alert store

class AnomalyDetectionService:
    def __init__(self, mqtt_client, debug=True, discover_printers_timeout=60):
        
        # Initialize self attributes
        self.debug = debug
        self.discover_printers_timeout = discover_printers_timeout

        # Initialize MQTT client
        self.mqtt_client = mqtt_client
        self.mqtt_client.connect()
        # Start MQTT client loop on separate thread
        self.mqtt_client.loop_start()
        # Initialize MQTT communication with provided client
        self.subscriber = MQTTSubscriber(self.mqtt_client)
        self.publisher = MQTTPublisher(self.mqtt_client)

        if self.debug:
            print("[ANOMALY_DETECTION DEBUG] Initialized MQTT client and pub/sub")

        # Search all printers in the network -> blocking call
        # Any payload with printerId will be added to the discovered printers
        self.printers = discover_printers(self.subscriber, timeout=self.discover_printers_timeout, debug=self.debug)

        # Initialize temperature history and analyzer
        self.history = TemperatureHistory(self.printers, debug=self.debug)
        # Initialize alert history for emergency alerts
        self.alert_history = AlertHistory(debug=self.debug)

        # Initialize temperature analyzer for heat level computation
        self.analyzer = TemperatureAnalyzer(debug=self.debug)


        # Alert list
        self.alerts = list()


        # Initialize printer temperature dicts with: key printerID and DTOs as values (None initially)
        self.current_printer_temperatures = {
            pid: None for pid in self.printers
        }
        self.prev_printer_temperatures = {
            pid: None for pid in self.printers
        }

        # Initialize room temperature: DTOs as values (None initially)
        self.current_room_temperature = None
        self.prev_room_temperature = None


    def start(self):

        if self.debug:
            print(f"[GLOBAL_TEMP DEBUG] Starting GlobalTemperatureService with {len(self.printers)} discovered printers.")
        
        # Subscribe to room and printer temperature topics
        self.subscriber.subscribe_room_temperature(self._on_room_temp)
        self.subscriber.subscribe_printer_temperature(self._on_printer_temp)

        if self.debug:
            print("[GLOBAL_TEMP DEBUG] Subscribed to room and printer temperature topics.")


    # Custom callbacks for MQTT messages, for store temperature readings
    def _on_room_temp(self, client, userdata, dto):

        # Update previous and current room temperature DTOs
        self.prev_room_temperature = self.current_room_temperature
        self.current_room_temperature = dto

        self.history.add_room_reading(dto)

    def _on_printer_temp(self, client, userdata, dto):
        # dto should be a TemperatureReadingPrinterDTO
        printer_id = dto.printerId

        dto = self.parse_dto(dto, TemperatureReadingPrinterDTO)
        self.current_printer_temperatures[printer_id] = dto

        # Analyze the temperature reading for anomalies
        alert_threshold = self.analyzer.check_thresholds(self.current_printer_temperatures[printer_id])
        alert_rate = self.analyzer.check_rate(self.prev_printer_temperatures[printer_id], self.current_printer_temperatures[printer_id])

        # Update previous and current temperature DTOs for this printer
        if printer_id in self.current_printer_temperatures:
            self.prev_printer_temperatures[printer_id] = self.current_printer_temperatures[printer_id]
        else:
            raise ValueError(f"Unknown printer ID added to temperature readings: {printer_id}")

        self.history.add_printer_reading(dto)

    def parse_dto(self, dto, dto_class) -> TemperatureReadingPrinterDTO | TemperatureReadingRoomDTO:
        if dto_class == TemperatureReadingPrinterDTO:
            return TemperatureReadingPrinterDTO(**dto)
        elif dto_class == TemperatureReadingRoomDTO:
            return TemperatureReadingRoomDTO(**dto)
        else:
            raise ValueError("Invalid DTO class specified.")

    def periodic_csv_dump(self, file_path="app/persistence/save", interval=60):
        """Periodically dump the temperature history to a CSV file."""
        def run():
            while True:
                # CSVs dump
                self.history.csv_dump(os.path.join(file_path, "temperature_history.csv"))
                self.alert_history.csv_dump(os.path.join(file_path, "alert_history.csv"))
                
                # Sleep for the specified interval before the next dump
                time.sleep(interval)
        
        # Start the periodic CSV dump in a separate thread
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        if self.debug:
            print(f"[GLOBAL_TEMP DEBUG] Periodic CSV dump started with interval {interval} seconds.")


if __name__ == "__main__":
    # Example usage for testing
    #
    # From global_temperature directory:
    #    #    cd IoT_Project/global_temperature
    #    #    python3 -m app.models.global_temperature_service
    #
    
    
    from app.mqtt.client import MQTTClient

    client = MQTTClient()

    service = AnomalyDetectionService(mqtt_client=client, debug=True, discover_printers_timeout=60)
    service.start()

    # Keep the service running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Service stopped by user.")
        service.mqtt_client.loop_stop()