import logging
import time
import signal
import sys
from .config_manager import ConfigManager
from .sensor import SensorSimulator
from .mqtt_client import MQTTClient

class Application:
    """Main application that coordinates all components"""
    
    def __init__(self):
        """Initialize the application"""
        # Setup basic logging until we load the config
        logging.basicConfig(level=logging.INFO,
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.config_manager = ConfigManager()
        self.sensor = None
        self.mqtt_client = None
        self.running = False
    
    def initialize(self):
        """Initialize all components based on configuration"""
        self.logger.info("Initializing application...")
        
        # Load configuration
        try:
            self.config_manager.load_config()
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return False
        
        # Initialize sensor
        sensor_config = self.config_manager.get_sensor_config()
        self.sensor = SensorSimulator(
            sensor_id=sensor_config.get('id', 'room-sensor-1'),
            min_temp=sensor_config.get('min_temperature', 11.0),
            max_temp=sensor_config.get('max_temperature', 49.0)
        )
        
        # Initialize MQTT client
        mqtt_config = self.config_manager.get_mqtt_config()
        self.mqtt_client = MQTTClient(
            sensor_id=sensor_config.get('id', 'room-sensor-1'),
            broker_host=mqtt_config.get('broker_host', 'localhost'),
            broker_port=mqtt_config.get('broker_port', 1883),
            topic=mqtt_config.get('topic', 'device/room/temperature')
        )
        
        # Connect to MQTT broker
        if not self.mqtt_client.connect():
            self.logger.error("Failed to connect to MQTT broker, aborting")
            return False
        
        self.logger.info("Application initialized successfully")
        return True
    
    def run(self):
        """Run the main application loop"""
        if not self.initialize():
            self.logger.error("Initialization failed, exiting")
            return
        
        self.running = True
        self.logger.info("Starting main application loop")
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        sensor_config = self.config_manager.get_sensor_config()
        update_interval = sensor_config.get('update_interval_seconds', 5)
        
        try:
            while self.running:
                # Get sensor reading
                reading = self.sensor.get_reading()
                
                # Publish to MQTT
                if not self.mqtt_client.publish(reading):
                    self.logger.warning("Failed to publish message, will retry on next cycle")
                
                # Wait for next update cycle
                time.sleep(update_interval)
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {str(e)}")
        
        finally:
            self.shutdown()
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals"""
        self.logger.info(f"Received signal {sig}, shutting down")
        self.running = False
    
    def shutdown(self):
        """Perform cleanup and shutdown"""
        self.logger.info("Shutting down application")
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        self.logger.info("Shutdown complete")

if __name__ == "__main__":
    app = Application()
    app.run()
