"""
Configuration loader for the Robot Device Microservice.
Loads configuration from environment variables and YAML file.
"""
import os
import logging
import yaml
from typing import Dict, Any, Tuple

logger = logging.getLogger("ConfigLoader")

class ConfigLoader:
    """
    Loads and validates configuration from environment variables and YAML file.
    Environment variables take precedence over YAML configuration.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_file: Path to the YAML configuration file (optional)
                         If not provided, will look for config.yaml in the same directory
        """
        # Default configuration values
        self.defaults = {
            "robot": {
                "id": "rob-1",
                "home_position": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "unloading_area": {
                    "x": 500,
                    "y": 500,
                    "z": 50
                }
            },
            "mqtt": {
                "broker_host": "broker",
                "broker_port": 1883,
                "qos": 0,
                "client_id": "robot-client"
            }
        }
        
        # Load configuration from YAML file
        if config_file is None:
            # Use default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(current_dir, "config.yaml")
        
        self.config = self._load_yaml_config(config_file)
        
        # Override with environment variables
        self._apply_env_overrides()
        
        # Extract commonly used values as properties
        self._extract_properties()
        
        logger.info("Configuration loaded successfully")
    
    def _load_yaml_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_file: Path to YAML configuration file
            
        Returns:
            Dict containing the merged configuration (defaults + YAML)
        """
        config = self.defaults.copy()
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as file:
                    yaml_config = yaml.safe_load(file)
                
                if yaml_config:
                    # Merge with defaults (shallow merge for now)
                    for section, values in yaml_config.items():
                        if section in config:
                            config[section].update(values)
                        else:
                            config[section] = values
                
                logger.info(f"Loaded configuration from {config_file}")
            else:
                logger.warning(f"Configuration file {config_file} not found, using defaults")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_file}: {e}")
        
        return config
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to the configuration"""
        # Robot ID
        if os.environ.get("ROBOT_ID"):
            self.config["robot"]["id"] = os.environ.get("ROBOT_ID")
        
        # MQTT settings
        if os.environ.get("MQTT_BROKER_HOST"):
            self.config["mqtt"]["broker_host"] = os.environ.get("MQTT_BROKER_HOST")
        
        if os.environ.get("MQTT_BROKER_PORT"):
            try:
                self.config["mqtt"]["broker_port"] = int(os.environ.get("MQTT_BROKER_PORT"))
            except ValueError:
                logger.warning("Invalid MQTT_BROKER_PORT, using default")
        
        # Home position
        if os.environ.get("HOME_X"):
            try:
                self.config["robot"]["home_position"]["x"] = float(os.environ.get("HOME_X"))
            except ValueError:
                logger.warning("Invalid HOME_X, using default")
        
        if os.environ.get("HOME_Y"):
            try:
                self.config["robot"]["home_position"]["y"] = float(os.environ.get("HOME_Y"))
            except ValueError:
                logger.warning("Invalid HOME_Y, using default")
        
        if os.environ.get("HOME_Z"):
            try:
                self.config["robot"]["home_position"]["z"] = float(os.environ.get("HOME_Z"))
            except ValueError:
                logger.warning("Invalid HOME_Z, using default")
    
    def _extract_properties(self) -> None:
        """Extract commonly used configuration values as properties"""
        # Robot properties
        self.robot_id = self.config["robot"]["id"]
        
        # Home position as a tuple
        home = self.config["robot"]["home_position"]
        self.home_position = (home["x"], home["y"], home["z"])
        
        # Unloading area as a tuple
        unload = self.config["robot"]["unloading_area"]
        self.unloading_area = (unload["x"], unload["y"], unload["z"])
        
        # MQTT properties
        self.mqtt_host = self.config["mqtt"]["broker_host"]
        self.mqtt_port = self.config["mqtt"]["broker_port"]
        self.mqtt_qos = self.config["mqtt"]["qos"]
    
    def get(self, section: str, key: str, default=None) -> Any:
        """
        Get a configuration value by section and key.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found
            
        Returns:
            The configuration value or default
        """
        return self.config.get(section, {}).get(key, default)
