"""
TemperatureHistory: Stores and manages all received temperature readings (room and printers).
"""
from typing import List, Dict, Any
from app.dto.temperature_reading_room_dto import TemperatureReadingRoomDTO
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO
from app.dto.global_temperature_response_dto import TemperatureReadingDTO
import threading

class TemperatureHistory:
    def __init__(self):
        self._lock = threading.Lock()
        self.room_readings: List[TemperatureReadingRoomDTO] = []
        self.printer_readings: List[TemperatureReadingPrinterDTO] = []

    def add_room_reading(self, reading: TemperatureReadingRoomDTO):
        with self._lock:
            self.room_readings.append(reading)

    def add_printer_reading(self, reading: TemperatureReadingPrinterDTO):
        with self._lock:
            self.printer_readings.append(reading)

    def get_all_readings(self) -> List[TemperatureReadingDTO]:
        """
        Returns all readings as TemperatureReadingDTO (for API response)
        """
        with self._lock:
            readings = []
            for r in self.room_readings:
                readings.append(TemperatureReadingDTO(
                    temperature=r.temperature,
                    source="room",
                    sourceId=r.sensorId,
                    timestamp=r.timestamp
                ))
            for p in self.printer_readings:
                readings.append(TemperatureReadingDTO(
                    temperature=p.temperature,
                    source="printer",
                    sourceId=p.printerId,
                    timestamp=p.timestamp
                ))
            return readings

    def get_latest_room(self) -> TemperatureReadingRoomDTO:
        with self._lock:
            if not self.room_readings:
                return None
            return max(self.room_readings, key=lambda r: r.timestamp)

    def get_latest_printer(self, printer_id: str) -> TemperatureReadingPrinterDTO:
        with self._lock:
            filtered = [r for r in self.printer_readings if r.printerId == printer_id]
            if not filtered:
                return None
            return max(filtered, key=lambda r: r.timestamp)

    def clear(self):
        with self._lock:
            self.room_readings.clear()
            self.printer_readings.clear()

