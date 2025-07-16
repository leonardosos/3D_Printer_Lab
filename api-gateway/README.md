# 🚪 API Gateway Microservice

This microservice implements an **API Gateway** that receives HTTP requests from a Web UI and routes them to the appropriate backend microservices. It acts as a **single entry point** for all client interactions, handling:

- Routing
- Request and response validation
- Data transformation
- Optional features like authentication and rate limiting

---

## 📌 Features

- Receives HTTP requests from the frontend Web UI
- Routes requests to the corresponding backend microservices
- Sends back responses to the Web UI
- Validates request/response payloads using Data Transfer Objects (DTOs)
- Containerized using Docker for consistent deployment

---

## 🏗️ Microservice Structure

api-gateway/
├── app/
│ ├── main.py # Entry point of the application
│ ├── routes/ # API Gateway endpoints (UI-facing)
│ ├── services/ # Communication logic with backend services
│ ├── dto/ # Data models for request/response validation
├── Dockerfile # Docker image definition
├── requirements.txt # Python dependencies
└── README.md # This file


---

## 🌐 Service Ports

| Service              | Port  |
|----------------------|-------|
| Web UI               | 8000  |
| API Gateway          | 8080  |
| Queue Manager        | 8090  |
| Global Temperature   | 8100  |
| Printer Monitoring   | 8110  |

---

## 📥 Routes and Behaviors

Below are the routes exposed to the Web UI and how they are routed internally to the corresponding backend microservices.

---

### 1️⃣ Job Management – Queue Manager Microservice (`:8090`)

#### 1.1 `GET /jobs`

Returns the list of jobs.

**Example response:**
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

#### 1.2 `POST /jobs`

Creates a new print job.

**Example request:**
```json
{
  "modelId": "string",
  "printerId": "string",     // Optional preferred printer
  "priority": 0              // Optional, default = 0
}
```

**Example response:**
```json
{
  "modelId": "model-789",
  "priority": 5
}
```

#### 1.3 `PUT /jobs/{jobId}`

Updates an existing job (e.g., priority change).

**Example request:**
```json
{
  "priority": 15
}
```

**Example response:**

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

#### 1.4 DELETE /jobs/{jobId}

Deletes a job.

**Response:**

    204 No Content (if successful)


### 2️⃣ Temperature Monitoring – Global Temperature Microservice (:`8100`)

#### 2.1 `GET /temperature/global`

Retrieves temperature data from rooms and printers.

**Example response:**
```json
{
  "temperatures": [
    { 
      "temperature": 22.7, 
      "source": "room", 
      "sourceId": "room-sensor-1", 
      "timestamp": "2025-06-15T08:31:10Z" 
    },
    { 
      "temperature": 205.3, 
      "source": "printer", 
      "sourceId": "printer-1", 
      "timestamp": "2025-06-15T08:31:15Z" 
    },
    { 
      "temperature": 198.7, 
      "source": "printer", 
      "sourceId": "printer-2", 
      "timestamp": "2025-06-15T08:31:12Z" 
    }
  ],
  "lastUpdated": "2025-06-15T08:31:15Z"
}
```

### 3️⃣ Printer Monitoring – Printer Monitoring Microservice (:`8110`)
#### 3.1 `GET /printers/status`
Returns the current status of all printers.

**Example response:**
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

### 🚀 How to Run the Project

#### ✅ Prerequisites

    Docker

    Docker Compose

### 📦 Dependencies
Install Python dependencies locally (optional for non-containerized testing):
```bash
    pip install -r requirements.txt
```