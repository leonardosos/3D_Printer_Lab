import time
from datetime import datetime, timezone
from app.dto.fan_controller_temp_dto import FanControllerTempDTO

def iso8601_now():
    # Returns current UTC time in ISO 8601 format
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

class MQTTPublisher:
    def __init__(self, mqtt_client):

        # Initialize the passed MQTT client
        self.mqtt_client = mqtt_client  

    def publish_fan_heat_level(self, heat_level):
        """
        Publishes heat level to fan controller:
            Topic: device/fan/controller/status
            Type: FanControllerTempDTO
            QoS: 0
        """
        dto = FanControllerTempDTO(
            heatLevel=heat_level,
            timestamp=iso8601_now()
        )
        self.mqtt_client.publish(
            "device/fan/controller/status",
            dto.to_json(),
            qos=0
        )


if __name__ == "__main__":
    # Example usage for testing
    #
    # From global_temperature directory:
    #
    #    cd /home/leonardo/iot/IoT_Project/global_temperature
    #    python3 -m app.mqtt.publisher
    #
    from app.mqtt.client import MQTTClient
    client = MQTTClient("app/mqtt_config.yaml")
    client.connect()
    client.loop_start()
    publisher = MQTTPublisher(client)
    publisher.publish_fan_heat_level(7)
    time.sleep(1)
    client.loop_stop()
    print("MQTT messages published for testing.")