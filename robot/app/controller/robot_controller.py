"""
Robot controller that manages the robot's operations and state.
"""
import logging
import threading
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

from app.dto.coordinate_dto import CoordinateDTO
from app.dto.progress_dto import ProgressDTO, RobotAction, ActionStatus
from app.service.mqtt_service import MqttService
from app.service.path_planner import PathPlanner, Point3D
from app.utils.validators import validate_coordinate_message

logger = logging.getLogger('robot')

@dataclass
class RobotState:
    """Class to maintain the robot's current state"""
    position: Point3D
    current_action: str = RobotAction.IDLE.value
    status: str = ActionStatus.COMPLETED.value
    printer_id: Optional[str] = None

class RobotController:
    """
    Controls the robot's operations and manages its state.
    This class is responsible for handling coordinate commands,
    planning paths, executing movements, and reporting status.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the robot controller.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.robot_id = config['robot']['id']
        
        # Initialize state with home position
        home_pos = config['robot']['home_position']
        self.state = RobotState(
            position=Point3D(home_pos['x'], home_pos['y'], home_pos['z']),
            current_action=RobotAction.IDLE.value,
            status=ActionStatus.COMPLETED.value
        )
        
        # Initialize services
        self.mqtt_service = MqttService(config, self.handle_coordinate_message)
        self.path_planner = PathPlanner(
            default_speed=config['robot']['default_speed'],
            max_speed=config['robot']['max_speed'],
            acceleration=config['robot']['acceleration']
        )
        
        # Flag to indicate if the robot is busy
        self.busy = False
        self.busy_lock = threading.Lock()
    
    def initialize(self):
        """Initialize the robot and connect to services"""
        logger.info(f"Initializing robot {self.robot_id}")
        # Connect to MQTT broker
        self.mqtt_service.connect()
        # Subscribe to coordinate topic
        self.mqtt_service.subscribe()
        logger.info(f"Robot {self.robot_id} initialized and ready")
    
    def shutdown(self):
        """Shutdown the robot and disconnect from services"""
        logger.info(f"Shutting down robot {self.robot_id}")
        self.mqtt_service.disconnect()
    
    def handle_coordinate_message(self, payload: str):
        """
        Handle incoming coordinate messages from MQTT.
        
        Args:
            payload: JSON string with coordinate data
        """
        try:
            # Check if robot is busy
            with self.busy_lock:
                if self.busy:
                    logger.warning(f"Robot {self.robot_id} is busy. Ignoring new coordinate command.")
                    return
                self.busy = True
            
            # Validate and parse the message
            logger.info(f"Received coordinate message: {payload}")
            coordinate_dto = validate_coordinate_message(payload, self.robot_id)
            
            # Execute the robot operation in a separate thread
            threading.Thread(
                target=self.execute_operation,
                args=(coordinate_dto,),
                daemon=True
            ).start()
            
        except ValueError as e:
            logger.error(f"Error processing coordinate message: {str(e)}")
            with self.busy_lock:
                self.busy = False
        except Exception as e:
            logger.error(f"Unexpected error handling coordinate message: {str(e)}", exc_info=True)
            with self.busy_lock:
                self.busy = False
    
    def execute_operation(self, coordinate_dto: CoordinateDTO):
        """
        Execute the full robot operation based on the coordinate command.
        
        Args:
            coordinate_dto: The coordinate command DTO
        """
        try:
            # Store the printer ID for later use in progress messages
            self.state.printer_id = coordinate_dto.printerId
            
            # 1. Move to printer location
            target = Point3D(coordinate_dto.x, coordinate_dto.y, coordinate_dto.z)
            speed = coordinate_dto.speed or self.config['robot']['default_speed']
            self.move_to_position(target, speed)
            
            # 2. Pick up the object
            self.perform_pick_operation()
            
            # 3. Move to unloading area
            unload_area = self.config['robot']['unloading_area']
            unload_pos = Point3D(unload_area['x'], unload_area['y'], unload_area['z'])
            self.move_to_position(unload_pos, speed)
            
            # 4. Place the object
            self.perform_place_operation()
            
            # 5. Return to home position
            home_pos = self.config['robot']['home_position']
            home = Point3D(home_pos['x'], home_pos['y'], home_pos['z'])
            self.move_to_position(home, speed)
            
            # 6. Publish completion message
            self.publish_completion_message()
            
        except Exception as e:
            logger.error(f"Error during robot operation: {str(e)}", exc_info=True)
        finally:
            # Reset busy flag
            with self.busy_lock:
                self.busy = False
    
    def move_to_position(self, target: Point3D, speed: int):
        """
        Move the robot to the target position.
        
        Args:
            target: Target position
            speed: Movement speed
        """
        logger.info(f"Moving robot to position: ({target.x}, {target.y}, {target.z}) at speed {speed}")
        
        # Calculate path
        path = self.path_planner.calculate_path(self.state.position, target)
        
        # Simulate movement (in a real system, this would control motors)
        for waypoint in path:
            # Update robot position
            self.state.position = waypoint
            
            # In a real system, we'd wait for the robot to reach this position
            # Here we'll just sleep to simulate movement time
            time.sleep(0.1)  # 100ms per waypoint
        
        logger.info(f"Robot arrived at position: ({target.x}, {target.y}, {target.z})")
    
    def perform_pick_operation(self):
        """Perform the pick operation to retrieve an object from a printer"""
        logger.info(f"Performing pick operation at printer {self.state.printer_id}")
        
        # Simulate the pick operation
        time.sleep(2)  # 2 second operation time
        
        logger.info("Pick operation completed")
    
    def perform_place_operation(self):
        """Perform the place operation to deposit an object at the unloading area"""
        logger.info("Performing place operation at unloading area")
        
        # Simulate the place operation
        time.sleep(1.5)  # 1.5 second operation time
        
        logger.info("Place operation completed")
    
    def publish_completion_message(self):
        """Publish a message indicating the robot has completed its operation and is idle"""
        if not self.state.printer_id:
            logger.warning("Cannot publish completion message: printer ID is missing")
            return
            
        # Create completion message
        progress_dto = ProgressDTO.create_completion_message(
            robot_id=self.robot_id,
            printer_id=self.state.printer_id
        )
        
        # Publish the message
        self.mqtt_service.publish_progress(progress_dto)
        logger.info(f"Published completion message for printer {self.state.printer_id}")
