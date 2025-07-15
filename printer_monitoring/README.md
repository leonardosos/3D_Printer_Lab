# Printer Monitoring Microservice

The `printer_monitoring` microservice is responsible for collecting and organizing information about active 3D printing jobs. It aggregates data coming from a printer, a robot (responsible for post-processing), and a job assignment system. Its main function is to serve this organized data to a front-end User Interface upon request via an HTTP GET endpoint.

---

## Overview

### Inputs

Data is received via MQTT from three primary sources:

* **Printer progress** (`device/printer/-id-/progress`)
* **Robot progress** (`device/robot/-id-/progress`)
* **Job assignment** (`device/printer/-id-/assignement`)

### Output

Data is provided in response to an HTTP `GET /printer/status` request, containing the current status of all active printer-robot-job groupings.

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
      "progress": 42,
      "temperature": 205.3,
      "lastUpdated": "2025-06-15T08:31:15Z"
    }
  ]
}
```

---

## DTO Definitions

Located in `app/dto/`:

```python
@dataclass
class printerProgressDTO:
    printerId: str
    jobId: str
    status: str
    progress: int
    timestamp: float

@dataclass
class robotProgressDTO:
    robotId: str
    jobId: str
    action: str
    status: str
    timestamp: float

@dataclass
class jobDTO:
    jobId: str
    modelUrl: str
    filamentType: str
    estimatedTime: int
    priority: int
    assignedAt: float
    parameters: dict

@dataclass
class MonitoringDTO:
    printers: list  # List of dicts representing linked printer-robot-job states
```

---

## Core Class: `PrinterMonitoring`

Implemented in `main.py`:

```python
class PrinterMonitoring:

    def __init__(self):
        self.printers = []
        self.robots = []
        self.jobs = []

    def on_printer_progress(self, json_input):
        # Deserialize and store printer data

    def on_robot_progress(self, json_input):
        # Deserialize and store robot data

    def on_job_assignement(self, json_input):
        # Deserialize and store job info

    def is_job_id(self):
        # Check if matching jobId exists across all sources

    def link(self, job_id):
        # Link matching printer, robot, and job into a MonitoringDTO

    def monitoring_list(self, monitoring):
        # creates the output list for the HTTP GET /printer/status request
```

### Logic

1. Data is incrementally stored in lists (`self.printers`, `self.robots`, `self.jobs`) upon receiving MQTT updates.
2. The `is_job_id()` method searches for matching `jobId`s in all lists.
3. Matching entries are linked using `link(job_id)` to produce a `MonitoringDTO`.
4. The result is returned by `publish_monitoring()` upon an HTTP GET request.

---

## Directory Structure

```
printer_monitoring/
├── app/
│   ├── dto/
│   │   ├── __init__.py
│   │   ├── printer_progress_dto.py
│   │   ├── robot_progress_dto.py
│   │   ├── job_dto.py
│   ├── model/
│   │   ├── __init__.py
│   │   ├── monitoring.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   └── repository.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── mqtt/
│   │   ├── __init__.py
│   │   ├── subscriber.py
│   ├── main.py
├── requirements.txt
├── Dockerfile
```

---

## Known Limitations / Improvements

* Currently only supports 1:1:1 mappings of printer-robot-job by `jobId`
* Lacks persistence or cleanup of outdated entries
* No real-time push system to UI; only polling via HTTP GET

---

## Docker Usage

To containerize and run:

```bash
docker build -t printer_monitoring .
docker run -d --name printer_monitoring printer_monitoring
```

---

## Final Notes

* All DTO fields are typed correctly.
* Each input and output is strongly aligned with its respective dataclass.
* The system is optimized for aggregation and read-only querying.
* Directory structure reflects clean modular separation.

Feel free to request additional features, such as WebSocket support, RESTful endpoints for individual job queries, or job history logging.
