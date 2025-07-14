"""
GlobalTemperatureService: Main service class for temperature aggregation, fan control, and API.
"""
from app.persistence.temperature_history import TemperatureHistory
from IoT_Project.global_temperature.app.models.temperature_analyzer import TemperatureAnalyzer
from app.mqtt.subscriber import MQTTSubscriber
from app.mqtt.publisher import MQTTPublisher
from app.dto.fan_controller_temp_dto import FanControllerTempDTO
from app.dto.global_temperature_response_dto import GlobalTemperatureResponseDTO


class GlobalTemperatureService:
    def __init__(self, mqtt_client):
        # Initialize temperature history and analyzer
        self.history = TemperatureHistory()
        self.analyzer = TemperatureAnalyzer()

        # Initialize MQTT communication with provided client
        self.subscriber = MQTTSubscriber(mqtt_client)
        self.publisher = MQTTPublisher(mqtt_client)



    def start(self):
        # Subscribe to room and printer temperature topics
        self.subscriber.subscribe_room_temperature(self._on_room_temp)
        self.subscriber.subscribe_printer_temperature(self._on_printer_temp)

    # Custom callbacks for MQTT messages, for store temperature readings
    def _on_room_temp(self, client, userdata, dto):
        self.history.add_room_reading(dto)

    def _on_printer_temp(self, client, userdata, dto):
        self.history.add_printer_reading(dto)

    # Method to compute and publish fan heat level one time -> need to be called periodically
    def periodic_fan_update(self):
        # Compute heat level and publish to fan controller
        heat_level = self.analyzer.compute_heat_level(self.history.room_readings, self.history.printer_readings)
        self.publisher.publish_fan_heat_level(heat_level)


    # get all temperature readings for API response


# define the total behavior of the service
# define the total printrs
# priodic fan update
# create the MQTT client and start it
# start the GlobalTemperatureService