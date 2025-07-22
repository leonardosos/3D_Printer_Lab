import random
import logging
import time
from datetime import datetime

class SensorSimulator:
    """Simulates a temperature sensor with realistic behavior"""
    
    def __init__(self, sensor_id="room-sensor-1", min_temp=11.0, max_temp=49.0):
        """Initialize the temperature sensor simulator"""
        self.sensor_id = sensor_id
        self.min_temperature = min_temp
        self.max_temperature = max_temp
        self.unit = "C"  # Celsius is fixed per requirements
        
        # Start with a random comfortable room temperature
        self.current_temperature = random.uniform(18.0, 25.0)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Sensor {self.sensor_id} initialized with temperature: {self.current_temperature:.1f}°C")
        
        # Inertia factor to prevent unrealistic rapid changes
        self.temperature_trend = 0  # -1 cooling, 0 stable, 1 warming
        
    def read_temperature(self):
        """Generate a new temperature reading with realistic changes"""
        # Randomly decide to change direction sometimes
        if random.random() < 0.3:
            self.temperature_trend = random.choice([-1, 0, 1])
        
        # Calculate temperature change (smaller changes are more likely)
        change_magnitude = random.triangular(0.1, 0.5, 0.2)
        
        # Apply the change in the trend direction
        if self.temperature_trend == 1:
            self.current_temperature += change_magnitude
        elif self.temperature_trend == -1:
            self.current_temperature -= change_magnitude
        
        # Ensure temperature stays within bounds
        self.current_temperature = max(self.min_temperature, 
                                     min(self.max_temperature, 
                                         self.current_temperature))
        
        # Round to 1 decimal place for realistic sensor precision
        self.current_temperature = round(self.current_temperature, 1)
        
        self.logger.debug(f"New temperature reading: {self.current_temperature}°C")
        return self.current_temperature
    
    def get_reading(self):
        """Return a complete sensor reading with all metadata"""
        return {
            "sensorId": self.sensor_id,
            "temperature": self.read_temperature(),
            "unit": self.unit,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
