"""
GlobalTemperatureService: Main service class for temperature aggregation, fan control, and API.
"""
from app.persistence.temperature_history import TemperatureHistory
from IoT_Project.global_temperature.app.models.temperature_analyzer import TemperatureAnalyzer
from app.mqtt.subscriber import MQTTSubscriber
from app.mqtt.publisher import MQTTPublisher
from app.dto.fan_controller_temp_dto import FanControllerTempDTO
from app.dto.global_temperature_response_dto import GlobalTemperatureResponseDTO
from app.services.discover_printers import discover_printers

class GlobalTemperatureService:
    def __init__(self, mqtt_client, debug=True):

        self.debug = debug

        # Initialize MQTT communication with provided client
        self.subscriber = MQTTSubscriber(mqtt_client)
        self.publisher = MQTTPublisher(mqtt_client)

        # Search all printers in the network -> blocking call
        # Any payload with printerId will be added to the discovered printers
        self.printers = discover_printers(self.subscriber, timeout=60, debug=self.debug)

        # Initialize temperature history and analyzer
        self.history = TemperatureHistory(self.printers, debug=self.debug)

        # Initialize temperature analyzer for heat level computation
        self.analyzer = TemperatureAnalyzer()


    def start(self):
        # Subscribe to room and printer temperature topics
        self.subscriber.subscribe_room_temperature(self._on_room_temp)
        self.subscriber.subscribe_printer_temperature(self._on_printer_temp)
        self.periodic_fan_update()

    # Custom callbacks for MQTT messages, for store temperature readings
    def _on_room_temp(self, client, userdata, dto):
        self.history.add_room_reading(dto)

    def _on_printer_temp(self, client, userdata, dto):
        self.history.add_printer_reading(dto)

    # Method to compute and publish fan heat level one time -> need to be called periodically
    def fan_update(self):
        # Get the latest temperature
        room_temp = self.history.get_latest_room()
        printers_temp = self.history.get_latest_printers()

        if self.debug:
            print(f"[GLOBAL_TEMP DEBUG] Room temp: {room_temp.temperature if room_temp else 'No data'}")
            print(f"[GLOBAL_TEMP DEBUG] Latest printer temps: {printers_temp}")

        # Compute heat level and publish to fan controller
        heat_level = self.analyzer.compute_heat_level(
            room_readings=self.history.get_latest_room(),
            printer_readings=list(self.history.get_latest_printers().values())
        )
        if self.debug:
            print(f"[GLOBAL_TEMP DEBUG] Computed heat level: {heat_level}")

        self.publisher.publish_fan_heat_level(heat_level)

    def periodic_fan_update(self):
        """Periodically update the fan based on temperature readings."""
        pass

    # get all temperature readings for API response


# define the total behavior of the service
# define the total printrs
# priodic fan update
# create the MQTT client and start it
# start the GlobalTemperatureService

# do i need classes??