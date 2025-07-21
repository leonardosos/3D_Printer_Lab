import json
import threading
import logging
import paho.mqtt.client as mqtt

from app.dto.printer_progress_dto import PrinterProgressDTO
from app.dto.job_dto import JobDTO

class MQTTSubscriber:
    def __init__(self, broker_host, broker_port, printer_monitoring):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.printer_monitoring = printer_monitoring
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self):
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_forever()
        except Exception as e:
            logging.error(f"MQTT connection error: {e}")

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected to MQTT broker with result code " + str(rc))
        # Subscribe to all relevant topics
        client.subscribe("device/printer/+/progress")
        client.subscribe("device/printer/+/assignement")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic

            if topic.startswith("device/printer/") and topic.endswith("/progress"):
                required = {"printerId", "jobId", "status", "progress", "timestamp"}
                if not required.issubset(payload):
                    logging.error(f"Missing fields in printer progress: {payload}")
                    return
                dto = PrinterProgressDTO(**payload)
                self.printer_monitoring.on_printer_progress(dto)
            elif topic.startswith("device/printer/") and topic.endswith("/assignement"):
                required = {"jobId", "modelUrl", "filamentType", "estimatedTime", "priority", "assignedAt", "parameters"}
                if not required.issubset(payload):
                    logging.error(f"Missing fields in job assignment: {payload}")
                    return
                dto = JobDTO(**payload)
                self.printer_monitoring.on_job_assignement(dto)
            else:
                logging.warning(f"Unknown topic: {topic}")

            logging.info(f"Received message on {topic}: {payload}")

        except Exception as e:
            logging.error(f"Error processing message on {msg.topic}: {e}")

# Standalone test mode
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    class DummyPrinterMonitoring:
        def on_printer_progress(self, dto):
            print(f"[Dummy] Printer progress: {dto}")

        def on_job_assignement(self, dto):
            print(f"[Dummy] Job assignment: {dto}")

    broker_host = "localhost"
    broker_port = 1883

    subscriber = MQTTSubscriber(broker_host, broker_port, DummyPrinterMonitoring())
    print("Starting MQTT subscriber in standalone mode. Press Ctrl+C to exit.")