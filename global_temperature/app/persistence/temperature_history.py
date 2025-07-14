"""
TemperatureHistory: Stores and manages all received temperature readings (room and printers).
"""
from typing import List, Dict, Any
from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO
from app.dto.global_temperature_response_dto import TemperatureReadingDTO
import threading
import csv

class TemperatureHistory:
    def __init__(self, printer_ids: List[str]):
        # Thread-safe storage for temperature readings
        self._lock = threading.Lock()

        # Store room and printer readings
        # Using lists to maintain order of readings
        self.room_readings: List[TemperatureReadingRoomDTO] = []
        self.printer_readings: List[TemperatureReadingPrinterDTO] = []
        
        # Initialize with known printer IDs
        self.printer_ids = printer_ids

    def add_room_reading(self, reading: TemperatureReadingRoomDTO):
        with self._lock:
            self.room_readings.append(reading)

    def add_printer_reading(self, reading: TemperatureReadingPrinterDTO):
        with self._lock:
            self.printer_readings.append(reading)

    def get_latest_room(self) -> TemperatureReadingDTO:
        with self._lock:
            if not self.room_readings:
                return None
            latest = max(self.room_readings, key=lambda r: r.timestamp)
            return TemperatureReadingDTO(
                temperature=latest.temperature,
                source="room",
                sourceId=latest.sensorId,
                timestamp=str(latest.timestamp)
            )

    def get_latest_printer(self, printer_id: str) -> TemperatureReadingDTO:
        with self._lock:
            filtered = [r for r in self.printer_readings if r.printerId == printer_id]
            if not filtered:
                return None
            latest = max(filtered, key=lambda r: r.timestamp)
            return TemperatureReadingDTO(
                temperature=latest.temperature,
                source="printer",
                sourceId=latest.printerId,
                timestamp=str(latest.timestamp)
            )
    
    def get_latest_printers(self) -> Dict[str, TemperatureReadingDTO]:
        """Get the latest reading for each printer ID known as DTOs."""
        with self._lock:
            latest_readings = {}
            for printer_id in self.printer_ids:
                filtered = [r for r in self.printer_readings if r.printerId == printer_id]
                if filtered:
                    latest = max(filtered, key=lambda r: r.timestamp)
                    latest_readings[printer_id] = TemperatureReadingDTO(
                        temperature=latest.temperature,
                        source="printer",
                        sourceId=latest.printerId,
                        timestamp=str(latest.timestamp)
                    )
            return latest_readings

    def clear(self):
        with self._lock:
            self.room_readings.clear()
            self.printer_readings.clear()

    def csv_dump(self, file_path: str):
        """Dump the temperature history to a CSV file."""
        with open(file_path, mode="w", newline="") as csvfile:
            fieldnames = ["timestamp", "temperature", "source", "sourceId"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

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

if __name__ == "__main__":
    # Example usage for testing
    #
    # From persistence directory:
    #
    #    cd /home/leonardo/iot/IoT_Project/global_temperature
    #    python3 -m app.persistence.temperature_history
    #
    from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
    from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO

    printer_ids = ["printer1", "printer2"]
    history = TemperatureHistory(printer_ids=printer_ids)

    # Add room readings
    history.add_room_reading(TemperatureReadingRoomDTO(temperature=22, sensorId="room1", timestamp=1, unit="C"))
    history.add_room_reading(TemperatureReadingRoomDTO(temperature=40, sensorId="room1", timestamp=2, unit="C"))

    # Add printer readings
    history.add_printer_reading(TemperatureReadingPrinterDTO(temperature=100, printerId="printer1", timestamp=1, unit="C"))
    history.add_printer_reading(TemperatureReadingPrinterDTO(temperature=300, printerId="printer1", timestamp=2, unit="C"))
    history.add_printer_reading(TemperatureReadingPrinterDTO(temperature=123, printerId="printer1", timestamp=3, unit="C"))
    history.add_printer_reading(TemperatureReadingPrinterDTO(temperature=280, printerId="printer2", timestamp=1, unit="C"))
    history.add_printer_reading(TemperatureReadingPrinterDTO(temperature=289, printerId="printer2", timestamp=2, unit="C"))

    print("Latest room reading:", history.get_latest_room())
    print("Latest printer1 reading:", history.get_latest_printer("printer1"))
    print("Latest printer2 reading:", history.get_latest_printer("printer2"))
    print("Latest printers:", history.get_latest_printers())

    ### test temperature analyzer
    from app.models.temperature_analyzer import TemperatureAnalyzer

    analyzer = TemperatureAnalyzer()
    heat_level = analyzer.compute_heat_level(
        room_readings=history.get_latest_room(),
        printer_readings=list(history.get_latest_printers().values())
    )
    print("Computed heat level:", heat_level)

    # Dump to CSV
    history.csv_dump("temperature_history.csv")