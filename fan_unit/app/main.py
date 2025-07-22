import json
import time
import logging
import os
from datetime import datetime
import yaml
import paho.mqtt.client as mqtt
from dto import FanSpeedMessage

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get fan ID from environment variable or use default
FAN_ID = os.environ.get("FAN_ID", "fan1")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

if DEBUG:
    logger.setLevel(logging.DEBUG)

class FanUnit:
    def __init__(self, config_path="/app/app/config.yaml"):
        self.current_speed = 0
        self.load_config(config_path)
        self.setup_mqtt()
        
    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
            logger.info("Configuration loaded successfully")
            logger.debug(f"Config: {self.config}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Use default configuration
            self.config = {
                "mqtt": {
                    "broker_host": "broker",
                    "broker_port": 1883,
                    "topic_subscribe": f"device/fan/{FAN_ID}/speed",
                    "qos": 1
                },
                "fan": {
                    "id": FAN_ID,
                    "min_speed": 0,
                    "max_speed": 100
                }
            }
            logger.info("Using default configuration")
            
    def setup_mqtt(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        mqtt_host = self.config["mqtt"]["broker_host"]
        mqtt_port = self.config["mqtt"]["broker_port"]
        
        try:
            logger.info(f"Connecting to MQTT broker at {mqtt_host}:{mqtt_port}")
            self.client.connect(mqtt_host, mqtt_port, 60)
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
            topic = self.config["mqtt"]["topic_subscribe"]
            qos = self.config["mqtt"]["qos"]
            client.subscribe(topic, qos)
            logger.info(f"Subscribed to topic: {topic} with QoS: {qos}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            logger.debug(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
            payload = json.loads(msg.payload.decode())
            
            # Validate message with DTO
            fan_message = FanSpeedMessage(**payload)
            
            # Check if this message is for this fan
            if fan_message.fanId != self.config["fan"]["id"]:
                logger.debug(f"Message not for this fan. Expected {self.config['fan']['id']}, got {fan_message.fanId}")
                return
                
            # Set fan speed
            self.set_fan_speed(fan_message.speed)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    def set_fan_speed(self, speed):
        """Set the fan speed and calculate the proportional current."""
        # Ensure speed is within valid range
        speed = max(self.config["fan"]["min_speed"], min(self.config["fan"]["max_speed"], speed))
        
        # Update current speed
        self.current_speed = speed
        # logger.info(f"Fan speed set to {speed}%")
        
        # Calculate current (in amperes) - just a simple proportional relationship
        # Assuming max current is 1.0A at 100% speed
        current = (speed / 100.0) * 1.0
        logger.info(f"Fan current set to {current:.2f}A")
        
        # In a real implementation, this would control actual hardware
        return current
        
    def run(self):
        """Start the MQTT client loop and keep the application running."""
        self.client.loop_start()
        try:
            logger.info("Fan unit service started")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down fan unit service")
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    fan_unit = FanUnit()
    fan_unit.run()
