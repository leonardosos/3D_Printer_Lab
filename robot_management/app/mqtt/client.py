"""
MQTT client for Robot Management microservice.
"""
import time
import logging
import os
import paho.mqtt.client as mqtt
from typing import Dict, Any, Callable, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('/app/logs', 'mqtt_client.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MQTTClient:
    """
    MQTT client for handling communication with the MQTT broker.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MQTT client.
        
        Args:
            config: MQTT configuration dictionary
        """
        self.broker = config.get("broker", "localhost")
        self.port = config.get("port", 1883)
        self.client_id = config.get("client_id", "robot-management-service")
        self.keep_alive = config.get("keep_alive", 60)
        self.reconnect_delay = config.get("reconnect_delay", 5)
        
        # Initialize callbacks dictionary
        self.topic_callbacks = {}
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to the MQTT broker.
        
        Returns:
            True if connection was successful, False otherwise.
        """
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, self.keep_alive)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from the MQTT broker.
        """
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    def subscribe(self, topic: str, callback: Callable[[str, str], None]) -> None:
        """
        Subscribe to a topic and register a callback for that topic.
        
        Args:
            topic: The topic to subscribe to
            callback: Function to call when a message is received on this topic
        """
        logger.info(f"Subscribing to topic: {topic}")
        self.topic_callbacks[topic] = callback
        self.client.subscribe(topic)
    
    def publish(self, topic: str, payload: str, qos: int = 0) -> None:
        """
        Publish a message to a topic.
        
        Args:
            topic: The topic to publish to
            payload: The message payload
            qos: Quality of Service level
        """
        logger.info(f"Publishing to topic {topic}: {payload}")
        self.client.publish(topic, payload, qos)
    
    def wait_for_connection(self, timeout: int = 10) -> bool:
        """
        Wait for connection to the MQTT broker.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if connected, False if timeout occurred
        """
        start_time = time.time()
        while not self.connected and time.time() - start_time < timeout:
            time.sleep(0.1)
        return self.connected
    
    def _on_connect(self, client, userdata, flags, rc) -> None:
        """
        Callback for when the client connects to the broker.
        
        Args:
            client: The client instance
            userdata: User data passed to client
            flags: Connection flags
            rc: Result code
        """
        if rc == 0:
            logger.info("Connected to MQTT broker")
            self.connected = True
            
            # Resubscribe to topics
            for topic in self.topic_callbacks:
                logger.info(f"Resubscribing to topic: {topic}")
                self.client.subscribe(topic)
        else:
            logger.error(f"Failed to connect to MQTT broker with code {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc) -> None:
        """
        Callback for when the client disconnects from the broker.
        
        Args:
            client: The client instance
            userdata: User data passed to client
            rc: Result code
        """
        logger.warning(f"Disconnected from MQTT broker with code {rc}")
        self.connected = False
        
        # If disconnection was unexpected, try to reconnect
        if rc != 0:
            logger.info(f"Attempting to reconnect in {self.reconnect_delay} seconds")
            time.sleep(self.reconnect_delay)
            try:
                self.client.reconnect()
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}")
    
    def _on_message(self, client, userdata, msg) -> None:
        """
        Callback for when a message is received from the broker.
        
        Args:
            client: The client instance
            userdata: User data passed to client
            msg: The message
        """
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        logger.debug(f"Message received on topic {topic}: {payload}")
        
        # Call the appropriate callback for this topic
        if topic in self.topic_callbacks:
            try:
                self.topic_callbacks[topic](topic, payload)
            except Exception as e:
                logger.error(f"Error in callback for topic {topic}: {e}")
        else:
            logger.warning(f"No callback registered for topic {topic}")
