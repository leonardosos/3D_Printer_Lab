import os
import time
import json
from dataclasses import dataclass, asdict
import paho.mqtt.client as mqtt

### Data Transfer Objects (DTOs) ###

@dataclass
class TemperatureReadingRoomDTO:
    sensorId: str
    temperature: float
    unit: str  # "C"
    timestamp: str
    def to_json(self) -> str:
        return json.dumps(asdict(self))

@dataclass
class TemperatureReadingPrinterDTO:
    printerId: str
    temperature: float
    unit: str  # "C"
    timestamp: str
    def to_json(self) -> str:
        return json.dumps(asdict(self))

### Configuration & Constants ###

BROKER = os.environ.get("MQTT_BROKER", "localhost")
PORT = int(os.environ.get("MQTT_PORT", "1883"))

ROOM_SENSOR_ID = os.environ.get("ROOM_SENSOR_ID", "room-sensor_odd_1")
PRINTER_ID = os.environ.get("PRINTER_ID", "printer_odd_1")

ROOM_TEMP_TOPIC = "device/room/temperature"
PRINTER_TEMP_TOPIC = "device/printer/{}/temperature".format(PRINTER_ID)

printer_publish = True  # Flag to control publishing to printer topic
room_publish = False# Flag to control publishing to room topic

### Utility Functions ###

def iso8601_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

### MQTT Functions ###

def on_message(client, userdata, msg):
    print(f"[RECV] Topic: {msg.topic}\nPayload: {msg.payload.decode()}")

def subscribe_topics(client):
    client.on_message = on_message

def publish_room_temperature(client, temperature, count=None):
    dto = TemperatureReadingRoomDTO(
        sensorId=ROOM_SENSOR_ID,
        temperature=temperature,
        unit="C",
        timestamp=iso8601_now()
    )
    msg = f"[SEND"
    if count is not None:
        msg += f" {count}"
    msg += f"] Publishing room temperature DTO to {ROOM_TEMP_TOPIC}: {temperature}°C"
    print(msg)
    client.publish(ROOM_TEMP_TOPIC, dto.to_json(), qos=0)

def publish_printer_temperature(client, temperature, count=None):
    dto = TemperatureReadingPrinterDTO(
        printerId=PRINTER_ID,
        temperature=temperature,
        unit="C",
        timestamp=iso8601_now()
    )
    msg = f"[SEND"
    if count is not None:
        msg += f" {count}"
    msg += f"] Publishing printer temperature DTO to {PRINTER_TEMP_TOPIC}: {temperature}°C"
    print(msg)
    client.publish(PRINTER_TEMP_TOPIC, dto.to_json(), qos=1)

### Main Logic ###

def main():
    client = mqtt.Client()
    client.connect(BROKER, PORT)
    subscribe_topics(client)
    client.loop_start()

    print("starting temperature publishing...")

    count = 1
    # Publish starting value (20°C) for 20 seconds
    start_time = time.time()
    while time.time() - start_time < 15:
        if room_publish:
            publish_room_temperature(client, 20, count)
        if printer_publish:
            publish_printer_temperature(client, 20, count)
        count += 1
        time.sleep(1)

    # Increase temperature from 20 to 500 over 60 seconds
    for temp in range(20, 501):
        if room_publish:
            publish_room_temperature(client, temp, count)
        if printer_publish:
            publish_printer_temperature(client, temp, count)
        count += 1
        time.sleep(0.12)  # ~60 seconds total

    # Hold at 500 degrees for 60 seconds
    hold_start = time.time()
    while time.time() - hold_start < 60:
        if room_publish:
            publish_room_temperature(client, 500, count)
        if printer_publish:
            publish_printer_temperature(client, 500, count)
        count += 1
        time.sleep(1)

    # Decrease temperature back to 20 over 60 seconds
    for temp in range(500, 19, -1):
        if room_publish:
            publish_room_temperature(client, temp, count)
        if printer_publish:
            publish_printer_temperature(client, temp, count)
        count += 1
        time.sleep(0.12)  # ~60 seconds total

    # Publish ending value (20°C) for 60 seconds
    end_time = time.time()
    while time.time() - end_time < 60:
        if room_publish:
            publish_room_temperature(client, 20, count)
        if printer_publish:
            publish_printer_temperature(client, 20, count)
        count += 1
        time.sleep(1)

    print("Temperature publishing completed.")


if __name__ == "__main__":
    main()