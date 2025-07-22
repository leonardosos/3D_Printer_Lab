# Priority Queue Management Microservice

The **Priority Queue Management** microservice 

the priority queue manager does the following operations:

- receives HTTP POST /jobs requests from api-gateway and stores the jobs internally
- receives HTTP GET /jobs requests from api-gateway and sends all the job
- receives HTTP PUT /jobs/{jobId} from api-gateway which receives a new priority (criteria for the sorting) for a certain jobId
- receive HTTP DELETE /jobs/{jobId} from api-gateway which deletes a stored job using its jobId for identification
- receives HTTP GET/jobs from job_handler, which has the same output as for the api-gateway response
- receives HTTP GET/prioritaty_job/ from job_handler, sends to him the highest priority job actually stored 
- each job that is stored internally is ranked on its priority from high to low (high first)
- each time a prioritary job is requested and retrieved by job handler, it follows a consumer list approach, in which when the first element is retrieved it is destroyed and the second element becomes the first.

also:

- it should work in a docker compose situation
- it should have a dockerfile
- it should have a yaml config
- it should provide logging and basic error handling





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

### GET `/prioritary_job`

Retrieves the job with the highest priority.

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

