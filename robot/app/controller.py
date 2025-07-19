"""
Robot Controller for managing the robot's workflow and state.
"""
import logging
import time
from typing import Optional, Dict, Any, Tuple

from .dto.coordinate_dto import CoordinateDTO
from .dto.progress_dto import ProgressDTO
from .state import RobotState, State
from .config import ConfigLoader

logger = logging.getLogger("RobotController")

class RobotController:
    """
    Main controller for the robot device. Handles the workflow:
    1. Receive coordinate command
    2. Navigate to printer
    3. Pick up the printed object
    4. Transport to unloading area
    5. Return to home position
    """
    
    def __init__(self, config: ConfigLoader):
        """
        Initialize the robot controller.
        
        Args:
            config: Configuration loader with robot settings
        """
        self.config = config
        self.state = RobotState()
        self.mqtt_client = None
        self.current_printer_id = None
        
        # Extract configuration
        self.robot_id = config.robot_id
        self.home_position = config.home_position
        self.unloading_area = config.unloading_area
        
        # Default speed (mm/s) if not specified in command
        self.default_speed = 100
        
        logger.info(f"Robot controller initialized for robot {self.robot_id}")
        logger.info(f"Home position: {self.home_position}")
        logger.info(f"Unloading area: {self.unloading_area}")
    
    def set_mqtt_client(self, mqtt_client) -> None:
        """
        Set the MQTT client for publishing progress updates.
        
        Args:
            mqtt_client: MQTT client instance
        """
        self.mqtt_client = mqtt_client
    
    def handle_coordinate_command(self, coordinate_dto: CoordinateDTO) -> None:
        """
        Process a coordinate command and execute the robot workflow.
        
        Args:
            coordinate_dto: Validated coordinate command
        """
        # Check if the robot is available
        if self.state.current_state != State.IDLE:
            logger.warning(f"Received command while in {self.state.current_state} state. Command ignored.")
            return
        
        logger.info(f"Handling coordinate command for printer {coordinate_dto.printer_id}")
        
        # Store printer ID for progress reporting
        self.current_printer_id = coordinate_dto.printer_id
        
        # Extract target coordinates and optional speed
        target = (coordinate_dto.x, coordinate_dto.y, coordinate_dto.z)
        speed = coordinate_dto.speed or self.default_speed
        
        # Execute the workflow as a sequence of operations
        try:
            # 1. Navigate to printer
            self._navigate_to_coordinates(target, speed)
            
            # 2. Pick up the printed object
            self._pick_object()
            
            # 3. Transport to unloading area
            self._transport_to_unloading_area(speed)
            
            # 4. Return to home position
            self._return_to_home(speed)
            
            # 5. Publish final completion status
            self._publish_progress("idle", "completed")
            
            logger.info("Workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Error during workflow execution: {e}")
            self._publish_progress("idle", "error")
            # Reset state to idle
            self.state.set_state(State.IDLE)
    
    def _navigate_to_coordinates(self, target: Tuple[float, float, float], speed: float) -> None:
        """
        Simulate navigating to the specified coordinates.
        
        Args:
            target: (x, y, z) coordinates in mm
            speed: Movement speed in mm/s
        """
        self.state.set_state(State.NAVIGATING)
        logger.info(f"Navigating to coordinates: {target} at speed {speed} mm/s")
        
        # Calculate distance to target (simplified)
        current_pos = self.home_position
        distance = ((target[0] - current_pos[0])**2 + 
                   (target[1] - current_pos[1])**2 + 
                   (target[2] - current_pos[2])**2)**0.5
        
        # Calculate travel time based on distance and speed
        travel_time = distance / speed
        
        # Simulate movement with sleep
        logger.info(f"Moving... (estimated time: {travel_time:.2f} seconds)")
        time.sleep(min(travel_time, 5))  # Cap simulation time for faster testing
        
        logger.info(f"Reached target coordinates: {target}")
    
    def _pick_object(self) -> None:
        """Simulate picking up a printed object from the printer"""
        self.state.set_state(State.PICKING)
        logger.info("Picking up the printed object")
        
        # Simulate picking action
        time.sleep(2)
        
        logger.info("Object picked successfully")
    
    def _transport_to_unloading_area(self, speed: float) -> None:
        """
        Simulate transporting the object to the unloading area.
        
        Args:
            speed: Movement speed in mm/s
        """
        self.state.set_state(State.TRANSPORTING)
        logger.info(f"Transporting object to unloading area: {self.unloading_area}")
        
        # Calculate distance to unloading area (simplified)
        current_pos = (0, 0, 0)  # Assuming we're at the printer position
        unloading_pos = self.unloading_area
        distance = ((unloading_pos[0] - current_pos[0])**2 + 
                   (unloading_pos[1] - current_pos[1])**2 + 
                   (unloading_pos[2] - current_pos[2])**2)**0.5
        
        # Calculate travel time based on distance and speed
        travel_time = distance / speed
        
        # Simulate movement with sleep
        logger.info(f"Moving to unloading area... (estimated time: {travel_time:.2f} seconds)")
        time.sleep(min(travel_time, 5))  # Cap simulation time for faster testing
        
        # Simulate placing object in unloading area
        self._publish_progress("place", "in_progress")
        time.sleep(1)
        self._publish_progress("place", "completed")
        
        logger.info("Object placed in unloading area")
    
    def _return_to_home(self, speed: float) -> None:
        """
        Simulate returning to the home position.
        
        Args:
            speed: Movement speed in mm/s
        """
        self.state.set_state(State.RETURNING)
        logger.info(f"Returning to home position: {self.home_position}")
        
        # Calculate distance to home (simplified)
        current_pos = self.unloading_area
        home_pos = self.home_position
        distance = ((home_pos[0] - current_pos[0])**2 + 
                   (home_pos[1] - current_pos[1])**2 + 
                   (home_pos[2] - current_pos[2])**2)**0.5
        
        # Calculate travel time based on distance and speed
        travel_time = distance / speed
        
        # Simulate movement with sleep
        logger.info(f"Moving to home... (estimated time: {travel_time:.2f} seconds)")
        time.sleep(min(travel_time, 3))  # Cap simulation time for faster testing
        
        # Set state back to idle
        self.state.set_state(State.IDLE)
        logger.info("Returned to home position")
    
    def _publish_progress(self, action: str, status: str) -> None:
        """
        Publish a progress update via MQTT.
        
        Args:
            action: Current action ("pick", "place", "idle")
            status: Status of the action ("in_progress", "completed", "error")
        """
        if not self.mqtt_client:
            logger.warning("Cannot publish progress: MQTT client not set")
            return
        
        if not self.current_printer_id:
            logger.warning("Cannot publish progress: No printer ID set")
            return
        
        progress = ProgressDTO(
            robot_id=self.robot_id,
            printer_id=self.current_printer_id,
            action=action,
            status=status
        )
        
        self.mqtt_client.publish_progress(progress)

