from http import client
from app.persistence.temperature_history import TemperatureHistory
from app.models.temperature_analyzer import TemperatureAnalyzer
from app.mqtt.subscriber import MQTTSubscriber
from app.mqtt.publisher import MQTTPublisher
from app.dto.fan_controller_temp_dto import FanControllerTempDTO
from app.dto.global_temperature_response_dto import GlobalTemperatureResponseDTO, TemperatureReadingDTO
from app.services.discover_printers import discover_printers
import threading
import time

class GlobalTemperatureService:
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
        self.publisher = MQTTPublisher(self.mqtt_client)

        if self.debug:
            print("[GLOBAL_TEMP DEBUG] Initialized MQTT client and pub/sub")

        # Search all printers in the network -> blocking call
        # Any payload with printerId will be added to the discovered printers
        self.printers = discover_printers(self.subscriber, timeout=self.discover_printers_timeout, debug=self.debug)

        # Initialize temperature history and analyzer
        self.history = TemperatureHistory(self.printers, debug=self.debug)

        # Initialize temperature analyzer for heat level computation
        self.analyzer = TemperatureAnalyzer(debug=self.debug)


    def start(self):

        if self.debug:
            print(f"[GLOBAL_TEMP DEBUG] Starting GlobalTemperatureService with {len(self.printers)} discovered printers.")
        
        # Subscribe to room and printer temperature topics
        self.subscriber.subscribe_room_temperature(self._on_room_temp)
        self.subscriber.subscribe_printer_temperature(self._on_printer_temp)

        if self.debug:
            print("[GLOBAL_TEMP DEBUG] Subscribed to room and printer temperature topics.")

        # Start periodic fan update
        self.start_periodic_fan_update()

        if self.debug:
            print("[GLOBAL_TEMP DEBUG] Periodic fan update started.")

        # Start periodic CSV dump
        self.periodic_csv_dump()

        print(f"[GLOBAL_TEMP] GlobalTemperatureService started successfully. (with {len(self.printers)} printers discovered.)")

    # Custom callbacks for MQTT messages, for store temperature readings
    def _on_room_temp(self, client, userdata, dto):
        self.history.add_room_reading(dto)

    def _on_printer_temp(self, client, userdata, dto):
        self.history.add_printer_reading(dto)

    # Method to compute and publish fan heat level one time -> need to be called periodically
    def fan_update(self):
        # Get the latest temperature
        room_temp = self.history.get_latest_room()
        printers_temp = self.history.get_latest_printers_list()  # <-- FIXED

        if self.debug:
            print(f"[GLOBAL_TEMP DEBUG] Room temp: {room_temp.temperature if room_temp else 'No data'}")
            print(f"[GLOBAL_TEMP DEBUG] Latest printer temps: {printers_temp}")

        # Compute heat level and publish to fan controller
        heat_level = self.analyzer.compute_heat_level(
            room_readings=room_temp,
            printer_readings=printers_temp
        )
        if self.debug:
            print(f"[GLOBAL_TEMP DEBUG] Computed heat level: {heat_level}")

        self.publisher.publish_fan_heat_level(heat_level)

    def start_periodic_fan_update(self):
        """Periodically update the fan based on temperature readings."""
        def run():
            while True:
                self.fan_update()
                time.sleep(30)
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    # get all temperature readings for API response
    def get_temperature_api_response(self):
        room_temp = self.history.get_latest_room()
        printers_temp = self.history.get_latest_printers_list()

        if self.debug:
            print(f"[GLOBAL_TEMP DEBUG] Room temp for API: {room_temp}")
            print(f"[GLOBAL_TEMP DEBUG] Latest printer temps for API: {printers_temp}")

        temperatures = []
        last_updated = None

        # Add room temperature if available
        if room_temp:
            temperatures.append(
                TemperatureReadingDTO(
                    temperature=room_temp.temperature,
                    source="room",
                    sourceId=getattr(room_temp, "sourceId", "room"),
                    timestamp=room_temp.timestamp
                )
            )
            last_updated = room_temp.timestamp

        # Add printer temperatures if available
        for pt in printers_temp or []:
            temperatures.append(
                TemperatureReadingDTO(
                    temperature=pt.temperature,
                    source="printer",
                    sourceId=getattr(pt, "sourceId", "printer"),
                    timestamp=pt.timestamp
                )
            )
            # Update last_updated if printer timestamp is newer
            if not last_updated or pt.timestamp > last_updated:
                last_updated = pt.timestamp

        return GlobalTemperatureResponseDTO(
            temperatures=temperatures,
            lastUpdated=last_updated if last_updated else ""
        )

    def periodic_csv_dump(self, file_path="app/persistence/save/temperature_history.csv", interval=60):
        """Periodically dump the temperature history to a CSV file."""
        def run():
            while True:
                self.history.csv_dump(file_path)
                time.sleep(interval)
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

    service = GlobalTemperatureService(mqtt_client=client, debug=True, discover_printers_timeout=60)
    service.start()

    # Keep the service running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Service stopped by user.")
        service.mqtt_client.loop_stop()