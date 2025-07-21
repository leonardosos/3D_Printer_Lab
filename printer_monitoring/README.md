# Printer Monitoring Microservice

The `printer_monitoring` microservice collects and aggregates real-time status data from 3D printers and related jobs. It listens for MQTT messages from the printer and job assignment systems, organizes the data, and serves it via a RESTful HTTP GET endpoint. The system has been refactored for better modularity using a repository-service architecture.

---

## Overview

### Inputs (via MQTT)

Data is received from:

- **Printer Progress:** `device/printer/-id-/progress`
- **Robot Progress:** `device/robot/-id-/progress`
- **Job Assignment:** `device/printer/-id-/assignement`

### Output (via HTTP)

The system serves monitoring data on:

- **Endpoint:** `GET /printer/status`

Returns the current status of all active printers with relevant job data.

---

## Message Formats

### Printer Progress (MQTT)

**Topic:** `device/printer/-id-/progress`

```json
{
  "printerId": "printer-1",
  "jobId": "job-123",
  "status": "printing",
  "progress": 42,
  "timestamp": "2025-06-15T08:32:00Z"
}
```

### Robot Progress (MQTT)

**Topic:** `device/robot/-id-/progress`

```json
{
  "robotId": "rob-1",
  "action": "pick",
  "status": "in_progress",
  "timestamp": "2025-06-15T08:32:10Z"
}
```

### Job Assignment (MQTT)

**Topic:** `device/printer/-id-/assignement`

```json
{
  "jobId": "job-123",
  "modelUrl": "models/model-456.gcode",
  "filamentType": "PLA",
  "estimatedTime": 3600,
  "priority": 10,
  "assignedAt": "2025-06-15T08:30:00Z",
  "parameters": {
    "layerHeight": 0.2,
    "infill": 20,
    "nozzleTemp": 210,
    "bedTemp": 60
  }
}
```

### Monitoring Output (HTTP GET)

**Endpoint:** `/printer/status`

```json
{
  "printers": [
    {
      "printerId": "printer-1",
      "status": "printing",
      "currentJobId": "job-123",
      "modelUrl": "models/model-456.gcode",
      "progress": 42,
      "temperature": 205.3,
      "lastUpdated": "2025-06-15T08:31:15Z"
    }
  ]
}
```

---

## Core Components

### Service Layer: `PrinterMonitoringService`

Implemented in `app/model/monitoring.py`. Responsibilities include:

- Aggregating printer and job data from the repository
- Constructing `MonitoringDTO` objects
- Exposing `on_printer_progress` and `on_job_assignement` entry points
- Cleanup of completed jobs

```python
def get_monitoring_dto(self) -> MonitoringDTO:
    # Aggregates printer and job info into a MonitoringDTO
```

### Persistence Layer: `PrinterMonitoringRepository`

Responsible for in-memory storage and retrieval of printers and jobs.

```python
def get_printers(self) -> List[PrinterProgressDTO]
def get_jobs(self) -> List[JobDTO]
def add_or_update_printer(dto)
def add_or_update_job(dto)
```

### API

Implemented via FastAPI in `app/api/routes.py`, exposing:

- `GET /printer/status` — returns the monitoring status via the `PrinterMonitoringService`

### MQTT Subscriber

Listens for MQTT messages and passes them to the appropriate service method (`on_printer_progress`, `on_job_assignement`).

---

## DTO Definitions

Located in `app/dto/`:

```python
@dataclass
class PrinterProgressDTO:
    printerId: str
    jobId: str
    status: str
    progress: int
    timestamp: float

@dataclass
class JobDTO:
    jobId: str
    modelUrl: str
    filamentType: str
    estimatedTime: int
    priority: int
    assignedAt: float
    parameters: dict

@dataclass
class PrinterStatusDTO:
    printerId: str
    status: str
    currentJobId: str
    modelUrl: str
    progress: int
    temperature: float
    lastUpdated: str

@dataclass
class MonitoringDTO:
    printers: List[PrinterStatusDTO]
```

---

## Entry Point (`main.py`)

Handles FastAPI initialization, MQTT subscriber startup, and example standalone mode:

- Launches MQTT subscriber
- Injects service via dependency
- On `__main__`, runs a test with dummy data and optionally starts the API

---

## Directory Structure

```
printer_monitoring/
├── app/
│   ├── dto/
│   │   ├── printer_progress_dto.py
│   │   ├── robot_progress_dto.py
│   │   ├── job_dto.py
│   │   ├── monitoring_dto.py
│   ├── model/
│   │   ├── monitoring.py
│   ├── persistence/
│   │   └── repository.py
│   ├── api/
│   │   └── routes.py
│   ├── mqtt/
│   │   └── subscriber.py
│   ├── main.py
├── requirements.txt
├── Dockerfile
```

---

## Docker Usage

To build and run the container:

```bash
docker build -t printer_monitoring .
docker run -d --name printer_monitoring -p 8000:8000 printer_monitoring
```

---

## Known Limitations / Future Improvements

- Currently supports only one active job per printer (1:1 mapping)
- Data persistence is in-memory; no database support
- No real-time push (e.g., WebSocket) to frontend
- Robot progress data is not yet linked in monitoring output

---

## Final Notes

- The system follows a clean architecture: DTOs, services, repositories, API, and MQTT all separated.
- Can be extended easily with historical logging, WebSocket updates, or database support.
- Designed for robust read-only status querying via REST API.

---
