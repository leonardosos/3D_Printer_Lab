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

        # Classes
        # Initialize temperature history and analyzer
        self.history = TemperatureHistory(self.printers, debug=self.debug)
        # Initialize alert history for emergency alerts
        self.alert_history = AlertHistory(debug=self.debug)

        # Initialize temperature analyzer for heat level computation
        self.analyzer = TemperatureAnalyzer(debug=self.debug)


        # VARIABLES FOR KEEPING TRACK OF TEMPERATURES
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

        # Hysteresis counters for emergency resolution
        self.room_threshold_safe_count = 0
        self.room_rate_safe_count = 0
        self.printer_threshold_safe_count = {pid: 0 for pid in self.printers}
        self.printer_rate_safe_count = {pid: 0 for pid in self.printers}
        self.SAFE_REQUIRED = 3  # Number of consecutive safe readings required


    def start(self):

        if self.debug:
            print(f"[GLOBAL_TEMP DEBUG] Starting GlobalTemperatureService with {len(self.printers)} discovered printers.")
        
        # Subscribe to room and printer temperature topics
        self.subscriber.subscribe_room_temperature(self._on_room_temp)
        self.subscriber.subscribe_printer_temperature(self._on_printer_temp)

        if self.debug:
            print("[GLOBAL_TEMP DEBUG] Subscribed to room and printer temperature topics.")



    # Custom callbacks for MQTT messages, for store temperature readings
    def _publish_emergency_async(self, action, type_, source, id_):
        threading.Thread(
            target=self.publisher.publish_emergency_command,
            args=(action, type_, source, id_),
            daemon=True
        ).start()

    def _on_room_temp(self, client, userdata, dto_received):
        # Update previous and current room temperature DTOs
        self.prev_room_temperature = self.current_room_temperature
        self.current_room_temperature = dto_received

        # Analyze the room temperature reading for anomalies
        alert_threshold = self.analyzer.check_thresholds(self.current_room_temperature)

        # Only check rate if both previous and current readings are available
        if self.prev_room_temperature is not None and self.current_room_temperature is not None:
            alert_rate = self.analyzer.check_rate(self.prev_room_temperature, self.current_room_temperature)
        else:
            alert_rate = False

        # Add the room temperature reading to the history
        self.history.add_room_reading(dto_received)

        if alert_threshold:
            # Add alert to the alert history, only publish if new
            # Return True if the alert was added (not already present)
            added_threshold = self.alert_history.add_alert(
                EmergencyAlert(
                    alert_id=f"room_{dto_received.sensorId}_{dto_received.timestamp}_threshold",
                    alert_type="Threshold Alert",
                    source="room",
                    source_id=dto_received.sensorId,
                    timestamp=dto_received.timestamp,
                    details={
                        "description": f"Room temperature exceeded threshold: {dto_received.temperature} {dto_received.unit}"
                    }
                )
            )
            if added_threshold:
                self._publish_emergency_async(
                    action="emergency",
                    type_="overheat",
                    source="room",
                    id_=dto_received.sensorId
                )
        else:
            added_threshold = False

        self.reentrant_threshold_on_room_temp(alert_threshold, added_threshold)

        if alert_rate:
            # Add alert to the alert history, only publish if new
            # Return True if the alert was added (not already present)
            added_rate = self.alert_history.add_alert(
                EmergencyAlert(
                    alert_id=f"room_{dto_received.sensorId}_{dto_received.timestamp}_rate",
                    alert_type="Rate Alert",
                    source="room",
                    source_id=dto_received.sensorId,
                    timestamp=dto_received.timestamp,
                    details={
                        "description": f"Room temperature rate of change exceeded: {dto_received.temperature} {dto_received.unit}"
                    }
                )
            )
            if added_rate:
                self._publish_emergency_async(
                    action="emergency",
                    type_="thermal_runaway",
                    source="room",
                    id_=dto_received.sensorId
                )
        else:
            added_rate = False

        self.reentrant_rate_on_room_temp(alert_rate, added_rate)

    def _on_printer_temp(self, client, userdata, dto_received):
        printer_id = dto_received.printerId
        # Update previous and current printer temperature DTOs
        self.prev_printer_temperatures[printer_id] = self.current_printer_temperatures.get(printer_id)
        self.current_printer_temperatures[printer_id] = dto_received

        # Analyze the printer temperature reading for anomalies
        alert_threshold = self.analyzer.check_thresholds(reading=self.current_printer_temperatures[printer_id])

        # Only check rate if both previous and current readings are available
        if self.prev_printer_temperatures[printer_id] is not None and self.current_printer_temperatures[printer_id] is not None:
            alert_rate = self.analyzer.check_rate(
                reading_prev=self.prev_printer_temperatures[printer_id], 
                reading_curr=self.current_printer_temperatures[printer_id]
            )
        else:
            alert_rate = False

        # Add the printer temperature reading to the history
        self.history.add_printer_reading(dto_received)

        if alert_threshold:
            # Add alert to the alert history
            # Return True if the alert was added (not already present)
            added_threshold = self.alert_history.add_alert(
                EmergencyAlert(
                    alert_id=f"printer_{printer_id}_{dto_received.timestamp}_threshold",
                    alert_type="Threshold Alert",
                    source="printer",
                    source_id=printer_id,
                    timestamp=dto_received.timestamp,
                    details={
                        "description": f"Printer {printer_id} temperature exceeded threshold: {dto_received.temperature} {dto_received.unit}"
                    }
                )
            )
            if added_threshold:
                self._publish_emergency_async(
                    action="emergency",
                    type_="overheat",
                    source="printer",
                    id_=printer_id
                )
        else:
            added_threshold = False

        self.reentrant_threshold_on_printer_temp(printer_id, alert_threshold, added_threshold)

        if alert_rate:
            # Keep track of the alert
            # Return True if the alert was added (not already present)
            added_rate = self.alert_history.add_alert(
                EmergencyAlert(
                    alert_id=f"printer_{printer_id}_{dto_received.timestamp}_rate",
                    alert_type="Rate Alert",
                    source="printer",
                    source_id=printer_id,
                    timestamp=dto_received.timestamp,
                    details={
                        "description": f"Printer {printer_id} temperature rate of change exceeded: {dto_received.temperature} {dto_received.unit}"
                    }
                )
            )
            if added_rate:
                self._publish_emergency_async(
                    action="emergency",
                    type_="thermal_runaway",
                    source="printer",
                    id_=printer_id
                )
        else:
            added_rate = False

        self.reentrant_rate_on_printer_temp(printer_id, alert_rate, added_rate)



    def reentrant_threshold_on_room_temp(self, alert_threshold, added):
        """
        Reentrant function to resolve room threshold emergency if condition is cleared.
        Uses hysteresis to avoid pendulum effect.
        """
        if not alert_threshold:
            self.room_threshold_safe_count += 1
            if self.room_threshold_safe_count >= self.SAFE_REQUIRED:
                for alert in self.alert_history.get_unresolved_alerts():
                    if alert.source == "room" and alert.alert_type == "Threshold Alert":
                        self.alert_history.resolve_alert(alert.alert_id)
                        self._publish_emergency_async(
                            action="resolve",
                            type_="overheat",
                            source="room",
                            id_=alert.source_id
                        )
                        if self.debug:
                            print(f"[REENTRANT] Room threshold emergency resolved: {alert.alert_id}")
                self.room_threshold_safe_count = 0
        else:
            self.room_threshold_safe_count = 0

    def reentrant_rate_on_room_temp(self, alert_rate, added):
        """
        Reentrant function to resolve room rate emergency if condition is cleared.
        Uses hysteresis to avoid pendulum effect.
        """
        if not alert_rate:
            self.room_rate_safe_count += 1
            if self.room_rate_safe_count >= self.SAFE_REQUIRED:
                for alert in self.alert_history.get_unresolved_alerts():
                    if alert.source == "room" and alert.alert_type == "Rate Alert":
                        self.alert_history.resolve_alert(alert.alert_id)
                        self._publish_emergency_async(
                            action="resolve",
                            type_="thermal_runaway",
                            source="room",
                            id_=alert.source_id
                        )
                        if self.debug:
                            print(f"[REENTRANT] Room rate emergency resolved: {alert.alert_id}")
                self.room_rate_safe_count = 0
        else:
            self.room_rate_safe_count = 0

    def reentrant_threshold_on_printer_temp(self, printer_id, alert_threshold, added):
        """
        Reentrant function to resolve printer threshold emergency if condition is cleared.
        Uses hysteresis to avoid pendulum effect.
        """
        if not alert_threshold:
            self.printer_threshold_safe_count[printer_id] += 1
            if self.printer_threshold_safe_count[printer_id] >= self.SAFE_REQUIRED:
                for alert in self.alert_history.get_unresolved_alerts():
                    if alert.source == "printer" and alert.source_id == printer_id and alert.alert_type == "Threshold Alert":
                        self.alert_history.resolve_alert(alert.alert_id)
                        self._publish_emergency_async(
                            action="resolve",
                            type_="overheat",
                            source="printer",
                            id_=printer_id
                        )
                        if self.debug:
                            print(f"[REENTRANT] Printer {printer_id} threshold emergency resolved: {alert.alert_id}")
                self.printer_threshold_safe_count[printer_id] = 0
        else:
            self.printer_threshold_safe_count[printer_id] = 0

    def reentrant_rate_on_printer_temp(self, printer_id, alert_rate, added):
        """
        Reentrant function to resolve printer rate emergency if condition is cleared.
        Uses hysteresis to avoid pendulum effect.
        """
        if not alert_rate:
            self.printer_rate_safe_count[printer_id] += 1
            if self.printer_rate_safe_count[printer_id] >= self.SAFE_REQUIRED:
                for alert in self.alert_history.get_unresolved_alerts():
                    if alert.source == "printer" and alert.source_id == printer_id and alert.alert_type == "Rate Alert":
                        self.alert_history.resolve_alert(alert.alert_id)
                        self._publish_emergency_async(
                            action="resolve",
                            type_="thermal_runaway",
                            source="printer",
                            id_=printer_id
                        )
                        if self.debug:
                            print(f"[REENTRANT] Printer {printer_id} rate emergency resolved: {alert.alert_id}")
                self.printer_rate_safe_count[printer_id] = 0
        else:
            self.printer_rate_safe_count[printer_id] = 0



    def periodic_csv_dump(self, file_path="app/persistence/save", interval=120):
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
    # From anomaly_detection directory:
    #    #    cd IoT_Project/anomaly_detection
    #    #    python3 -m app.models.anomaly_detection_service
    #

    from app.mqtt.client import MQTTClient

    client = MQTTClient()
    service = AnomalyDetectionService(mqtt_client=client, debug=True, discover_printers_timeout=10)
    service.start()

    service.periodic_csv_dump(file_path="app/persistence/save")

    print("[ANOMALY_DETECTION] Service started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Service stopped by user.")
        service.mqtt_client.loop_stop()