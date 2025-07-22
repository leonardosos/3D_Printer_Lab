import yaml
import logging
import os

class ConfigManager:
    """Handles loading and providing access to configuration values"""
    
    def __init__(self, config_path="config/config.yaml"):
        """Initialize the config manager with the path to the config file"""
        self.config_path = config_path
        self.config = None
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            if not os.path.exists(self.config_path):
                self.logger.error(f"Config file not found at {self.config_path}")
                raise FileNotFoundError(f"Config file not found at {self.config_path}")
            
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
                
            self._setup_logging()
            self.logger.info("Configuration loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            raise
    
    def _setup_logging(self):
        """Configure logging based on configuration"""
        if self.config and 'logging' in self.config:
            log_level = self.config['logging'].get('level', 'INFO')
            numeric_level = getattr(logging, log_level.upper(), None)
            if isinstance(numeric_level, int):
                logging.basicConfig(
                    level=numeric_level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
    
    def get_sensor_config(self):
        """Get sensor configuration"""
        if not self.config:
            self.load_config()
        return self.config.get('sensor', {})
    
    def get_mqtt_config(self):
        """Get MQTT configuration"""
        if not self.config:
            self.load_config()
        return self.config.get('mqtt', {})
