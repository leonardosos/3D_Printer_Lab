# 🛠️ Job Handler Microservice

The `job_handler` microservice is a key orchestration component in a distributed 3D printing system. Its main responsibility is to assign print jobs to available printers, monitor their progress, and free up printers once printing and post-processing (plate cleaning by robots) are completed.

---

## 🚀 Features

- Discovers available printers in the environment.
- Retrieves prioritized print jobs via HTTP from a Queue Manager.
- Assigns jobs via MQTT to printers.
- Tracks printer progress through MQTT subscriptions.
- Notifies a robot microservice when a job is complete.
- Marks printers as available after cleaning.

---

## 📦 Project Structure

```
job_handler/
├── app/
│   ├── api/                   # HTTP or API routes (e.g. /prioritary_job)
│   ├── dto/                   # Data Transfer Objects
│   ├── model/                 # Domain logic
│   ├── mqtt/                  # MQTT publisher and subscriber logic
│   ├── persistence/           # In-memory repository for state tracking
│   ├── config/                # Configuration files (YAML)
│   └── main.py                # Entry point for the microservice
├── tests/                     # Unit and integration tests
├── Dockerfile                 # Containerization
├── requirements.txt           # Python dependencies
└── README.md                  # You're here
```

---

## 🔁 Job Lifecycle Overview

### 1. **Printer Discovery**
At startup, the service waits **30 seconds** to listen to all available printers broadcasting their idle status. These are marked as "available".

### 2. **Job Assignment Loop**
Continuously:
- Checks for available printers.
- Sends HTTP `GET /prioritary_job` to the Queue Manager.
- If a job is returned, it assigns the job to a printer by publishing an MQTT message to:

  ```
  device/printer/<printer-id>/assignement
  ```

#### Example Job Response
```json
{
  "id": "job-123",
  "modelId": "model-456",
  "assignedPrinterId": null,
  "priority": 10,
  "status": "pending",
  "submittedAt": "2025-06-15T08:30:00Z",
  "updatedAt": "2025-06-15T08:30:00Z"
}
```

#### Example Assignment
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

### 3. **Printer Progress Monitoring**
Printers report progress via:

```
device/printer/<printer-id>/progress
```

#### Example Progress
```json
{
  "printerId": "printer-1",
  "jobId": "job-123",
  "status": "printing",
  "progress": 42,
  "timestamp": "2025-06-15T08:32:00Z"
}
```

Printers reaching `progress: 100` and status `idle` will be broadcast to:

```
device/printers
```

### 4. **Robot Cleaning & Completion**
Robots listen and act on this list. Once they complete cleaning, they report back:

```
device/robot/<robot-id>/progress
```

#### Example Robot Progress
```json
{
  "robotId": "rob-1",
  "printerId": "printer-1",
  "action": "pick",
  "status": "completed",
  "timestamp": "2025-06-15T08:32:10Z"
}
```

Once the status is `completed`, the job handler marks that printer as available again, completing the cycle.

---

# JobHandler

The `JobHandler` class manages the orchestration of print jobs in an automated 3D print farm. It communicates with printers and cleaning robots using MQTT, fetches jobs from a REST-based queue manager, and manages job assignments and printer states.

---

## Features

* Discovers available 3D printers via MQTT
* Requests and assigns high-priority print jobs
* Tracks printer job progress and robot cleaning status
* Maintains printer availability status
* Publishes job assignments and printer updates

---

## Initialization

```python
JobHandler(broker_host: str, broker_port: int, queue_manager_url: str)
```

### Parameters

* `broker_host`: The hostname or IP address of the MQTT broker
* `broker_port`: The port number used by the MQTT broker
* `queue_manager_url`: URL of the job queue manager REST API

---

## Public Methods

### `start()`

Starts the job handler:

* Connects to the MQTT broker
* Runs the discovery phase to find available printers
* Enters the main loop to assign jobs

---

### `discovery_phase()`

Scans for available printers over a predefined period (`discovery_time`). Printers send progress updates via MQTT, and idle printers are registered.

---

### `main_loop()`

Continuously checks for available printers and pending jobs:

* If printers are available, requests a job
* Assigns the job to an idle printer
* Waits briefly before the next iteration

---

### `request_job() -> Optional[Job]`

Sends a GET request to the queue manager to fetch a high-priority job.

* Returns a `Job` object if available
* Returns `None` if no jobs are currently available

---

### `assign_job_to_printer(printer_id: str, job: Job)`

Builds an `Assignment` DTO and publishes it to the specified printer over MQTT.

* Marks the printer as busy in the internal repository

---

### `on_printer_progress(progress: PrinterProgress)`

Handles MQTT messages from printers:

* Marks printers as idle, busy, or awaiting cleaning
* If job is completed, notifies robot manager for cleaning

---

### `on_robot_progress(progress: RobotProgress)`

Handles MQTT messages from cleaning robots:

* Once cleaning is complete, marks the printer as available again

---

### `stop()`

Stops the job handler:

* Disconnects from MQTT publisher and subscriber
* Logs the shutdown

---

## Integration

This class is meant to work as part of a larger system involving:

* MQTT-connected 3D printers and robots
* A RESTful queue manager
* Internal repositories for tracking printer/job status

---



## 🐳 Docker

To build and run the service in a container:

```bash
docker build -t job-handler .
docker run -e BROKER_HOST=localhost -e QUEUE_MANAGER_URL=http://your-queue-manager job-handler
```

---

## ⚙️ Configuration

Edit `config/job_handler_config.yaml` to set parameters like MQTT broker, ports, and queue manager URLs.

---

## ✅ Requirements

Install Python requirements using:

```bash
pip install -r requirements.txt
```

---

