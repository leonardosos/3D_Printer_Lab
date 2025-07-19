"""
MQTT communication service for the robot.
Handles MQTT connection, message publishing and subscription.
"""
import logging
import uuid
from typing import Dict, Any, Callable

import paho.mqtt.client as mqtt
from app.dto.progress_dto import ProgressDTO

logger = logging.getLogger('robot')

class MqttService:
    """
    Service for MQTT communication.
    Handles connection to the MQTT broker, subscription to topics,
    and message publishing.
    """
    
    def __init__(self, config: Dict[str, Any], coordinate_callback: Callable[[str], None]):
        """
        Initialize the MQTT service.
        
        Args:
            config: Configuration dictionary
            coordinate_callback: Callback function for received coordinate messages
        """
        self.config = config
        self.robot_id = config['robot']['id']
        self.broker_host = config['mqtt']['broker_host']
        self.broker_port = config['mqtt']['broker_port']
        self.qos = config['mqtt']['qos']
        
        # Generate a unique client ID if not provided
        client_id = config['mqtt'].get('client_id', f"robot-{self.robot_id}-{uuid.uuid4().hex[:8]}")
        
        # Create MQTT client
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Store the callback for coordinate messages
        self.coordinate_callback = coordinate_callback
        
        # Define topics
        self.coordinate_topic = f"device/robot/{self.robot_id}/coordinates"
        self.progress_topic = f"device/robot/{self.robot_id}/progress"
    
    def connect(self):
        """Connect to the MQTT broker"""
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            raise
    
    def disconnect(self):
        """Disconnect from the MQTT broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {str(e)}")
    
    def subscribe(self):
        """Subscribe to the coordinate topic"""
        try:
            self.client.subscribe(self.coordinate_topic, self.qos)
            logger.info(f"Subscribed to topic: {self.coordinate_topic}")
        except Exception as e:
            logger.error(f"Failed to subscribe to {self.coordinate_topic}: {str(e)}")
            raise
    
    def publish_progress(self, progress_dto: ProgressDTO):
        """
        Publish a progress message.
        
        Args:
            progress_dto: Progress data transfer object
        """
        try:
            # Validate the DTO
            progress_dto.validate()
            
            # Convert to JSON and publish
            message = progress_dto.to_json()
            self.client.publish(self.progress_topic, message, self.qos)
            logger.info(f"Published to {self.progress_topic}: {message}")
        except Exception as e:
            logger.error(f"Failed to publish progress message: {str(e)}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Resubscribe in case of reconnection
            self.subscribe()
        else:
            connection_errors = {
                1: "incorrect protocol version",
                2: "invalid client identifier",
                3: "server unavailable",
                4: "bad username or password",
                5: "not authorized"
            }
            error_message = connection_errors.get(rc, f"unknown error code {rc}")
            logger.error(f"Failed to connect to MQTT broker: {error_message}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker"""
        if rc == 0:
            logger.info("Disconnected from MQTT broker")
        else:
            logger.warning(f"Unexpected disconnect from MQTT broker: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for when a message is received from the broker"""
        try:
            logger.debug(f"Received message on topic {msg.topic}: {msg.payload}")
            
            if msg.topic == self.coordinate_topic:
                # Process coordinate message
                payload = msg.payload.decode('utf-8')
                self.coordinate_callback(payload)
        except Exception as e:
            logger.error(f"Error processing MQTT message: {str(e)}")
