from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO
import yaml
import os
from app.models.emergency_model import EmergencyAlert
from datetime import datetime

# input: TemperatureReadingPrinterDTO or TemperatureReadingRoomDTO
#       - for thresholds: 1 value
#       - for rate: 2 values
#
# output: EmergencyAlert (internal data model) or None

class TemperatureAnalyzer:
    def __init__(self, config_path: str = 'app/anomaly_detection_config.yaml', debug: bool = False):
        self.debug = debug

        self.room_max_threshold = 50
        self.printer_max_threshold = 300
        self.printer_max_rate = 100
        self.room_max_rate = 10

        # Load thresholds from YAML config if provided
        self.thresholds = self._load_thresholds_from_yaml(config_path)


    def _load_thresholds_from_yaml(self, path: str):
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    config = yaml.safe_load(f)
                    # Validate config structure
                    for section in ['room', 'printer']:
                        if section not in config:
                            raise ValueError(f"Missing '{section}' section in config")
                        if 'high' not in config[section]:
                            raise ValueError(f"Missing 'high' in '{section}' section")
                        if not isinstance(config[section]['high'], (int, float)):
                            raise ValueError(f"'high' in '{section}' must be numeric")
                    
                    if self.debug:
                        print(f"[TEMP_ANALYZER DEBUG] Loaded thresholds from {path}: {config}")
                    return config
                except Exception as e:
                    raise ValueError(f"Invalid config file: {e}")
        raise FileNotFoundError(f"Config file not found: {path}")

    def check_thresholds(self, reading: TemperatureReadingPrinterDTO | TemperatureReadingRoomDTO) -> EmergencyAlert | None:
        # Check if reading exceeds thresholds
        if isinstance(reading, TemperatureReadingPrinterDTO):
            temp = reading.temperature

            if temp > self.printer_max_threshold:
                if self.debug:
                    print(f"[TEMP_ANALYZER DEBUG] Threshold alert generated for printer {reading.printerId}: {temp} > {self.printer_max_threshold}")

                return EmergencyAlert(
                    alert_id=f"printer_{reading.printerId}_{reading.timestamp}",
                    source="printer",
                    source_id=reading.printerId,
                    alert_type="overheat",
                    timestamp=reading.timestamp,
                    details={"temperature": temp}
                )

        elif isinstance(reading, TemperatureReadingRoomDTO):
            temp = reading.temperature
            
            if temp > self.room_max_threshold:
                if self.debug:
                    print(f"[TEMP_ANALYZER DEBUG] Threshold alert generated for room {reading.sensorId}: {temp} > {self.room_max_threshold}")

                return EmergencyAlert(
                    alert_id=f"room_{reading.sensorId}_{reading.timestamp}",
                    source="room",
                    source_id=reading.sensorId,
                    alert_type="overheat",
                    timestamp=reading.timestamp,
                    details={"temperature": temp}
                )
        else:
            raise TypeError("Invalid reading type. Expected TemperatureReadingPrinterDTO or TemperatureReadingRoomDTO.")

        if self.debug and isinstance(reading, TemperatureReadingPrinterDTO):
            print("[TEMP_ANALYZER DEBUG] No printer THRESHOLD alert generated.")
        elif self.debug and isinstance(reading, TemperatureReadingRoomDTO):
            print("[TEMP_ANALYZER DEBUG] No room THRESHOLD alert generated.")
        return None

    def check_rate(self, reading_prev: TemperatureReadingPrinterDTO | TemperatureReadingRoomDTO, reading_curr: TemperatureReadingPrinterDTO | TemperatureReadingRoomDTO) -> EmergencyAlert | None:
        # Check if the rate of change exceeds a threshold
        if isinstance(reading_prev, TemperatureReadingPrinterDTO) and isinstance(reading_curr, TemperatureReadingPrinterDTO):
            delta_temp = reading_curr.temperature - reading_prev.temperature
            if delta_temp <= 0:
                if self.debug:
                    print("[TEMP_ANALYZER DEBUG] No printer RATE alert generated (temperature did not increase).")
                return None
            # Convert timestamps to float in case they are strings
            prev_time = _parse_timestamp(reading_prev.timestamp)
            curr_time = _parse_timestamp(reading_curr.timestamp)
            delta_time = abs(curr_time - prev_time)
            rate_per_second = delta_temp / delta_time if delta_time > 0 else float('inf')
            rate_per_minute = rate_per_second * 60

            if self.debug:
                print(f"[TEMP_ANALYZER DEBUG] Detected: printer rate per minute {rate_per_minute} with delta_temp {delta_temp} and delta_time {delta_time}")

            if rate_per_minute > self.printer_max_rate:
                if self.debug:
                    print(f"[TEMP_ANALYZER DEBUG] Rate alert generated for printer {reading_curr.printerId}: {rate_per_minute} > {self.printer_max_rate}")

                return EmergencyAlert(
                    alert_id=f"rate_printer_{reading_curr.printerId}_{reading_curr.timestamp}",
                    source="printer",
                    source_id=reading_curr.printerId,
                    alert_type="rate_exceeded",
                    timestamp=reading_curr.timestamp,
                    details={"rate per minute": rate_per_minute}
                )
            
        elif isinstance(reading_prev, TemperatureReadingRoomDTO) and isinstance(reading_curr, TemperatureReadingRoomDTO):
            delta_temp = reading_curr.temperature - reading_prev.temperature
            if delta_temp <= 0:
                if self.debug:
                    print("[TEMP_ANALYZER DEBUG] No room RATE alert generated (temperature did not increase).")
                return None
            # Convert timestamps to float in case they are strings
            prev_time = _parse_timestamp(reading_prev.timestamp)
            curr_time = _parse_timestamp(reading_curr.timestamp)
            delta_time = abs(curr_time - prev_time)
            rate_per_second = delta_temp / delta_time if delta_time > 0 else float('inf')
            rate_per_minute = rate_per_second * 60

            if self.debug:
                print(f"[TEMP_ANALYZER DEBUG] Detected: room rate per minute {rate_per_minute} with delta_temp {delta_temp} and delta_time {delta_time}")

            if rate_per_minute > self.room_max_rate:
                if self.debug:
                    print(f"[TEMP_ANALYZER DEBUG] Room rate alert generated for {reading_curr.sensorId}: {rate_per_minute} > {self.room_max_rate}")

                return EmergencyAlert(
                    alert_id=f"rate_room_{reading_curr.sensorId}_{reading_curr.timestamp}",
                    source="room",
                    source_id=reading_curr.sensorId,
                    alert_type="rate_exceeded",
                    timestamp=reading_curr.timestamp,
                    details={"rate per minute": rate_per_minute}
                )
        else:
            raise TypeError("Invalid reading types for rate check. Expected TemperatureReadingPrinterDTO or TemperatureReadingRoomDTO.")

        # No alert if thresholds not exceeded
        if self.debug:
            if isinstance(reading_prev, TemperatureReadingPrinterDTO):
                print("[TEMP_ANALYZER DEBUG] No printer RATE alert generated.")
            elif isinstance(reading_prev, TemperatureReadingRoomDTO):
                print("[TEMP_ANALYZER DEBUG] No room RATE alert generated.")

        return None

