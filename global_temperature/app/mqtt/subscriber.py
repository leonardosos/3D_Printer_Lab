import json
from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO

class MQTTSubscriber:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def subscribe_room_temperature(self, callback):
        """
        Subscribes to room (only one) temperature readings.
        Topic: device/room/temperature
        Type: TemperatureReadingRoomDTO
        QoS: 0
        """
        topic = "device/room/temperature"
        def dto_callback(client, userdata, message):
            payload = json.loads(message.payload.decode())
            dto = TemperatureReadingRoomDTO(
                sensorId=payload.get("sensorId"),
                temperature=payload.get("temperature"),
                unit=payload.get("unit"),
                timestamp=payload.get("timestamp")
            )
            callback(client, userdata, dto)
        self.mqtt_client.subscribe(topic, dto_callback, qos=0)

    def subscribe_printer_temperature(self, callback):
        """
        Subscribes to printer temperature readings.
        Topic: device/printer/all printers/temperature
        Type: TemperatureReadingPrinterDTO
        QoS: 1
        """
        topic = f"device/printer/+/temperature"
        def dto_callback(client, userdata, message):
            payload = json.loads(message.payload.decode())
            dto = TemperatureReadingPrinterDTO(
                printerId=payload.get("printerId"),
                temperature=payload.get("temperature"),
                unit=payload.get("unit"),
                timestamp=payload.get("timestamp")
            )
            callback(client, userdata, dto)
        self.mqtt_client.subscribe(topic, dto_callback, qos=1)


if __name__ == "__main__":
    # Example usage for testing
    #
    #from global_temperature directory:
    #
    #    cd /home/leonardo/iot/IoT_Project/global_temperature
    #    python3 -m app.mqtt.subscriber
    #
    
    from app.mqtt.client import MQTTClient
    def dummy_callback(client, userdata, assignment_dto):
        print("Received assignment DTO:", assignment_dto)
    client = MQTTClient("app/mqtt_config.yaml")
    client.connect()
    client.loop_start()
    subscriber = MQTTSubscriber(client)
    subscriber.subscribe_room_temperature(dummy_callback)
    subscriber.subscribe_printer_temperature(dummy_callback)
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting subscriber...")
        client.loop_stop()
        client.client.disconnect()

