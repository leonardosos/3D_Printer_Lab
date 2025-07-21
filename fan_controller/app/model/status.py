import logging
import threading
import datetime
from typing import Optional
from app.dto.status_dto import StatusDTO
from app.dto.emergency_dto import EmergencyDTO
from app.dto.fan_speed_dto import FanSpeedDTO
from app.persistence.repository import FanControllerRepository
from app.mqtt.publisher import MqttPublisher
from app.mqtt.subscriber import MqttSubscriber

class FanController:
    def __init__(self, fan_id: str, repository: FanControllerRepository, publisher: MqttPublisher):
        self.fan_id = fan_id
        self.repository = repository
        self.publisher = publisher
        self._thermal_runaway_timer = None

    def on_status_received(self, payload):
        """Handle incoming status messages."""
        try:
            status = StatusDTO(**payload)
            self.repository.update_status(status)
            logging.info(f"Status received: {status}")
            if not self.repository.get_latest_emergency():
                self.update_speed()
            else:
                logging.info("Emergency active, ignoring status update for speed control.")
        except Exception as e:
            logging.error(f"Failed to process status message: {e}")

    def on_emergency_received(self, payload):
        """Handle incoming emergency messages."""
        try:
            emergency = EmergencyDTO(**payload)
            logging.info(f"Emergency received: {emergency}")

            if emergency.type == "solved":
                self.repository.clear_emergency()
                logging.info("Emergency solved. Returning to normal operation.")
                self.update_speed()
                return

            self.repository.update_emergency(emergency)

            if emergency.type == "overheat":
                logging.info("Overheat emergency: setting fan to max speed until solved.")
                self.update_speed()
            elif emergency.type == "thermal_runaway":
                logging.info("Thermal runaway emergency: setting fan to max speed for 30 seconds.")
                self.update_speed()
                self._start_thermal_runaway_timer()
            else:
                logging.info("Other emergency type received. Updating state and recalculating speed.")
                self.update_speed()
        except Exception as e:
            logging.error(f"Failed to process emergency message: {e}")

    def update_speed(self):
        """Recalculate and publish the fan speed based on current state."""
        status = self.repository.get_latest_status()
        emergency = self.repository.get_latest_emergency()
        speed = self.calculate_speed(status, emergency)
        self.publish_speed(speed)
        logging.info(f"Fan speed updated to {speed} (status={status}, emergency={emergency})")

    def calculate_speed(self, status: Optional[StatusDTO], emergency: Optional[EmergencyDTO] = None) -> int:
        """Compute the fan speed based on status and emergency."""
        if emergency:
            if emergency.type in ("overheat", "thermal_runaway"):
                return 100
            if emergency.action == "shutdown":
                return 0
        if status:
            # Map status.value (1-10) to speed (0-100)
            return min(max(status.value * 10, 0), 100)
        return 0

    def publish_speed(self, speed: int):
        """Publish the fan speed to MQTT."""
        now = datetime.datetime.utcnow().isoformat() + "Z"
        fan_speed = FanSpeedDTO(
            fanId=self.fan_id,
            speed=speed,
            actual=speed,  # In real use, replace with measured value if available
            timestamp=now
        )
        # Print the JSON message as it would be sent
        import json
        print("MQTT OUT:", json.dumps(fan_speed.__dict__))
        self.publisher.publish_fan_speed(fan_speed)
        logging.info(f"Published fan speed DTO: {fan_speed}")

    def _start_thermal_runaway_timer(self):
        """Start a timer for thermal runaway emergency."""
        if self._thermal_runaway_timer and self._thermal_runaway_timer.is_alive():
            self._thermal_runaway_timer.cancel()
            logging.info("Existing thermal runaway timer cancelled.")
        self._thermal_runaway_timer = threading.Timer(30, self._end_thermal_runaway)
        self._thermal_runaway_timer.start()
        logging.info("Thermal runaway timer started for 30 seconds.")

    def _end_thermal_runaway(self):
        """Callback to end thermal runaway emergency after timer expires."""
        self.repository.clear_emergency()
        logging.info("Thermal runaway period ended. Returning to normal operation.")
        self.update_speed()

