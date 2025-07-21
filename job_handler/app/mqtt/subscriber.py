import paho.mqtt.client as mqtt
import json
import logging
from typing import Callable
from job_handler.app.dto.printer_progress_dto import PrinterProgress
from job_handler.app.dto.robot_progress_dto import RobotProgress

class MQTTSubscriber:
    def __init__(self, broker_host: str, broker_port: int, on_printer_progress: Callable[[PrinterProgress], None], on_robot_progress: Callable[[RobotProgress], None]):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.on_printer_progress = on_printer_progress
        self.on_robot_progress = on_robot_progress
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        self.client.connect(self.broker_host, self.broker_port)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected to MQTT broker with result code %s", rc)
        # Subscribe to all printer and robot progress topics
        client.subscribe("device/printer/+/progress")
        client.subscribe("device/robot/+/progress")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            if topic.startswith("device/printer/"):
                progress = PrinterProgress(**payload)
                logging.info(f"Received PrinterProgress: {progress}")
                self.on_printer_progress(progress)
            elif topic.startswith("device/robot/"):
                progress = RobotProgress(**payload)
                logging.info(f"Received RobotProgress: {progress}")
                self.on_robot_progress(progress)
            else:
                logging.warning(f"Unknown topic: {topic}")
        except Exception as e:
            logging.error(f"Error processing message on topic {msg.topic}: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()