import time
from datetime import datetime, timezone
from app.dto.emergency_command_dto import EmergencyCommandDTO

def iso8601_now():
    # Returns current UTC time in ISO 8601 format
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

class MQTTPublisher:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client  

    def publish_emergency_command(self, action, type_, source, id_):
        """
        Publishes an emergency command to the fan controller:
            Topic: device/fan/controller/emergency
            Type: EmergencyCommandDTO
            QoS: 2 (safety critical)
        """
        dto = EmergencyCommandDTO(
            action=action,
            type=type_,
            source=source,
            id=id_,
            timestamp=iso8601_now()
        )

        if self.mqtt_client.debug:
            print(f"[MQTT PUBLISHER DEBUG] Publishing emergency command: {dto.to_json()}")

        self.mqtt_client.publish(
            "device/fan/controller/emergency",
            dto.to_json(),
            qos=2
        )

if __name__ == "__main__":
    # Example usage for testing
    #
    # cd anomaly_detection/
    # python3 -m app.mqtt.publisher 
    #
    from app.mqtt.client import MQTTClient
    client = MQTTClient("app/mqtt_config.yaml")
    client.connect()
    client.loop_start()
    publisher = MQTTPublisher(client)
    publisher.publish_emergency_command(
        action="emergency",
        type_="overheat",
        source="printer",
        id_="printer123"
    )
    time.sleep(1)
    client.loop_stop()
    print("Emergency MQTT message published for testing.")