"""
MQTT client for the Robot Device Microservice.
Handles connection to broker, subscriptions, and publications.
"""
import logging
import json
import paho.mqtt.client as mqtt
from typing import Optional, Callable, Any

from .dto.coordinate_dto import CoordinateDTO
from .dto.progress_dto import ProgressDTO

logger = logging.getLogger("MQTTClient")

class MQTTClient:
    """
    MQTT client for handling message exchange between the robot and the broker.
    Subscribes to coordinate commands and publishes progress updates.
    """
    
    def __init__(self, client_id: str, broker_host: str, broker_port: int, 
                 robot_id: str, controller: Any, qos: int = 0):
        """
        Initialize the MQTT client.
        
        Args:
            client_id: Unique identifier for this MQTT client
            broker_host: Hostname or IP of the MQTT broker
            broker_port: Port number of the MQTT broker
            robot_id: Unique identifier for the robot
            controller: Reference to the RobotController for callbacks
            qos: Quality of Service level for MQTT messages
        """
        self.client_id = client_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.robot_id = robot_id
        self.controller = controller
        self.qos = qos
        self.client = None
        self.is_connected = False
        
        # Topic patterns
        self.coordinate_topic = f"device/robot/{robot_id}/coordinates"
        self.progress_topic = f"device/robot/{robot_id}/progress"
        
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to the MQTT broker and set up callbacks"""
        try:
            self.client = mqtt.Client(client_id=self.client_id)
            
            # Set up callbacks
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            
            # Connect to broker
            self.client.connect(self.broker_host, self.broker_port)
            
            # Start the loop in a separate thread
            self.client.loop_start()
            
            logger.info(f"MQTT client initialized, connecting to {self.broker_host}:{self.broker_port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    def _on_connect(self, client, userdata, flags, rc) -> None:
        """
        Callback for when the client connects to the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data from client setup
            flags: Response flags from broker
            rc: Result code of the connection
        """
        if rc == 0:
            self.is_connected = True
            logger.info(f"Connected to MQTT broker with result code {rc}")
            
            # Subscribe to the coordinate topic
            self.client.subscribe(self.coordinate_topic, qos=self.qos)
            logger.info(f"Subscribed to topic: {self.coordinate_topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with result code {rc}")
    
    def _on_message(self, client, userdata, msg) -> None:
        """
        Callback for when a message is received from the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data from client setup
            msg: The message object containing topic and payload
        """
        try:
            logger.debug(f"Received message on topic {msg.topic}: {msg.payload}")
            
            if msg.topic == self.coordinate_topic:
                # Parse the coordinate command
                payload = msg.payload.decode('utf-8')
                coordinate_dto = CoordinateDTO.from_json(payload)
                
                # Verify the robot ID matches
                if coordinate_dto.robot_id != self.robot_id:
                    logger.warning(f"Received message for robot {coordinate_dto.robot_id}, but this is {self.robot_id}")
                    return
                
                # Forward to the controller
                self.controller.handle_coordinate_command(coordinate_dto)
            else:
                logger.warning(f"Received message on unexpected topic: {msg.topic}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _on_disconnect(self, client, userdata, rc) -> None:
        """
        Callback for when the client disconnects from the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data from client setup
            rc: Result code of the disconnection
        """
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection with code {rc}. Attempting to reconnect...")
            try:
                self.client.reconnect()
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}")
        else:
            logger.info("MQTT client disconnected successfully")
    
    def publish_progress(self, progress_dto: ProgressDTO) -> bool:
        """
        Publish a progress update message.
        
        Args:
            progress_dto: ProgressDTO containing the update details
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Cannot publish: MQTT client not connected")
            return False
        
        try:
            payload = progress_dto.to_json()
            result = self.client.publish(self.progress_topic, payload, qos=self.qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published progress update: {progress_dto.action} - {progress_dto.status}")
                return True
            else:
                logger.error(f"Failed to publish progress update: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing progress update: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the MQTT broker and clean up resources"""
        if self.client and self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT client disconnected")
