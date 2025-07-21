import logging
from fastapi import FastAPI
from app.api.routes import router
from app.persistence.repository import PrinterMonitoringRepository
from app.model.monitoring import PrinterMonitoringService
from app.mqtt.subscriber import MQTTSubscriber

logging.basicConfig(level=logging.INFO)

# Global singletons
repository = PrinterMonitoringRepository()
service = PrinterMonitoringService(repository)
mqtt_subscriber = MQTTSubscriber("localhost", 1883, service)

app = FastAPI()

# Dependency for injection
def get_service():
    return service

# Include API router, injecting the service
app.include_router(router)

@app.on_event("startup")
def startup_event():
    logging.info("Starting Printer Monitoring Microservice...")
    mqtt_subscriber.start()
    service.cleanup_completed()

@app.on_event("shutdown")
def shutdown_event():
    logging.info("Shutting down Printer Monitoring Microservice...")

# Standalone test mode
if __name__ == "__main__":
    print("Running Printer Monitoring Microservice in standalone mode.")
    # Example: Add a test printer and job, then print the monitoring DTO
    test_printer = repository.__class__.__module__ + "." + repository.__class__.__name__
    repository.add_or_update_printer(
        # Example printer DTO, adjust fields as needed
        __import__('app.dto.printer_progress_dto', fromlist=['PrinterProgressDTO']).PrinterProgressDTO(
            printerId="printer-1",
            jobId="job-123",
            status="printing",
            progress=42,
            timestamp=1721385600.0
        )
    )
    repository.add_or_update_job(
        # Example job DTO, adjust fields as needed
        __import__('app.dto.job_dto', fromlist=['JobDTO']).JobDTO(
            jobId="job-123",
            modelUrl="models/model-456.gcode",
            filamentType="PLA",
            estimatedTime=3600,            
            priority=10,
            assignedAt=1721385600.0,
            parameters={"layerHeight": 0.2, "infill": 20, "nozzleTemp": 210, "bedTemp": 60}
        )
    )
    # Print the monitoring DTO output
    print("MonitoringDTO output:")
    print(service.get_monitoring_dto())
    # Optionally, start the API server for manual testing
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)