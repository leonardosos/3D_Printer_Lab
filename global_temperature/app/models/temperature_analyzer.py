"""
TemperatureAnalyzer: Computes heat level for fan controller based on temperature readings and thresholds.
"""
from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO
from typing import List, Optional
import yaml
import os

class TemperatureAnalyzer:
    def __init__(self, config_path: str = "app/global_temperature_config.yaml", debug: bool = True):
        
        self.debug = debug

        if self.debug:
            print(f"[TEMP_ANALYZER DEBUG] Initializing with config path: {config_path}")

        # load thresholds from YAML config
        self.thresholds = self._load_thresholds_from_yaml(config_path)


    def _load_thresholds_from_yaml(self, path: str) -> dict:
        if os.path.exists(path):
            with open(path, "r") as f:
                # Validate config structure
                try:
                    config = yaml.safe_load(f)
                    
                    room = config["room"]
                    printer = config["printer"]
                    for section in [room, printer]:
                        if "low" not in section or "high" not in section:
                            raise ValueError("Missing 'low' or 'high' in config section")
                        if not isinstance(section["low"], (int, float)) or not isinstance(section["high"], (int, float)):
                            raise ValueError("'low' and 'high' must be numeric")
                        if section["low"] >= section["high"]:
                            raise ValueError("'low' must be less than 'high'")

                    thresholds = {
                        "room": {"low": room["low"], "high": room["high"]},
                        "printer": {"low": printer["low"], "high": printer["high"]}
                    }
                    if self.debug:
                        print(f"[TEMP_ANALYZER DEBUG] Loaded thresholds from {path}: {thresholds}")

                    return thresholds
                except Exception as e:
                    raise ValueError(f"Invalid config file: {e}")
        
    def compute_heat_level(self, room_readings: Optional[List[TemperatureReadingRoomDTO]] = None, printer_readings: Optional[List[TemperatureReadingPrinterDTO]] = None) -> int:
        """
        Computes heat level for fan controller based on latest readings.
        Returns an integer heat level (e.g., 0-10).

        Is computed 70% from room temperature mapping with thresholds, 
        and 30% from mean from the provided printer readings mapping with thresholds.
        If only one type of readings is provided, the heat level depends solely on those readings.
        
        If no readings are provided, returns 0.

        If printers or room readings are not present, the result will be based all on the available readings.
        """

        # Helper to map temperature to 0-10 scale based on thresholds
        def map_to_scale(temp, low, high):
            if temp <= low:
                return 0
            elif temp >= high:
                return 10
            else:
                return int(round((temp - low) / (high - low) * 10))

        room_score = None
        printer_score = None

        # Treat None as empty list
        room_readings = room_readings if room_readings is not None else []
        printer_readings = printer_readings if printer_readings is not None else []

        # Use the latest room reading if available
        if room_readings:
            latest_room_temp = room_readings.temperature
            room_low = self.thresholds["room"]["low"]
            room_high = self.thresholds["room"]["high"]
            room_score = map_to_scale(latest_room_temp, room_low, room_high)
        # Use mean of printer readings if available
        if printer_readings:
            printer_temps = [r.temperature for r in printer_readings]

            if self.debug:
                print(f"[TEMP_ANALYZER DEBUG] Printer temps: {printer_temps}")

            mean_printer_temp = sum(printer_temps) / len(printer_temps)
            printer_low = self.thresholds["printer"]["low"]
            printer_high = self.thresholds["printer"]["high"]
            printer_score = map_to_scale(mean_printer_temp, printer_low, printer_high)

        # Decide final heat level based on available readings
        if room_score is not None and printer_score is not None:
            heat_level = 0.7 * room_score + 0.3 * printer_score
        elif room_score is not None:
            heat_level = room_score
        elif printer_score is not None:
            heat_level = printer_score
        else:
            # No readings provided
            heat_level = 0

        heat_level_int = int(round(heat_level))

        if self.debug:
            if room_score is not None:
                print(f"[TEMP_ANALYZER DEBUG] Room temp: {room_readings.temperature}, mapped: {room_score}")
            if printer_score is not None:
                print(f"[TEMP_ANALYZER DEBUG] Printer mean temp: {mean_printer_temp}, mapped: {printer_score}")
            print(f"[TEMP_ANALYZER DEBUG] Final heat level: {heat_level_int}")

        return heat_level_int


if __name__ == "__main__":
    # Example usage for testing
    #
    # From global_temperature directory:
    #
    #    cd /home/leonardo/iot/IoT_Project/global_temperature
    #    python3 -m app.models.temperature_analyzer
    #
    
    from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
    from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO

    # Create some example readings
    room_readings = [
        TemperatureReadingRoomDTO(temperature=25, sensorId="room1", timestamp=2, unit="C")
    ]
    printer_readings = [
        TemperatureReadingPrinterDTO(temperature=100, printerId="printer1", timestamp=1, unit="C"),
        TemperatureReadingPrinterDTO(temperature=150, printerId="printer2", timestamp=2, unit="C"),
        TemperatureReadingPrinterDTO(temperature=200, printerId="printer3", timestamp=3, unit="C")
    ]

    analyzer = TemperatureAnalyzer()
    heat_level = analyzer.compute_heat_level(printer_readings=printer_readings)
    heat_level = analyzer.compute_heat_level(room_readings=room_readings)
    heat_level = analyzer.compute_heat_level(room_readings=room_readings, printer_readings=printer_readings)
    print(f"Computed heat level: {heat_level}")


