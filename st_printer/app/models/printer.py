from dataclasses import dataclass

@dataclass
class Printer:
    printer_id: str          # Unique identifier for the printer
    printer_type: str        # Type of printer (e.g., FDM, SLA)
    filament_type: str       # Type of filament used (e.g., PLA, ABS)
    nozzle_diameter: float   # Diameter of the printer nozzle in mm
    max_nozzle_temp: float   # Maximum nozzle temperature in Celsius
    temp_rate: float         # Rate at which the nozzle temperature changes
    print_speed: float       # Printing speed in mm/s
    status: str = "idle"     # Current status of the printer
    current_temp: float = 25.0 # Current nozzle temperature in Celsius

    def update_status(self, status: str):
        # Update the printer's status (e.g., 'idle', 'printing', etc.)
        self.status = status

    def set_temperature(self, temp: float):
        # Set the current nozzle temperature
        self.current_temp = temp


