import os
import yaml
import json
import logging
import paho.mqtt.client as mqtt
from dataclasses import asdict

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../config/fan_controller_config.yaml')

class MqttPublisher:
    def __init__(self, client=None):
        self.config = self._load_config()
        self.client = client or mqtt.Client()
        self._connected = False
        self._queue = []
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def _load_config(self):
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)

    def _on_connect(self, client, userdata, flags, rc):
        self._connected = True
        logging.info("Publisher connected to MQTT broker with result code %s", rc)
        # Publish any queued messages
        while self._queue:
            topic, payload = self._queue.pop(0)
            self._publish(topic, payload)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        logging.warning("Publisher disconnected from MQTT broker with result code %s", rc)

    def connect(self):
        self.client.connect(self.config['mqtt']['host'], self.config['mqtt']['port'], 60)
        self.client.loop_start()

    def publish_fan_speed(self, fan_speed_dto, sync=False):
        topic = f"device/fan/{fan_speed_dto.fanId}/speed"
        payload = json.dumps(asdict(fan_speed_dto))
        if self._connected:
            self._publish(topic, payload, sync)
        else:
            logging.warning("MQTT not connected, queuing message for topic %s", topic)
            self._queue.append((topic, payload))

    def _publish(self, topic, payload, sync=False):
        try:
            result = self.client.publish(topic, payload, 0)
            if sync:
                result.wait_for_publish()
            logging.info("Published to %s: %s", topic, payload)
        except Exception as e:
            logging.error("Failed to publish to %s: %s", topic, e)
            self._queue.append((topic, payload))


    # testing

if __name__ == "__main__":
    import time
    from app.dto.fan_speed_dto import FanSpeedDTO

    logging.basicConfig(level=logging.INFO)

    publisher = MqttPublisher()
    publisher.connect()
    time.sleep(1)  # Allow time for MQTT connection

    test_dto = FanSpeedDTO(
        fanId="fan-1",
        speed=75,
        actual=72,
        timestamp="2025-06-15T08:32:15Z"
    )
    publisher.publish_fan_speed(test_dto, sync=True)
    print("Published test FanSpeedDTO to MQTT broker.")

    # Keep the script alive briefly to ensure message delivery
    time.sleep(2)