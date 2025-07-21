from app.dto.status_dto import StatusDTO
from app.dto.emergency_dto import EmergencyDTO

class FanControllerRepository:
    def __init__(self):
        self._latest_status = None  # type: StatusDTO | None
        self._latest_emergency = None  # type: EmergencyDTO | None

    def update_status(self, status: StatusDTO):
        self._latest_status = status

    def get_latest_status(self) -> StatusDTO | None:
        return self._latest_status

    def update_emergency(self, emergency: EmergencyDTO):
        self._latest_emergency = emergency

    def get_latest_emergency(self) -> EmergencyDTO | None:
        return self._latest_emergency

    def clear_emergency(self):
        self._latest_emergency = None