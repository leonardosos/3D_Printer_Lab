"""
TemperatureHistory: Stores and manages all received temperature readings (room and printers).
"""
from typing import List, Dict, Any
from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO
import threading
import csv
from datetime import datetime, timedelta


class TemperatureHistory:
    def __init__(self, printer_ids: List[str], debug: bool = True):
        # Thread-safe storage for temperature readings
        self._lock = threading.RLock()

        # Store room and printer readings
        # Using lists to maintain order of readings
        self.room_readings: List[TemperatureReadingRoomDTO] = []
        self.printer_readings: List[TemperatureReadingPrinterDTO] = []
        
        # Initialize with known printer IDs
        self.printer_ids = printer_ids

        self.debug = debug

    def add_room_reading(self, reading: TemperatureReadingRoomDTO):
        with self._lock:
            self.room_readings.append(reading)

    def add_printer_reading(self, reading: TemperatureReadingPrinterDTO):
        with self._lock:
            self.printer_readings.append(reading)

    def get_latest_room_temperature(self, timestamp: str) -> TemperatureReadingRoomDTO:
        """Get the latest room temperature reading up to the given timestamp."""
        with self._lock:
            readings = [r for r in self.room_readings if r.timestamp <= timestamp]
            if readings:
                return readings[-1]  # Return the most recent one
            return None  # No reading found
    
    def get_latest_printer_temperature(self, timestamp: str) -> Dict[str, TemperatureReadingPrinterDTO]:
        """Get the latest printer temperature readings up to the given timestamp."""
        with self._lock:
            latest_readings = {}
            for pid in self.printer_ids:
                readings = [r for r in self.printer_readings if r.printerId == pid and r.timestamp <= timestamp]
                if readings:
                    latest_readings[pid] = readings[-1]
            return latest_readings  # Return a dict of printerId to latest reading

    def clear(self):
        with self._lock:
            self.room_readings.clear()
            self.printer_readings.clear()

    def csv_dump(self, file_path: str):
        """Dump the temperature history to a CSV file."""

        # Create directories if they do not exist
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, mode="a", newline="") as csvfile:
            fieldnames = ["timestamp", "temperature", "source", "sourceId"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header only if the file is new
            if os.path.getsize(file_path) == 0:
                writer.writeheader()
            for reading in self.room_readings:
                writer.writerow({
                    "timestamp": reading.timestamp,
                    "temperature": reading.temperature,
                    "source": "room",
                    "sourceId": reading.sensorId
                })
            for reading in self.printer_readings:
                writer.writerow({
                    "timestamp": reading.timestamp,
                    "temperature": reading.temperature,
                    "source": "printer",
                    "sourceId": reading.printerId
                })
        
        if self.debug:
            print(f"[TEMPERATURE_HISTORY DEBUG] Dumped temperature history to {file_path}")


if __name__ == "__main__":
    # Example usage for testing
    #
    # From persistence directory:
    #
    #    cd /home/leonardo/iot/IoT_Project/anomaly_detection
    #    python3 -m app.persistence.temperature_history
    #
    from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
    from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO

    printer_ids = ["printer1", "printer2"]
    history = TemperatureHistory(printer_ids=printer_ids)

    # Simulate readings over a period (e.g., 10 time steps)
    import random

    start = datetime(2023, 10, 1, 12, 0, 1)
    for t in range(109):  # 109 readings, 1-second apart
        timestamp = (start + timedelta(seconds=t)).strftime("%Y-%m-%dT%H:%M:%SZ")
        room_temp = round(random.uniform(20, 30), 2)
        history.add_room_reading(TemperatureReadingRoomDTO(
            temperature=room_temp, sensorId="room1", timestamp=timestamp, unit="C"
        ))
        for pid in printer_ids:
            printer_temp = round(random.uniform(100, 300), 2)
            history.add_printer_reading(TemperatureReadingPrinterDTO(
                temperature=printer_temp, printerId=pid, timestamp=timestamp, unit="C"
            ))

    
    print("Latest room temperature:", history.get_latest_room_temperature("2023-10-01T12:00:10Z"))
    print("Latest printer temperatures:", history.get_latest_printer_temperature("2023-10-01T12:00:10Z"))