# API Gateway

## 📑 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [API Endpoints](#api-endpoints)
   - [Temperature Endpoints](#temperature-endpoints)
   - [Job Queue Endpoints](#job-queue-endpoints)
   - [Printer Status Endpoints](#printer-status-endpoints)
   - [Health Check Endpoint](#health-check-endpoint)
5. [Data Models](#data-models)
6. [Configuration](#configuration)
7. [Development Guide](#development-guide)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [Error Handling](#error-handling)
11. [Security Considerations](#security-considerations)
12. [Performance Optimization](#performance-optimization)
13. [Future Enhancements](#future-enhancements)

## Overview

The API Gateway serves as the central entry point for the 3D Printers Lab management system. It routes HTTP requests from the web-UI to the appropriate microservices, providing a unified interface while abstracting the underlying microservice architecture.

Key responsibilities:
- Request routing and forwarding
- Response transformation and validation
- Error handling and standardization
- Health monitoring
- Request logging

## Architecture

```
                  ┌─────────────────────┐
                  │                     │
                  │      Web UI         │
                  │                     │
                  └─────────┬───────────┘
                            │
                            │ HTTP
                            ▼
                  ┌─────────────────────┐
                  │                     │
                  │    API Gateway      │
                  │                     │
                  └─────────┬───────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
┌──────────────────┐  ┌──────────────┐ ┌───────────────┐
│                  │  │              │ │               │
│Global Temperature│  │Priority Queue│ │Printer        │
│ Service          │  │Manager       │ │Monitoring     │
│                  │  │              │ │               │
└──────────────────┘  └──────────────┘ └───────────────┘
```

### Component Structure

```
api-gateway/
├── app/                   # Application code
│   ├── __init__.py
│   ├── main.py            # Application entry point
│   ├── dto/               # Data Transfer Objects
│   │   ├── __init__.py
│   │   ├── create_job_dto.py
│   │   ├── job_dto.py
│   │   ├── printer_status_dto.py
│   │   ├── temperature_dto.py
│   │   └── update_job_dto.py
│   ├── routes/            # API route definitions
│   │   ├── __init__.py
│   │   ├── jobs.py
│   │   ├── printers.py
│   │   └── temperature.py
│   ├── services/          # Microservice communication
│   │   ├── __init__.py
│   │   ├── printer_service.py
│   │   ├── queue_service.py
│   │   └── temperature_service.py
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── error_handler.py
│       ├── request_forwarder.py
│       └── service_exception.py
├── config/                # Configuration files
│   └── config.yaml
├── logs/                  # Log files directory
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
├── run.py                 # Script to run the application
└── README.md              # This file
```

## Features

- **Centralized Routing**: Routes requests from the Web UI to appropriate microservices
- **Data Validation**: Validates requests and responses using DTOs
- **Error Handling**: Standardized error responses and logging
- **Service Discovery**: Configured service endpoints with easy updates
- **Health Monitoring**: Health check endpoint for monitoring
- **Logging**: Comprehensive logging for troubleshooting
- **Containerization**: Docker support for easy deployment
- **Environment Variable Override**: Configuration can be overridden with environment variables

## API Endpoints

### Temperature Endpoints

#### `GET /temperature/global`

Retrieves temperature data from all temperature sensors (room and printers).

**Response Example:**

```json
{
  "temperatures": [
    { 
      "temperature": 22.7, 
      "source": "room", 
      "sourceId": "room-sensor-1", 
      "timestamp": "2023-11-10T14:30:00Z" 
    },
    { 
      "temperature": 205.3, 
      "source": "printer", 
      "sourceId": "printer-1", 
      "timestamp": "2023-11-10T14:30:00Z" 
    }
  ],
  "lastUpdated": "2023-11-10T14:30:00Z"
}
```

### Job Queue Endpoints

#### `GET /jobs`

Retrieves all jobs in the queue.

**Response Example:**

```json
{
  "jobs": [
    {
      "id": "job-123",
      "modelId": "model-456",
      "assignedPrinterId": null,
      "priority": 10,
      "status": "pending",
      "submittedAt": "2023-11-10T12:30:00Z",
      "updatedAt": "2023-11-10T12:30:00Z"
    }
  ]
}
```

#### `POST /jobs`

Creates a new print job.

**Request Example:**

```json
{
  "modelId": "model-789",
  "printerId": "printer-1",
  "priority": 5
}
```

**Response Example:**

```json
{
  "modelId": "model-789",
  "priority": 5
}
```

#### `PUT /jobs/{job_id}`

Updates an existing job (e.g., priority change).

**Request Example:**

```json
{
  "priority": 15
}
```

**Response Example:**

```json
{
  "job": {
    "id": "job-123",
    "modelId": "model-456",
    "assignedPrinterId": null,
    "priority": 15,
    "status": "pending",
    "submittedAt": "2023-11-10T12:30:00Z",
    "updatedAt": "2023-11-10T12:35:00Z"
  }
}
```

#### `DELETE /jobs/{job_id}`

Deletes a job from the queue.

**Response Status: 204 No Content**

### Printer Status Endpoints

#### `GET /printers/status`

Retrieves the status of all printers.

**Response Example:**

```json
{
  "printers": [
    {
      "printerId": "printer-1",
      "status": "printing",
      "currentJobId": "job-123",
      "progress": 42,
      "temperature": 205.3,
      "lastUpdated": "2023-11-10T14:30:00Z"
    }
  ]
}
```

### Health Check Endpoint

#### `GET /health`

Checks if the API Gateway is operational.

**Response Example:**

```json
{
  "status": "ok",
  "service": "api-gateway",
  "version": "1.0.0"
}
```

## Data Models

The API Gateway uses Data Transfer Objects (DTOs) to validate and transform data:

### Job DTOs

- **JobDTO**: Represents a job in the queue
- **JobsResponseDTO**: Contains a list of jobs
- **CreateJobRequestDTO**: Validates job creation requests
- **CreateJobResponseDTO**: Formats job creation responses
- **UpdateJobRequestDTO**: Validates job update requests
- **UpdateJobResponseDTO**: Formats job update responses

### Temperature DTOs

- **TemperatureReadingDTO**: Represents a single temperature reading
- **TemperatureResponseDTO**: Contains a list of temperature readings

### Printer Status DTOs

- **PrinterStatusDTO**: Represents the status of a printer
- **PrinterStatusResponseDTO**: Contains a list of printer statuses

## Configuration

The API Gateway is configured through a YAML file at `config/config.yaml`:

```yaml
# API Gateway Configuration
server:
  host: '0.0.0.0'
  port: 8080
  debug: false

services:
  global_temperature:
    base_url: 'http://global-temperature-service:8100'
    endpoints:
      get_temperatures: '/temperature'
  
  priority_queue:
    base_url: 'http://priority-queue-manager:8090'
    endpoints:
      get_jobs: '/jobs'
      add_job: '/jobs'
      update_job: '/jobs/{job_id}'
      delete_job: '/jobs/{job_id}'
  
  printer_monitoring:
    base_url: 'http://printer-monitoring:8110'
    endpoints:
      get_status: '/printers/status'

logging:
  level: 'INFO'
  file: 'logs/api-gateway.log'
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  max_size: 10485760  # 10MB
  backup_count: 5     # Keep 5 backup files
```

### Environment Variable Overrides

Configuration settings can be overridden with environment variables:

| Environment Variable           | Configuration Setting                              |
|--------------------------------|---------------------------------------------------|
| API_GATEWAY_PORT              | server.port                                        |
| GLOBAL_TEMP_SERVICE_URL       | services.global_temperature.base_url               |
| PRIORITY_QUEUE_SERVICE_URL    | services.priority_queue.base_url                   |
| PRINTER_MONITORING_SERVICE_URL| services.printer_monitoring.base_url               |

## Development Guide

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd IoT_Project/api-gateway
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the API Gateway:
   ```bash
   python run.py
   ```

### Adding a New Endpoint

1. Add the endpoint configuration to `config/config.yaml`
2. Create or update the relevant DTO in the `app/dto/` directory
3. Add the route handler in the appropriate file in `app/routes/`
4. Add the service method in the appropriate file in `app/services/`
5. Register the new route in `app/main.py` if needed

### Code Style Guidelines

- Follow PEP 8 for Python code style
- Use docstrings for functions and classes
- Add type hints where possible
- Write unit tests for new functionality

## Deployment

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t api-gateway .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 -v $(pwd)/config:/app/config -v $(pwd)/logs:/app/logs api-gateway
   ```

### Using Docker Compose

Add the API Gateway service to your `docker-compose.yml` file:

```yaml
api-gateway:
  build:
    context: ./api-gateway
  ports:
    - "8080:8080"
  volumes:
    - ./api-gateway/config:/app/config
    - ./api-gateway/logs:/app/logs
  networks:
    - iot-network
  depends_on:
    - global-temperature-service
    - priority-queue-manager
    - printer-monitoring
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 5s
```

Then run:

```bash
docker-compose up -d
```

## Troubleshooting

### Common Issues

#### API Gateway Cannot Connect to Microservices

- Check that the service names in `config.yaml` match the service names in Docker Compose
- Ensure all services are on the same Docker network
- Verify that the target services are running

#### Configuration Issues

- Check for YAML syntax errors in the configuration file
- Ensure the configuration file is properly mounted as a volume in Docker

#### Error Responses from Microservices

- Check the logs of both the API Gateway and the target microservice
- Verify that the request format matches what the microservice expects

### Logging

Logs are stored in the `logs/` directory. The default log file is `api-gateway.log`.

To view logs in a running Docker container:

```bash
docker logs <container-id>
```

Or when using Docker Compose:

```bash
docker-compose logs api-gateway
```

## Error Handling

The API Gateway uses a standardized error response format:

```json
{
  "error": {
    "code": 404,
    "message": "Resource not found",
    "details": "Job with ID 'job-999' does not exist"
  }
}
```

Common HTTP status codes:

- 200: Success
- 201: Created
- 204: No Content (for successful DELETE operations)
- 400: Bad Request (client error)
- 404: Not Found
- 500: Internal Server Error
- 503: Service Unavailable

## Security Considerations

- The API Gateway does not currently implement authentication or authorization
- For production use, consider adding:
  - API keys or JWT authentication
  - Rate limiting
  - HTTPS encryption
  - Input validation and sanitization (already partially implemented with DTOs)

## Performance Optimization

- The API Gateway uses simple request forwarding without caching
- For high-traffic scenarios, consider adding:
  - Response caching for frequently requested data
  - Connection pooling for backend services
  - Load balancing for multiple API Gateway instances

## Future Enhancements

Potential improvements for future versions:

- API documentation integration (Swagger/OpenAPI)
- Authentication and authorization
- Request rate limiting
- Response caching
- Circuit breaker pattern for handling service degradation
- Metrics collection and monitoring integration
- GraphQL support for more flexible data fetching
- WebSocket support for real-time updates