# Priority Queue Management Microservice

The **Priority Queue Management** microservice handles dynamic job prioritization in a print workflow system. It ensures that job execution follows a strict priority order while supporting real-time job creation, updates, and deletions via a RESTful HTTP API. This service acts as the source of truth for job scheduling decisions, and it integrates tightly with the Web UI and Job Handler microservices.

---

## Features

- Create new jobs with optional priority and printer assignment.
- Update the priority of jobs dynamically.
- Delete individual or multiple jobs in bulk.
- Retrieve the complete list of jobs sorted by highest priority.
- Lightweight, stateless API for Web UI and backend orchestration.

---

## API Endpoints

### POST `/jobs`

Creates a new job and inserts it into the priority queue.

**Request:**
```json
{
  "modelId": "string",
  "printerId": "string",   // optional
  "priority": 5            // optional, default = 0
}
```

**Response:**
```json
{
  "job": {
    "id": "job-123",
    "modelId": "model-789",
    "assignedPrinterId": null,
    "priority": 5,
    "status": "pending",
    "submittedAt": "2025-07-14T09:00:00Z",
    "updatedAt": "2025-07-14T09:00:00Z"
  }
}
```

---

### PUT `/jobs/{jobId}`

Modifies the priority of an existing job.

**Request:**
```json
{
  "priority": 15
}
```

**Response:**
```json
{
  "job": {
    "id": "job-123",
    "modelId": "model-456",
    "assignedPrinterId": null,
    "priority": 15,
    "status": "pending",
    "submittedAt": "2025-06-15T08:30:00Z",
    "updatedAt": "2025-06-15T08:35:00Z"
  }
}
```

---

### DELETE `/jobs/{jobId}`

Deletes a single job by ID.

**Response:**
- HTTP 204 No Content

---

### DELETE `/jobs?ids=job-1,job-2,...`

Deletes multiple jobs by ID in a single request.

**Response:**
- HTTP 204 No Content

---

### GET `/jobs`

Retrieves all jobs sorted from highest to lowest priority.

**Response:**
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

## Data Transfer Objects (DTOs)

Defined using Python `@dataclass` for clarity and type safety.

### `JobRequestDTO`
```python
@dataclass
class JobRequestDTO:
    modelId: str
    printerId: Optional[str] = None
    priority: int = 0
```

### `JobResponseDTO`
```python
@dataclass
class JobResponseDTO:
    id: str
    modelId: str
    assignedPrinterId: Optional[str] = None
    priority: int
    status: str  # pending, queued, in_progress, completed, failed
    submittedAt: datetime
    updatedAt: datetime
```

---

## Core Logic – PriorityQueueService

The `PriorityQueueService` encapsulates all core operations for managing and prioritizing jobs.

```python
class PriorityQueueService:

    def add_job(self, model_id: str, printer_id: str = None, priority: int = 0):
        # Adds a new job to the queue with optional printer and priority

    def update_job_priority(self, job_id: str, new_priority: int):
        # Updates the priority of an existing job and reorders the queue

    def delete_job(self, job_id: str):
        # Deletes a single job by ID

    def delete_multiple_jobs(self, job_ids: list[str]):
        # Bulk delete of multiple jobs

    def get_all_jobs(self) -> list:
        # Returns all jobs sorted by priority

    def get_job_by_id(self, job_id: str) -> dict:
        # Returns a job by its ID

    def reorder_queue(self):
        # Sorts the job queue after priority updates

    def assign_printer_to_job(self, job_id: str, printer_id: str):
        # Assigns a printer to a job

    def update_job_status(self, job_id: str, status: str):
        # Updates the job status (e.g., pending → in_progress)

    def get_next_job(self) -> dict:
        # Returns the highest priority job ready for processing
```

---

## Project Structure

```
priority-queue-management/
├── app/
│   ├── dto/
│   │   ├── job_request_dto.py
│   │   ├── job_response_dto.py
│   ├── routes/
│   │   ├── job_routes.py
│   ├── services/
│   │   ├── priority_queue_service.py
│   ├── config/
│   │   ├── service_conf.yaml
│   ├── main.py
│
├── tests/
│   ├── test_priority_queue.py
│
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Testing

All tests are located in the `tests/` directory. Use `fake_api_response.py` for mocking HTTP responses and testing the service layer in isolation.

---

## Docker Support

To build and run locally via Docker:

```bash
docker build -t priority-queue .
docker run -p 8080:8080 priority-queue
```

---

## Job Status Lifecycle

Jobs may have one of the following statuses:

- `pending`
- `queued`
- `in_progress`
- `completed`
- `failed`

---

## Ownership

This microservice is maintained by the **Backend Team**. For integration or support, please reach out through internal channels. It is intended for internal use only by the Job Handler and Web UI.