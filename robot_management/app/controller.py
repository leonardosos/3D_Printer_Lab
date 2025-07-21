"""
Robot Controller for managing robot operations.
"""
import json
import logging
import time
import os
from queue import Queue
from typing import Dict, Any, Optional
from datetime import datetime

from .mqtt.client import MQTTClient
from .config import ConfigManager
from .dto.printer_status import PrinterStatusDTO, PrinterItemDTO
from .dto.robot_command import RobotCommandDTO
from .dto.robot_progress import RobotProgressDTO

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('/app/logs', 'robot_management.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RobotController:
    """
    Controller for managing robot operations.
    """
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the RobotController.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.mqtt_config = config_manager.get_mqtt_config()
        
        # Override MQTT broker settings with environment variables if provided
        mqtt_host = os.environ.get('MQTT_BROKER_HOST')
        mqtt_port = os.environ.get('MQTT_BROKER_PORT')
        
        if mqtt_host:
            self.mqtt_config['broker'] = mqtt_host
        if mqtt_port:
            self.mqtt_config['port'] = int(mqtt_port)
            
        logger.info(f"Using MQTT broker at {self.mqtt_config['broker']}:{self.mqtt_config['port']}")
        
        self.service_config = config_manager.config.get("service", {})
        
        # Initialize MQTT client
        self.mqtt_client = MQTTClient(self.mqtt_config)
        
        # Get robot configuration
        self.default_robot_id = config_manager.get_default_robot_id()
        if not self.default_robot_id:
            logger.error("No robots configured. Cannot continue.")
            raise ValueError("No robots configured")
        
        self.robot_config = config_manager.get_robot_by_id(self.default_robot_id)
        self.topics = self.robot_config.get("topics", {})
        
        # Initialize the robot queue
        self.robot_queue = Queue(maxsize=self.service_config.get("queue_size", 100))
        
        # Flag to control processing loop
        self.running = False
        
        # Current task being processed
        self.current_task: Optional[PrinterItemDTO] = None
        self.waiting_for_completion = False
        
    def start(self) -> None:
        """
        Start the robot controller.
        """
        logger.info("Starting Robot Controller")
        
        # Connect to MQTT broker
        if not self.mqtt_client.connect():
            logger.error("Failed to connect to MQTT broker. Exiting.")
            return
        
        # Wait for connection to be established
        if not self.mqtt_client.wait_for_connection():
            logger.error("Timed out waiting for MQTT connection. Exiting.")
            return
        
        # Subscribe to topics
        printer_topic = self.service_config.get("printer_topic", "device/printers")
        progress_topic = self.topics.get("progress", f"device/robot/{self.default_robot_id}/progress")
        
        self.mqtt_client.subscribe(printer_topic, self._handle_printer_status)
        self.mqtt_client.subscribe(progress_topic, self._handle_robot_progress)
        
        # Start processing queue
        self.running = True
        self._process_queue()
        
    def stop(self) -> None:
        """
        Stop the robot controller.
        """
        logger.info("Stopping Robot Controller")
        self.running = False
        self.mqtt_client.disconnect()
        
    def _handle_printer_status(self, topic: str, payload: str) -> None:
        """
        Handle incoming printer status messages.
        
        Args:
            topic: The topic the message was received on
            payload: The message payload
        """
        logger.info(f"Received printer status: {payload}")
        
        # Parse and validate the message
        printer_status = PrinterStatusDTO.from_json(payload)
        if not printer_status:
            logger.error(f"Invalid printer status message: {payload}")
            return
        
        # Get printers with "finish" status
        finished_printers = printer_status.get_finished_printers()
        if not finished_printers:
            logger.info("No printers with 'finish' status")
            return
        
        # Add finished printers to the queue
        for printer in finished_printers:
            try:
                if not self.robot_queue.full():
                    logger.info(f"Adding printer {printer.printer_id} to queue")
                    self.robot_queue.put(printer)
                else:
                    logger.warning("Robot queue is full, cannot add more tasks")
            except Exception as e:
                logger.error(f"Error adding printer to queue: {e}")
    
    def _handle_robot_progress(self, topic: str, payload: str) -> None:
        """
        Handle incoming robot progress messages.
        
        Args:
            topic: The topic the message was received on
            payload: The message payload
        """
        logger.info(f"Received robot progress: {payload}")
        
        # Parse and validate the message
        progress = RobotProgressDTO.from_json(payload)
        if not progress:
            logger.error(f"Invalid robot progress message: {payload}")
            return
        
        # Check if we're waiting for completion
        if not self.waiting_for_completion or not self.current_task:
            logger.info("Received progress update but not waiting for completion")
            return
        
        # Check if this is the progress update for our current task
        if progress.printer_id != self.current_task.printer_id:
            logger.warning(f"Progress update for different printer: {progress.printer_id} vs {self.current_task.printer_id}")
            return
        
        # Check if the task is completed
        if progress.is_completed():
            logger.info(f"Task for printer {progress.printer_id} completed")
            self.waiting_for_completion = False
            self.current_task = None
        elif progress.is_error():
            logger.error(f"Error in task for printer {progress.printer_id}: {payload}")
            # Handle error - could retry or mark as failed
            self.waiting_for_completion = False
            self.current_task = None
    
    def _process_queue(self) -> None:
        """
        Process the robot queue.
        """
        logger.info("Starting queue processing")
        
        while self.running:
            # If we're waiting for a task to complete, don't process the next one
            if self.waiting_for_completion:
                time.sleep(self.service_config.get("processing_interval", 1.0))
                continue
            
            # Check if there are items in the queue
            if self.robot_queue.empty():
                logger.debug("Queue is empty, waiting...")
                time.sleep(self.service_config.get("processing_interval", 1.0))
                continue
            
            # Get the next task from the queue
            try:
                printer = self.robot_queue.get(block=False)
                logger.info(f"Processing task for printer {printer.printer_id}")
                
                # Set as current task
                self.current_task = printer
                
                # Send coordinates to the robot
                success = self._send_robot_to_printer(printer.printer_id)
                if success:
                    # Mark as waiting for completion
                    self.waiting_for_completion = True
                else:
                    # If sending failed, clear current task
                    self.current_task = None
                
                # Mark task as processed
                self.robot_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing queue: {e}")
                time.sleep(1)  # Avoid tight loop in case of error
    
    def _send_robot_to_printer(self, printer_id: str) -> bool:
        """
        Send the robot to a printer's coordinates.
        
        Args:
            printer_id: ID of the printer
            
        Returns:
            True if command was sent successfully, False otherwise
        """
        # Get printer coordinates
        coordinates = self.config_manager.get_printer_coordinates(printer_id)
        if not coordinates:
            logger.error(f"No coordinates found for printer {printer_id}")
            return False
        
        # Create command
        robot_command = RobotCommandDTO(
            robot_id=self.default_robot_id,
            printer_id=printer_id,
            x=coordinates["x"],
            y=coordinates["y"],
            z=coordinates["z"],
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        
        # Send command
        try:
            coordinates_topic = self.topics.get("coordinates", f"device/robot/{self.default_robot_id}/coordinates")
            self.mqtt_client.publish(coordinates_topic, robot_command.to_json())
            logger.info(f"Sent robot command for printer {printer_id}: {robot_command.to_json()}")
            return True
        except Exception as e:
            logger.error(f"Error sending robot command: {e}")
            return False
