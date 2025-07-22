import time
import json
import threading
import paho.mqtt.client as mqtt
import os

# DTO
# 2.2.3) PrinterAssignment

from dataclasses import dataclass, asdict
import json

@dataclass
class AssignmentParameters:
    layerHeight: float
    infill: float
    nozzleTemp: float

@dataclass
class PrinterAssignmentDTO:
    jobId: str
    modelUrl: str
    filamentType: str
    estimatedTime: int
    priority: int
    assignedAt: str
    parameters: AssignmentParameters

    def to_json(self) -> str:
        # Serialize nested dataclass
        data = asdict(self)
        data['parameters'] = asdict(self.parameters)  # Serialize parameters
        return json.dumps(data)


########### TESTER

# Interval to publish assignment, periodically
timeout_publish = 120  # seconds 

# Topics
PRINTER_ID = "printer_001"
ASSIGNMENT_TOPIC = f"device/printer/{PRINTER_ID}/assignment"
PROGRESS_TOPIC = "device/printer/+/progress"
TEMPERATURE_TOPIC = "device/printer/+/temperature"
STATUS_TOPIC = "device/printer/+/status"

BROKER = os.environ.get("MQTT_BROKER", "localhost")
PORT = 1883



# Example assignment payload
assignment_payload = {
    "jobId": "job_001",
    "modelUrl": "http://example.com/model.gcode",
    "filamentType": "PLA",
    "estimatedTime": 10,
    "priority": 1,
    "assignedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "layerHeight": 0.2,
    "infill": 20,
    "nozzleTemp": 200
}

message_received_event = threading.Event()
def on_message(client, userdata, msg):
    print(f"[RECV] Topic: {msg.topic}\nPayload: {msg.payload.decode()}")
    message_received_event.set()

def subscribe_printer_topics(client):
    client.subscribe(PROGRESS_TOPIC, qos=0)
    client.subscribe(TEMPERATURE_TOPIC, qos=1)
    client.subscribe(STATUS_TOPIC, qos=0)
    client.on_message = on_message

def publish_assignment(client):
    # Build DTO from assignment_payload
    dto = PrinterAssignmentDTO(
        jobId=assignment_payload["jobId"],
        modelUrl=assignment_payload["modelUrl"],
        filamentType=assignment_payload["filamentType"],
        estimatedTime=assignment_payload["estimatedTime"],
        priority=assignment_payload["priority"],
        assignedAt=assignment_payload["assignedAt"],
        parameters=AssignmentParameters(
            layerHeight=assignment_payload["layerHeight"],
            infill=assignment_payload["infill"],
            nozzleTemp=assignment_payload["nozzleTemp"]
        )
    )
    print(f"[SEND] Publishing assignment DTO to {ASSIGNMENT_TOPIC}")
    client.publish(ASSIGNMENT_TOPIC, dto.to_json(), qos=1)

def main():
    from paho.mqtt.client import CallbackAPIVersion
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT)
    subscribe_printer_topics(client)
    client.loop_start()
    print(f"Publishing assignment every {timeout_publish} seconds. Waiting for printer responses... (Press Ctrl+C to exit)")
    try:
        last_publish = time.time() - 30
        while True:
            now = time.time()
            if now - last_publish >= timeout_publish:
                publish_assignment(client)
                last_publish = now
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting...")
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