def _parse_timestamp(ts):
    # Handles ISO 8601 and float timestamps
    if isinstance(ts, (float, int)):
        return float(ts)
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except Exception:
        return float(ts)  # fallback for legacy float timestamps


if __name__ == "__main__":
    # Example usage for testing
    #
    # From anomaly_detection directory:
    #    cd /home/leonardo/iot/IoT_Project/anomaly_detection
    #    python3 -m app.classes.temperature_analyzer

    # Adjustable interval in seconds
    #       with 60 seconds the rate is the --> difference <-- between two consecutive readings
    #       with 30 seconds the rate is the --> difference*2 <-- between two consecutive readings
    #       with 120 seconds the rate is the --> difference/2 <-- between two consecutive readings
    interval = 60/2

    # Create some example readings with more realistic values and intervals
    room_readings = [
        TemperatureReadingRoomDTO(temperature=22.5, sensorId="room1", timestamp=0, unit="C"),
        TemperatureReadingRoomDTO(temperature=23.0, sensorId="room1", timestamp=interval, unit="C"),
        TemperatureReadingRoomDTO(temperature=23.2, sensorId="room1", timestamp=2*interval, unit="C"),
        TemperatureReadingRoomDTO(temperature=51.0, sensorId="room1", timestamp=3*interval, unit="C"),  # Over threshold
        TemperatureReadingRoomDTO(temperature=22.8, sensorId="room2", timestamp=0, unit="C"),
        TemperatureReadingRoomDTO(temperature=23.1, sensorId="room2", timestamp=interval, unit="C"),
        TemperatureReadingRoomDTO(temperature=24.0, sensorId="room2", timestamp=2*interval, unit="C"),
        TemperatureReadingRoomDTO(temperature=24.5, sensorId="room2", timestamp=3*interval, unit="C"),
    ]
    printer_readings = [
        TemperatureReadingPrinterDTO(temperature=95.0, printerId="printer1", timestamp=0, unit="C"),
        TemperatureReadingPrinterDTO(temperature=97.5, printerId="printer1", timestamp=interval, unit="C"),
        TemperatureReadingPrinterDTO(temperature=102.0, printerId="printer1", timestamp=2*interval, unit="C"),
        TemperatureReadingPrinterDTO(temperature=310.0, printerId="printer1", timestamp=3*interval, unit="C"),  # Over threshold
        TemperatureReadingPrinterDTO(temperature=98.0, printerId="printer2", timestamp=0, unit="C"),
        TemperatureReadingPrinterDTO(temperature=99.5, printerId="printer2", timestamp=interval, unit="C"),
        TemperatureReadingPrinterDTO(temperature=100.0, printerId="printer2", timestamp=2*interval, unit="C"),
        TemperatureReadingPrinterDTO(temperature=101.0, printerId="printer2", timestamp=3*interval, unit="C"),
    ]

    analyzer = TemperatureAnalyzer(config_path='app/anomaly_detection_config.yaml', debug=True)
    


    # Threshold EVALUATION
    ''' 
    print("--- Threshold Values ---")
    print(f"Room max threshold: {analyzer.room_max_threshold}")
    print(f"Printer max threshold: {analyzer.printer_max_threshold}")
    print(f"Printer max rate: {analyzer.printer_max_rate}")
    print(f"Room max rate: {analyzer.room_max_rate}")

    print("\n--- Threshold Tests ---")
    for reading in printer_readings:
        print(f"Printer reading: {reading.temperature}")
        alert = analyzer.check_thresholds(reading)

    for reading in room_readings:
        print(f"Room reading: {reading.temperature}")
        alert = analyzer.check_thresholds(reading)
    '''



    # Rate of Change EVALUATION

    print("\n--- Rate of Change Tests ---")
    # Test printer rate
    for i in range(len(printer_readings) - 1):
        print(f"Printer rate {printer_readings[i].printerId}: {printer_readings[i].temperature} -> {printer_readings[i+1].temperature}")
        alert = analyzer.check_rate(printer_readings[i], printer_readings[i+1])

    # Test room rate
    for i in range(len(room_readings) - 1):
        print(f"Room rate {room_readings[i].sensorId}: {room_readings[i].temperature} -> {room_readings[i+1].temperature}")
        alert = analyzer.check_rate(room_readings[i], room_readings[i+1])
