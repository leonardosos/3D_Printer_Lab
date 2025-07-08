# 3D Printer Farm Microservice Message Schemas

Below is a proposed set of message‐types and JSON schemas for all of the HTTP and MQTT interactions in your 3D-printer-farm microservice architecture. Each "type" has a name, a list of fields (with types) and a small example payload.

## 1. HTTP APIs (JSON over REST)

### 1.1 Queue Manager (jobs)

#### 1.1.1 GET /jobs

**Response type:**

```json
{ jobs: Job[] }
```

**Job Schema:**

- `id` - string
- `modelId` - string
- `assignedPrinterId?` - string|null
- `priority` - number
- `status` - "pending" | "queued" | "in_progress" | "completed" | "failed"
- `submittedAt` - string (ISO 8601)
- `updatedAt` - string (ISO 8601)

**Example:**

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

#### 1.1.2 POST /jobs

**Request type:**

```json
{
  "modelId": "string",
  "printerId?": "string",    // optional preferred printer
  "priority?": "number"      // default = 0
}
```

**Response type:**

```json
{ "job": Job }
```

**Example request:**

```json
{ "modelId": "model-789", "priority": 5 }
```

#### 1.1.3 PUT /jobs/{jobId}

**Request type:**

```json
{
  "priority?": "number",     // update job priority
  "printerId?": "string"     // reassign to different printer
}
```

**Response type:**

```json
{ "job": Job }
```

**Example request:**

```json
{ "priority": 15 }
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

#### 1.1.4 DELETE /jobs/{jobId}

**Response:** 204 No Content

### 1.2 Global Temperature Service

#### 1.2.1 GET /temperature/global

**Response type:**

```json
{
  "temperatures": [
    {
      "temperature": "number",    // in °C
      "source": "room"|"printer",
      "sourceId": "string",       // sensor ID or printer ID
      "timestamp": "string"       // ISO 8601
    }
  ],
  "lastUpdated": "string"         // ISO 8601
}
```

**Example:**

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

### 1.3 Printer Monitoring Service

#### 1.3.1 GET /printers/status

**Response type:**

```json
{ "printers": PrinterStatus[] }
```

**PrinterStatus Schema:**

- `printerId` - string
- `status` - "idle" | "printing" | "error"
- `currentJobId?` - string
- `progress?` - number (0–100)
- `temperature?` - number (current nozzle temp in °C)
- `lastUpdated` - string (ISO 8601)

**Example:**

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

## 2. MQTT Topics (JSON payloads)

All topics follow the pattern `device/<component>/<ID>/<event>`.

### 2.1 Temperature Readings

#### 2.1.1 Topic: device/room/temperature

**Type:** TemperatureReading

- `sensorId` - string
- `temperature` - number (°C)
- `unit` - "C" (fixed)
- `timestamp` - string (ISO 8601)

**Example:**

```json
{ "sensorId": "room-sensor-1", "temperature": 22.9, "unit": "C", "timestamp": "2025-06-15T08:31:20Z" }
```

#### 2.1.2 Topic: device/printer/{printerId}/temperature

Same schema as above, plus printerId field:

**Example:**

```json
{
  "printerId": "printer-2",
  "temperature": 210.0,
  "unit": "C",
  "timestamp": "2025-06-15T08:31:22Z"
}
```

### 2.2 Print Job Assignment & Progress

#### 2.2.1 Topic: device/printer/{printerId}/assignment

**Type:** PrinterAssignment

- `printerId` - string
- `jobId` - string
- `modelUrl` - string (where to fetch the STL/GCODE)
- `filamentType` - "PLA"|"ABS"|"PETG"|…
- `estimatedTimeSec` - number (in seconds)
- `timestamp` - string (ISO 8601)

**Example:**

```json
{
  "printerId": "printer-1",
  "jobId": "job-123",
  "modelUrl": "https://…/model-456.gcode",
  "filamentType": "PLA",
  "estimatedTimeSec": 3600,
  "timestamp": "2025-06-15T08:31:25Z"
}
```

#### 2.2.2 Topic: device/printer/{printerId}/progress

**Type:** PrinterProgress

- `printerId` - string
- `jobId` - string
- `status` - "printing"|"paused"|"completed"|"error"
- `progress` - number (0–100)
- `timestamp` - string (ISO 8601)

**Example:**

```json
{
  "printerId": "printer-1",
  "jobId": "job-123",
  "status": "printing",
  "progress": 42,
  "timestamp": "2025-06-15T08:32:00Z"
}
```

### 2.3 Robot (Plate-Changer) Coordination

#### 2.3.1 Topic: device/robot/{robotId}/coordinates

**Type:** RobotCommand

- `robotId` - string
- `x` - number (mm)
- `y` - number (mm)
- `z` - number (mm)
- `speed?` - number (mm/s, optional)
- `timestamp` - string (ISO 8601)

**Example:**

```json
{ "robotId": "rob-1", "x": 120, "y": 45, "z": 10, "speed": 200, "timestamp": "2025-06-15T08:32:05Z" }
```

#### 2.3.2 Topic: device/robot/{robotId}/progress

**Type:** RobotProgress

- `robotId` - string
- `jobId?` - string (if tied to a print/job)
- `action` - "pick"|"place"|"idle"
- `status` - "in_progress"|"completed"|"error"
- `timestamp` - string (ISO 8601)

**Example:**

```json
{ "robotId": "rob-1", "action": "pick", "status": "in_progress", "timestamp": "2025-06-15T08:32:10Z" }
```

### 2.4 Fan Control & Safety

#### 2.4.1 Topic: device/fan/controller/speed

**Type:** FanSpeedCommand

- `speed` - number (0–100%)
- `unit` - "percent"
- `timestamp?` - string (ISO 8601, optional)

**Example:**

```json
{ "speed": 75, "unit": "percent" }
```

#### 2.4.2 Topic: device/fan/{fanId}/speed

**Type:** FanSpeedStatus

- `fanId` - string
- `speed` - number (commanded %)
- `actual?` - number (measured RPM or %, optional)
- `timestamp` - string (ISO 8601)

**Example:**

```json
{ "fanId": "fan-1", "speed": 75, "actual": 72, "timestamp": "2025-06-15T08:32:15Z" }
```

#### 2.4.3 Topic: device/fan/controller/emergency

**Type:** EmergencyCommand

- `action` - "shutdown"|"restart"
- `type` - "overheat"|"thermal_runaway"
- `source` - "printer"|"room"
- `id` - string (e.g. printerId or sensorId)
- `timestamp` - string (ISO 8601)

**Example:**

```json
{ "action": "shutdown", "type": "overheat", "source": "printer", "id": "printer-2", "timestamp": "2025-06-15T08:32:20Z" }
```

---

With these definitions in place, every microservice or device can validate incoming JSON against the appropriate schema and serialize outgoing data in a consistent, self-describing format.
