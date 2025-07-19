"""
Main entry point for the Robot microservice.
Initializes and runs the robot controller.
"""
import logging
import os
import signal
import sys
import time
import yaml
from logging.handlers import RotatingFileHandler

from app.controller.robot_controller import RobotController

# Configure logging
def setup_logging():
    """Set up logging configuration"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger('robot')
    logger.setLevel(logging.INFO)
    
    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'robot.log'),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def load_config():
    """Load configuration from YAML file and environment variables"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'robot_config.yaml')
    
    # Load config from file
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Override with environment variables
    if 'ROBOT_ID' in os.environ:
        config['robot']['id'] = os.environ['ROBOT_ID']
    
    if 'MQTT_BROKER_HOST' in os.environ:
        config['mqtt']['broker_host'] = os.environ['MQTT_BROKER_HOST']
    
    if 'MQTT_BROKER_PORT' in os.environ:
        config['mqtt']['broker_port'] = int(os.environ['MQTT_BROKER_PORT'])
    
    # Set home position from environment variables if provided
    if 'HOME_X' in os.environ:
        config['robot']['home_position']['x'] = float(os.environ['HOME_X'])
    
    if 'HOME_Y' in os.environ:
        config['robot']['home_position']['y'] = float(os.environ['HOME_Y'])
    
    if 'HOME_Z' in os.environ:
        config['robot']['home_position']['z'] = float(os.environ['HOME_Z'])
    
    return config

def main():
    """Main function to run the robot service"""
    logger = setup_logging()
    logger.info("Starting Robot Service")
    
    try:
        # Load configuration
        config = load_config()
        logger.info(f"Loaded configuration for robot ID: {config['robot']['id']}")
        
        # Create and initialize robot controller
        controller = RobotController(config)
        controller.initialize()
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received")
            controller.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep the service running
        logger.info("Robot service running. Press CTRL+C to exit.")
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in robot service: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
