import paho.mqtt.client as mqtt
import json
import logging
import random
import string
import time

class MQTTClient:
    """Handles MQTT communication with the broker"""
    
    def __init__(self, sensor_id, broker_host="localhost", broker_port=1883, topic="device/room/temperature"):
        """Initialize the MQTT client"""
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        
        # Create a unique client ID based on sensor ID
        random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        self.client_id = f"{sensor_id}-{random_suffix}"
        
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
        self.logger = logging.getLogger(__name__)
        self.connected = False
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            self.connected = True
            self.logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
        else:
            self.logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker"""
        self.connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection from MQTT broker, return code: {rc}")
        else:
            self.logger.info("Disconnected from MQTT broker")
    
    def connect(self, max_retries=5):
        """Connect to the MQTT broker with retry logic"""
        retry_count = 0
        while not self.connected and retry_count < max_retries:
            try:
                self.logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
                self.client.connect(self.broker_host, self.broker_port)
                self.client.loop_start()
                
                # Wait for connection to establish
                timeout = 5
                start_time = time.time()
                while not self.connected and time.time() - start_time < timeout:
                    time.sleep(0.1)
                
                if self.connected:
                    return True
                
            except Exception as e:
                self.logger.error(f"Error connecting to MQTT broker: {str(e)}")
            
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                self.logger.info(f"Retrying connection in {wait_time} seconds...")
                time.sleep(wait_time)
        
        if not self.connected:
            self.logger.error("Failed to connect to MQTT broker after maximum retries")
            return False
        
        return True
    
    def publish(self, message):
        """Publish a message to the configured topic"""
        if not self.connected:
            if not self.connect():
                self.logger.error("Cannot publish message: not connected to MQTT broker")
                return False
        
        try:
            # Convert dict to JSON string if necessary
            if isinstance(message, dict):
                message = json.dumps(message)
            
            result = self.client.publish(self.topic, message, qos=0)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Message published to topic {self.topic}")
                return True
            else:
                self.logger.error(f"Failed to publish message, return code: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error publishing message: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the MQTT broker"""
        if self.connected:
            self.logger.info("Disconnecting from MQTT broker")
            self.client.loop_stop()
            self.client.disconnect()
