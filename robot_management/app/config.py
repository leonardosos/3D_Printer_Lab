"""
Configuration manager for the Robot Management microservice.
"""
import os
import yaml
from typing import Dict, List, Any, Optional


class ConfigManager:
    """
    Manages configuration for the Robot Management microservice.
    Loads configuration from a YAML file and provides access to configuration values.
    """
    def __init__(self, config_file: str = None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_file: Path to the configuration file. If None, uses the default.
        """
        if config_file is None:
            # Default config file path
            self.config_file = os.path.join(os.path.dirname(__file__), 'config.yaml')
        else:
            self.config_file = config_file
            
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the YAML file.
        
        Returns:
            Dict containing configuration values.
        """
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Return basic default config
            return {
                "mqtt": {
                    "broker": "localhost",
                    "port": 1883
                },
                "robots": [],
                "printers": []
            }
    
    def get_mqtt_config(self) -> Dict[str, Any]:
        """
        Get MQTT broker configuration.
        
        Returns:
            Dict with broker address and port.
        """
        return self.config.get("mqtt", {"broker": "localhost", "port": 1883})
    
    def get_robots(self) -> List[Dict[str, Any]]:
        """
        Get list of configured robots.
        
        Returns:
            List of robot configurations.
        """
        return self.config.get("robots", [])
    
    def get_robot_by_id(self, robot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific robot.
        
        Args:
            robot_id: ID of the robot.
            
        Returns:
            Robot configuration or None if not found.
        """
        robots = self.get_robots()
        for robot in robots:
            if robot.get("id") == robot_id:
                return robot
        return None
    
    def get_printers(self) -> List[Dict[str, Any]]:
        """
        Get list of configured printers.
        
        Returns:
            List of printer configurations.
        """
        return self.config.get("printers", [])
    
    def get_printer_by_id(self, printer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific printer.
        
        Args:
            printer_id: ID of the printer.
            
        Returns:
            Printer configuration or None if not found.
        """
        printers = self.get_printers()
        for printer in printers:
            if printer.get("id") == printer_id:
                return printer
        return None
    
    def get_printer_coordinates(self, printer_id: str) -> Optional[Dict[str, int]]:
        """
        Get coordinates for a specific printer.
        
        Args:
            printer_id: ID of the printer.
            
        Returns:
            Dict with x, y, z coordinates or None if printer not found.
        """
        printer = self.get_printer_by_id(printer_id)
        if printer and "coordinates" in printer:
            return printer["coordinates"]
        return None
    
    def get_default_robot_id(self) -> Optional[str]:
        """
        Get the ID of the default robot (first one in the configuration).
        
        Returns:
            Robot ID or None if no robots configured.
        """
        robots = self.get_robots()
        if robots:
            return robots[0].get("id")
        return None
