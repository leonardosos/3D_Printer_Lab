import os
import time
import random
import json
import threading
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

@dataclass
class EmergencyCommandDTO:
    action: str            # "emergency" | "emergency_finished"
    type: str              # "overheat" | "thermal_runaway"
    source: str            # "printer" | "room"
    id: str                # printerId or sensorId
    timestamp: str         # ISO 8601
    def to_json(self) -> str:
        return json.dumps(asdict(self))

# MQTT Configuration
BROKER = os.environ.get("MQTT_BROKER", "localhost")
PORT = int(os.environ.get("MQTT_PORT", "1883"))

EMERGENCY_TOPIC = "device/fan/controller/emergency"


### Utility Functions ###

def iso8601_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

### MQTT Functions ###

def on_message(client, userdata, msg):
    print(f"[RECV] Topic: {msg.topic}\nPayload: {msg.payload.decode()}")

def subscribe_topics(client):
    client.subscribe(EMERGENCY_TOPIC, qos=2)
    client.on_message = on_message


### Main Logic ###

def main():
    # Initialize MQTT client
    from paho.mqtt.client import CallbackAPIVersion
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT)
    subscribe_topics(client)
    client.loop_start()

    print("Press Ctrl+C to exit.")
    print("Type 'e' to send an emergency command.")
    try:
        while True:
            time.sleep(0.5)
    # Close all
    except KeyboardInterrupt:
        print("Exiting tester...")
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()