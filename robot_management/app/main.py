"""
Main entry point for the Robot Management microservice.
"""
import os
import sys
import signal
import logging
import time
from typing import Optional

from .config import ConfigManager
from .controller import RobotController

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global controller instance for signal handling
controller: Optional[RobotController] = None


def signal_handler(sig, frame) -> None:
    """
    Handle signals (e.g., SIGINT, SIGTERM) for graceful shutdown.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {sig}, shutting down...")
    if controller:
        controller.stop()
    sys.exit(0)


def main() -> None:
    """
    Main function to start the Robot Management microservice.
    """
    global controller
    
    logger.info("Starting Robot Management microservice")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load configuration
        config_path = os.environ.get('CONFIG_PATH')
        config_manager = ConfigManager(config_path)
        
        # Create and start robot controller
        controller = RobotController(config_manager)
        controller.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        if controller:
            controller.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
