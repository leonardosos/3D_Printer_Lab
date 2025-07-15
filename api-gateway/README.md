# 🚪 API Gateway Microservice

This project implements an **API Gateway** that receives HTTP requests from a Web UI and routes them to the appropriate backend microservices. It acts as a single entry point for all client requests, handling routing, validation, data transformation, and optional security features like authentication and rate limiting.

---

## 📌 Features

- Receives HTTP requests from the frontend
- Routes requests to the appropriate backend service
- Transforms request/response payloads via DTOs
- Can handle authentication, logging, and rate limiting (optional)
- Configurable via environment variables
- Containerized with Docker

---

## 🏗️ Microservice Structure

api-gateway/
├── app/
│ ├── main.py # Entry point of the application
│ ├── config/ # Configuration and environment settings
│ ├── routes/ # API Gateway endpoints (UI-facing)
│ ├── services/ # Microservice communication logic
│ ├── dtos/ # Data models for request/response validation
│ ├── utils/ # Logging, error handling, etc.
│ └── middleware/ # (Optional) Auth, CORS, rate limiting
├── tests/ # Unit and integration tests
├── Dockerfile # Docker image definition
├── docker-compose.yml # Orchestrates gateway and other services
├── .env # Environment variables for local dev
├── requirements.txt # Python dependencies
└── README.md # This file


---

## 🚀 How to Run the Project

### 1. 🧱 Prerequisites

- Docker & Docker Compose installed
- Python 3.10+ (if running locally)
- Backend microservices already running or mocked

---

### 2. 🔧 Setup Environment

Create a `.env` file in the project root:

USER_SERVICE_URL=http://user-service:5001
ORDER_SERVICE_URL=http://order-service:5002
GATEWAY_PORT=8080


---

### 3. 🐳 Run with Docker Compose

```bash
docker-compose up --build
```

This will:

- Build the API Gateway container
- Launch it on port 8080
- Connect to user-service and order-service

### 4. 🔍 API Endpoints
Once the gateway is up, access endpoints like:

bash
Copy
Edit
GET http://localhost:8080/printer monitoring
GET http://localhost:8080/global temperature
The gateway will forward these to:

- http://user-service:5001/users/123

- http://order-service:5002/orders/456