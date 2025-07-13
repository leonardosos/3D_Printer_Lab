from dataclasses import dataclass

@dataclass
class PrintJob:
    job_id: str
    model_url: str
    filament_type: str
    estimated_time: int
    priority: int
    assigned_at: str
    layer_height: float
    infill: float
    nozzle_temp: float
    progress: float = 0.0
    status: str = "idle"

    def update_progress(self, progress: float):
        self.progress = progress

    def update_status(self, status: str):
        self.status = status

