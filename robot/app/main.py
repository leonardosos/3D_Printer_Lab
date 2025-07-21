#!/usr/bin/env python3
"""
Entry point for the Robot Device Microservice.
Initializes all components and starts the application.
"""
import logging
import time
import signal
import sys
from typing import Optional

from .config import ConfigLoader
from .controller import RobotController
from .mqtt_client import MQTTClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RobotMain")

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle termination signals for graceful shutdown"""
    global running
    logger.info("Shutdown signal received, stopping services...")
    running = False

def main():
    """Main entry point for the robot microservice"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    logger.info("Loading configuration...")
    config = ConfigLoader()
    
    # Create robot controller
    logger.info(f"Initializing robot controller with ID: {config.robot_id}")
    controller = RobotController(config)
    
    # Create and connect MQTT client
    logger.info(f"Connecting to MQTT broker at {config.mqtt_host}:{config.mqtt_port}")
    mqtt_client = MQTTClient(
        client_id=f"{config.robot_id}-client",
        broker_host=config.mqtt_host,
        broker_port=config.mqtt_port,
        robot_id=config.robot_id,
        controller=controller,
        qos=config.mqtt_qos
    )
    
    # Connect controller to MQTT client for publishing progress
    controller.set_mqtt_client(mqtt_client)
    
    try:
        # Main loop
        logger.info("Robot microservice started and waiting for commands")
        while running:
            time.sleep(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Clean shutdown
        logger.info("Shutting down robot microservice")
        mqtt_client.disconnect()
        sys.exit(0)

if __name__ == "__main__":
    main()
