# Job Handler Microservice

The `job_handler` microservice is the core orchestration unit in a distributed 3D printing architecture. It assigns print jobs to available printers, tracks their progress, and coordinates tray unloads via robot units.

---

## Overview

This service:

- Retrieves jobs via HTTP GET from the **Priority Queue Manager**
- Assigns available printers to new jobs based on priority
- Publishes assignments to:
  - The target printer
  - The printer manager
- Notifies the **Robot Manager** when a printer finishes a job and needs unloading
- Monitors MQTT topics for printer and robot progress
- Maintains internal state of jobs, printers, and assignment lifecycle

---

## Message Formats

### Jobs Input

**Source:** HTTP GET `/jobs` from the User Interface  
**Format:**

```json
{
  "jobs": [
    {
      "id": "job-123",
      "modelId": "model-456",
      "assignedPrinterId": null,
      "priority": 10,
      "status": "pending",
      "submittedAt": "2025-06-15T08:30:00Z",
      "updatedAt": "2025-06-15T08:30:00Z"
    }
  ]
}
```

---

### Job Assignment Output

**Topic:** `device/printer/<printer-id>/assignement`

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

---

### Printer Status Update to Robot Manager

**Topic:** `device/printers`

```json
{
  "printers": [
    { "printerId": "printer-1", "status": "work", "timestamp": "2025-07-09T10:00:00Z" },
    { "printerId": "printer-2", "status": "finish", "timestamp": "2025-07-09T10:00:00Z" },
    { "printerId": "printer-3", "status": "work", "timestamp": "2025-07-09T10:00:00Z" }
  ]
}
```

---

### Printer Progress Input

**Topic:** `device/printer/<printer-id>/progress`

```json
{
  "printerId": "printer-1",
  "jobId": "job-123",
  "status": "printing",
  "progress": 42,
  "timestamp": "2025-06-15T08:32:00Z"
}
```

---

### Robot Progress Input

**Topic:** `device/robot/<robot-id>/progress`

```json
{
  "robotId": "rob-1",
  "action": "pick",
  "status": "in_progress",
  "timestamp": "2025-06-15T08:32:10Z"
}
```

---

## Architecture

### DTOs

Located in `app/dto/`, used for data deserialization:

```python
@dataclass
class jobsDTO:
    jobs: list

@dataclass
class assignementDTO:
    jobId: str
    modelUrl: str
    filamentType: str
    estimatedTime: int
    priority: int
    assignedAt: float
    parameters: dict

@dataclass
class assignedPrinterDTO:
    printers: list

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
```

---

### JobHandler Logic

Main logic is encapsulated in `JobHandler`:

```python
class JobHandler:

    def __init__(self, printer_repository, robot_manager_client, mqtt_publisher): 
      # Initializes the job handler with the printer repository, robot manager client, and MQTT publisher

    def assign_job_to_printer(self, job_id: str): 
      # Assigns a job to an available printer that has a clean and ready plate

    def receive_printer_progress(self, progress_dto):
      # Receives and stores the printer's progress as a percentage of the job completion

    def handle_printer_idle(self, printer_id: str): 
      # Determines whether the printer is idle due to finishing a print or because it hasn’t been assigned a job yet, and updates its status accordingly

    def receive_robot_progress(self, progress_dto): 
      # Receives and stores the robot's progress in cleaning the plate

    def notify_robot_manager_of_printer_to_unload(self, printer_id: str):
      # Publishes the printer ID to the robot manager's priority queue for unloading

    def mark_printer_as_busy_with_job(self, printer_id: str, job_id: str):
      # Marks the printer as busy and associates it with the given job

    def mark_printer_as_available(self, printer_id: str): 
      # Marks the printer as available and adds it back to the available printers list

    def get_available_printer(self) -> str: 
      # Retrieves and removes an available printer from the available printers list

    def get_job_associated_with_printer(self, printer_id: str) -> str: 
      # Returns the job ID currently assigned to the specified printer

    def get_status(self) -> dict: 
      # Returns the current status of all printers: available, working, or waiting for plate cleaning

    
```

---

## Internal Workflow

1. **Initialization**  
   - Fetch current printers from MQTT `progress` topics
   - Populate available printers and job tracking

2. **Assignment Flow**  
   - Triggered at startup, periodically, or after a job completes
   - Retrieves all pending jobs via HTTP
   - For each job:
     - Finds a printer-robot pair
     - Creates assignment
     - Publishes to printer and robot manager
     - Sends DELETE to Priority Queue Manager (by subJobId)

3. **Progress Monitoring**  
   - Listens to:
     - Printer progress (to detect job completion)
     - Robot progress (to reinsert printer in available pool)

---

## Directory Structure

```
job_handler/
├── app/
│   ├── dto/
│   │   ├── jobs_dto.py
│   │   ├── assignement_dto.py
│   │   ├── assigned_printer_dto.py
│   │   ├── printer_progress_dto.py
│   │   ├── robot_progress_dto.py
│   ├── model/
│   │   └── job_handler.py
│   ├── persistence/
│   │   └── repository.py
│   ├── api/
│   │   └── routes.py
│   ├── mqtt/
│   │   ├── subscriber.py
│   │   └── publisher.py
│   ├── main.py
├── requirements.txt
├── Dockerfile
```

---

## Docker Usage

To build and run the container:

```bash
docker build -t job_handler .
docker run -d --name job_handler job_handler
```

---

## Installation

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Final Notes

- All JSON formats are represented using Python dataclasses
- Printers are marked `F` (Free) or `O` (Occupied)
- Assignments only happen if a printer and a robot are both available
- Assignments are published via MQTT and logged internally
- System is reactive: new jobs are fetched and assigned upon printer/robot availability

Feel free to extend this README with error handling, API tests, or deployment scripts.