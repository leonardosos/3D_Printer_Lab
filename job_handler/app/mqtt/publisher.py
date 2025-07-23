import paho.mqtt.client as mqtt
import json
import logging
from dataclasses import asdict
from app.dto.assignment_dto import Assignment
from app.dto.printer_list_dto import PrintersList
import datetime

class MQTTPublisher:
    def __init__(self, broker_host: str, broker_port: int, qos: int = 1):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.qos = qos
        self.client = mqtt.Client()
        self.client.connect(self.broker_host, self.broker_port)
        self.client.loop_start()

    def publish_assignment(self, printer_id: str, assignment: Assignment):
        topic = f"device/printer/{printer_id}/assignment"
        payload = json.dumps(asdict(assignment))
        try:
            self.client.publish(topic, payload, qos=self.qos)
            logging.info(f"Published assignment to {topic}: {payload}")
        except Exception as e:
            logging.error(f"Failed to publish assignment: {e}")

    def publish_printers_list(self, printers_list: PrintersList):

        # Assuming printers_list has an attribute 'printers' which is a list of printer objects
        if hasattr(printers_list, 'printers') and printers_list.printers:
            printers_list.printers[0].status = "finish"
            printers_list.printers[0].timestamp = datetime.datetime.utcnow().isoformat() + "Z"

        topic = "device/printers"
        payload = json.dumps(asdict(printers_list))
        try:
            self.client.publish(topic, payload, qos=self.qos)
            logging.info(f"Published printers list to {topic}: {payload}")
        except Exception as e:
            logging.error(f"Failed to publish printers list: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()