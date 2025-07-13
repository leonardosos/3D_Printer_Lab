from dataclasses import dataclass

@dataclass
class PrinterAssignment:
    job_id: str
    model_url: str
    filament_type: str
    estimated_time: int
    priority: int
    assigned_at: str
    layer_height: float
    infill: float
    nozzle_temp: float

