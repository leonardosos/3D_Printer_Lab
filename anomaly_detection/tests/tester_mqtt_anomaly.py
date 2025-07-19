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

### Configuration & Constants ###

multiplicator = 1/2

# If and when to publish
pub_printer = True
PRINTER_TEMP_INTERVAL = 30 * multiplicator

pub_odd_printer = True
ODD_PRINTER_TEMP_INTERVAL = 30 * multiplicator

pub_room = True
ROOM_TEMP_INTERVAL = 30 * multiplicator

pub_odd_room = False
ODD_ROOM_TEMP_INTERVAL = 30 * multiplicator

# MQTT Configuration
BROKER = os.environ.get("MQTT_BROKER", "localhost")
PORT = int(os.environ.get("MQTT_PORT", "1883"))

# Room and Printer IDs
ROOM_SENSOR_ID = os.environ.get("ROOM_SENSOR_ID", "room-sensor-1")
ODD_ROOM_SENSOR_ID = "room-sensor-odd"  # <-- Added odd room sensor ID
ODD_PRINTER_ID = "printer_odd"
PRINTER_IDS = ["printer_001", "printer_002"]

# MQTT Topics
PRINTER_TEMP_TOPIC = "device/printer/{}/temperature"
ODD_PRINTER_TEMP_TOPIC = PRINTER_TEMP_TOPIC.format(ODD_PRINTER_ID)
ROOM_TEMP_TOPIC = "device/room/temperature"
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
        temperature = round(random.uniform(19.0, 22.0), 2)
        dto = TemperatureReadingPrinterDTO(
            printerId=printer_id,
            temperature=temperature,
            unit="C",
            timestamp=iso8601_now()
        )
        topic = PRINTER_TEMP_TOPIC.format(printer_id)
        print(f"[SEND] Publishing printer temperature DTO to {topic}")
        client.publish(topic, dto.to_json(), qos=1)

def publish_odd_printer_temperature(client, alert_type: str = "overheat"):
    # Overheat: constant high temp; Thermal Runaway: rapid increase
    if alert_type == "overheat":
        temp = 400.0  # constant high value
    elif alert_type == "thermal_runaway":
        if not hasattr(publish_odd_printer_temperature, "temp"):
            publish_odd_printer_temperature.temp = 200.0
        publish_odd_printer_temperature.temp += random.uniform(5.0, 15.0)
        temp = publish_odd_printer_temperature.temp
    else:
        temp = 20.0  # fallback

    dto = TemperatureReadingPrinterDTO(
        printerId=ODD_PRINTER_ID,
        temperature=round(temp, 2),
        unit="C",
        timestamp=iso8601_now()
    )
    print(f"[SEND] Publishing odd printer temperature DTO to {ODD_PRINTER_TEMP_TOPIC} ({alert_type})")
    client.publish(ODD_PRINTER_TEMP_TOPIC, dto.to_json(), qos=1)

def publish_odd_room_temperature(client, alert_type: str = "overheat"):
    # Overheat: constant high temp; Thermal Runaway: rapid increase
    if alert_type == "overheat":
        temp = 80.0  # constant high value
    elif alert_type == "thermal_runaway":
        if not hasattr(publish_odd_room_temperature, "temp"):
            publish_odd_room_temperature.temp = 25.0
        publish_odd_room_temperature.temp += random.uniform(2.0, 5.0)
        temp = publish_odd_room_temperature.temp
    else:
        temp = 25.0  # fallback

    dto = TemperatureReadingRoomDTO(
        sensorId=ODD_ROOM_SENSOR_ID,
        temperature=round(temp, 2),
        unit="C",
        timestamp=iso8601_now()
    )
    print(f"[SEND] Publishing odd room temperature DTO to {ROOM_TEMP_TOPIC} ({alert_type})")
    client.publish(ROOM_TEMP_TOPIC, dto.to_json(), qos=0)

### Main Logic ###

def main():
    # Initialize MQTT client
    from paho.mqtt.client import CallbackAPIVersion
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT)
    subscribe_topics(client)
    client.loop_start()

    print("Press Ctrl+C to exit.")
    print("Type 'e' + Enter to send an emergency command (printer overheat).")
    
    # Timer for publishing
    last_room = time.time() - ROOM_TEMP_INTERVAL
    last_printer = time.time() - PRINTER_TEMP_INTERVAL
    last_odd_printer = time.time() - PRINTER_TEMP_INTERVAL
    last_odd_room = time.time() - ROOM_TEMP_INTERVAL  # <-- Add timer for odd room

    try:
        while True:
            now = time.time()
            
            # Publish room temperature if enabled
            if (now - last_room >= ROOM_TEMP_INTERVAL) and pub_room:
                publish_room_temperature(client)
                last_room = now

            # Publish printer temperatures if enabled
            if (now - last_printer >= PRINTER_TEMP_INTERVAL) and pub_printer:
                publish_printer_temperatures(client)
                last_printer = now

            # Publish odd printer temperature if enabled
            if (now - last_odd_printer >= ODD_PRINTER_TEMP_INTERVAL) and pub_odd_printer:
                publish_odd_printer_temperature(client, alert_type="overheat")
                last_odd_printer = now

            # Publish odd room temperature if enabled
            if (now - last_odd_room >= ODD_ROOM_TEMP_INTERVAL) and pub_odd_room:
                publish_odd_room_temperature(client, alert_type="overheat")
                last_odd_room = now
            
            # Sospiro command
            else:
                time.sleep(0.5)
    # Close all
    except KeyboardInterrupt:
        print("Exiting tester...")
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()