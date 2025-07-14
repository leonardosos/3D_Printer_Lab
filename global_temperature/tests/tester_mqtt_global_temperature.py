import time
import threading
import os
import random
import json
import paho.mqtt.client as mqtt

# DTOs (copied inside for self-contained testing)
from dataclasses import dataclass, asdict

@dataclass
class TemperatureReadingRoomDTO:
    sensorId: str
    temperature: float
    unit: str  # "C"
    timestamp: str

    def to_json(self) -> str:
        return json.dumps(asdict(self))

@dataclass
class FanControllerTempDTO:
    heatLevel: int  # interpreted temperature level for fan controller
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

# Topics and config
ROOM_SENSOR_ID = os.environ.get("ROOM_SENSOR_ID", "room-sensor-1")
ROOM_TEMP_TOPIC = "device/room/temperature"
FAN_STATUS_TOPIC = "device/fan/controller/status"
BROKER = os.environ.get("MQTT_BROKER", "localhost")
PORT = int(os.environ.get("MQTT_PORT", "1883"))

ROOM_TEMP_INTERVAL = 25
FAN_HEAT_INTERVAL = 15
PRINTER_TEMP_INTERVAL = 10  # seconds

PRINTER_IDS = ["printer_001", "printer_002"]
PRINTER_TEMP_TOPIC = "device/printer/{}/temperature"

def iso8601_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def on_message(client, userdata, msg):
    print(f"[RECV] Topic: {msg.topic}\nPayload: {msg.payload.decode()}")

def publish_room_temperature(client):
    temperature = round(random.uniform(21.0, 26.0), 2)
    dto = TemperatureReadingRoomDTO(
        sensorId=ROOM_SENSOR_ID,
        temperature=temperature,
        unit="C",
        timestamp=iso8601_now()
    )
    print(f"[SEND] Publishing room temperature DTO to {ROOM_TEMP_TOPIC}")
    client.publish(ROOM_TEMP_TOPIC, dto.to_json(), qos=0)

def publish_printer_temperatures(client):
    for printer_id in PRINTER_IDS:
        temperature = round(random.uniform(190.0, 220.0), 2)
        dto = TemperatureReadingPrinterDTO(
            printerId=printer_id,
            temperature=temperature,
            unit="C",
            timestamp=iso8601_now()
        )
        topic = PRINTER_TEMP_TOPIC.format(printer_id)
        print(f"[SEND] Publishing printer temperature DTO to {topic}")
        client.publish(topic, dto.to_json(), qos=1)

def subscribe_topics(client):
    client.subscribe(FAN_STATUS_TOPIC, qos=0)
    client.on_message = on_message

def main():
    from paho.mqtt.client import CallbackAPIVersion
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT)
    subscribe_topics(client)
    client.loop_start()
    print(f"Publishing room temperature every {ROOM_TEMP_INTERVAL}s and printer temperatures every {PRINTER_TEMP_INTERVAL}s. (Ctrl+C to exit)")
    last_room = time.time() - ROOM_TEMP_INTERVAL
    last_printer = time.time() - PRINTER_TEMP_INTERVAL
    try:
        while True:
            now = time.time()
            if now - last_room >= ROOM_TEMP_INTERVAL:
                publish_room_temperature(client)
                last_room = now
            if now - last_printer >= PRINTER_TEMP_INTERVAL:
                publish_printer_temperatures(client)
                last_printer = now
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting tester...")
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()