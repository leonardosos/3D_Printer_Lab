from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.dto.monitoring_dto import MonitoringDTO
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.get("/printer/status", response_model=MonitoringDTO)
def printer_status(service=Depends(lambda: __import__('app.main', fromlist=['get_service']).get_service())):
    monitoring_dto = service.get_monitoring_dto()
    return JSONResponse(content=jsonable_encoder(monitoring_dto))