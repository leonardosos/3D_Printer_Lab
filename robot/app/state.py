"""
State machine for tracking the robot's current state.
"""
import logging
from enum import Enum, auto

logger = logging.getLogger("RobotState")

class State(Enum):
    """Enum representing possible robot states"""
    IDLE = auto()          # Robot is idle, waiting for commands
    NAVIGATING = auto()    # Robot is moving to a target position
    PICKING = auto()       # Robot is picking up a printed object
    TRANSPORTING = auto()  # Robot is transporting an object to the unloading area
    RETURNING = auto()     # Robot is returning to home position

class RobotState:
    """
    State machine for the robot device.
    Tracks current state and manages valid state transitions.
    """
    
    def __init__(self):
        """Initialize the robot state to IDLE"""
        self.current_state = State.IDLE
        logger.info(f"Initial state: {self.current_state}")
        
        # Define valid state transitions
        self.valid_transitions = {
            State.IDLE: [State.NAVIGATING],
            State.NAVIGATING: [State.PICKING],
            State.PICKING: [State.TRANSPORTING, State.IDLE],  # Can go back to IDLE in case of error
            State.TRANSPORTING: [State.RETURNING, State.IDLE],  # Can go back to IDLE in case of error
            State.RETURNING: [State.IDLE]
        }
    
    def set_state(self, new_state: State) -> bool:
        """
        Attempt to transition to a new state.
        
        Args:
            new_state: The state to transition to
            
        Returns:
            bool: True if transition was successful, False otherwise
        """
        # Check if the transition is valid
        if new_state in self.valid_transitions.get(self.current_state, []):
            old_state = self.current_state
            self.current_state = new_state
            logger.info(f"State changed: {old_state} -> {new_state}")
            return True
        else:
            # Special case: We always allow transition to IDLE for error recovery
            if new_state == State.IDLE:
                old_state = self.current_state
                self.current_state = new_state
                logger.warning(f"Forced state reset: {old_state} -> {new_state}")
                return True
            
            logger.warning(f"Invalid state transition: {self.current_state} -> {new_state}")
            return False
    
    def is_idle(self) -> bool:
        """Check if the robot is in the IDLE state"""
        return self.current_state == State.IDLE
