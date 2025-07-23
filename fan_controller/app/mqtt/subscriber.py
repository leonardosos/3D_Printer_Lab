import os
import yaml
import json
import logging
import paho.mqtt.client as mqtt

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../config/fan_controller_config.yaml')

class MqttSubscriber:
    def __init__(self, on_status, on_emergency):
        self.config = self._load_config()
        self.client = mqtt.Client()
        self.on_status = on_status
        self.on_emergency = on_emergency

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _load_config(self):
        with open(CONFIG_PATH, 'r') as f:
            print(CONFIG_PATH, "config path")
            return yaml.safe_load(f)

    def _on_connect(self, client, userdata, flags, rc):
        logging.info("Connected to MQTT broker with result code %s", rc)
        client.subscribe(self.config['topics']['status'], 0)
        client.subscribe(self.config['topics']['emergency'], 2)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            if msg.topic == self.config['topics']['status']:
                self.on_status(payload)
            elif msg.topic == self.config['topics']['emergency']:
                self.on_emergency(payload)
            else:
                logging.warning("Received message on unknown topic: %s", msg.topic)
        except Exception as e:
            logging.error("Error processing message: %s", e)

    def start(self):
        self.client.connect(self.config['mqtt']['host'], self.config['mqtt']['port'], 60)
        self.client.loop_forever()


# Testing

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    def print_status(payload):
        print(f"Received STATUS: {payload}")

    def print_emergency(payload):
        print(f"Received EMERGENCY: {payload}")

    subscriber = MqttSubscriber(on_status=print_status, on_emergency=print_emergency)
    print("Starting MQTT subscriber. Waiting for messages...")
    subscriber.start()

