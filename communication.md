# Unified Message Schemas for 3D Printer Farm Microservices

## Overview

Below is a proposed set of message‐types and JSON schemas for all of the HTTP and MQTT interactions in your 3D-printer-farm microservice architecture. Each "type" has a name, a list of fields (with types) and a small example payload.

Every microservice or device can validate incoming JSON against the appropriate schema and serialize outgoing data in a consistent, self-describing format.

## Table of Contents

1. [HTTP APIs (JSON over REST)](#1-http-apis-json-over-rest)
    - [1.1 Queue Manager (jobs)](#11-queue-manager-jobs)
        - [1.1.1 GET /jobs](#111-get-jobs)
        - [1.1.2 POST /jobs](#112-post-jobs)
        - [1.1.3 PUT /jobs/{jobId}](#113-put-jobsjobid)
        - [1.1.4 DELETE /jobs/{jobId}](#114-delete-jobsjobid)
    - [1.2 Global Temperature Service](#12-global-temperature-service)
        - [1.2.1 GET /temperature/global](#121-get-temperatureglobal)
    - [1.3 Printer Monitoring Service](#13-printer-monitoring-service)
        - [1.3.1 GET /printers/status](#131-get-printersstatus)
2. [MQTT Topics (JSON payloads)](#2-mqtt-topics-json-payloads)
    - [2.1 Temperature Readings](#21-temperature-readings)
        - [2.1.1 device/room/temperature](#211-topic-deviceroomtemperature)
        - [2.1.2 device/printer/{printerId}/temperature](#212-topic-deviceprinterprinteridtemperature)
    - [2.2 Print Job Assignment & Progress](#22-print-job-assignment--progress)
        - [2.2.1 device/printers](#221-topic-deviceprinters)
        - [2.2.2 device/printer/{printerId}/progress](#222-topic-deviceprinterprinteridprogress)
        - [2.2.3 device/printer/{printerId}/assignment](#223-topic-deviceprinterprinteridassignment)
    - [2.3 Robot (Plate-Changer) Coordination](#23-robot-plate-changer-coordination)
        - [2.3.1 device/robot/{robotId}/coordinates](#231-topic-devicerobotrobotidcoordinates)
        - [2.3.2 device/robot/{robotId}/progress](#232-topic-devicerobotrobotidprogress)
    - [2.4 Fan Control & Safety](#24-fan-control--safety)
        - [2.4.1 device/fan/controller/status](#241-topic-devicefancontrollerstatus)
        - [2.4.2 device/fan/{fanId}/speed](#242-topic-devicefanfanidspeed)
        - [2.4.3 device/fan/controller/emergency](#243-topic-devicefancontrolleremergency)
3. [MQTT QoS (Quality of Service) Levels](#3-mqtt-qos-quality-of-service-levels)
    - [Recap of MQTT QoS Levels](#recap-of-mqtt-qos-levels)
    - [Summary Table](#summary-table)
    - [Reasons for QoS Choices](#reasons-for-qos-choices)

---

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
{ "temperatures": TemperatureReading[], "lastUpdated": "string" }
```

**TemperatureReading Schema:**

- `temperature` - number (°C)
- `source` - "room" | "printer"
- `sourceId` - string (sensor ID or printer ID)
- `timestamp` - string (ISO 8601)

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

**Type:** TemperatureReadingRoom

- `sensorId` - string
- `temperature` - number (°C)
- `unit` - "C" (fixed)
- `timestamp` - string (ISO 8601)

**Example:**

```json
{ "sensorId": "room-sensor-1", "temperature": 22.9, "unit": "C", "timestamp": "2025-06-15T08:31:20Z" }
```

#### 2.1.2 Topic: device/printer/{printerId}/temperature

**Type:** TemperatureReadingPrinter

- `printerId` - string
- `temperature` - number (°C)
- `unit` - "C" (fixed)
- `timestamp` - string (ISO 8601)

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

#### 2.2.1 Topic: device/printers

**Type:** PrinterStatusUpdate

- `printers` – array of objects:
  - `printerId` – string
  - `status` – "work" | "finish"
  - `timestamp` – string (ISO 8601)

**Example:**

```json
{
  "printers": [
    { "printerId": "printer-1", "status": "work", "timestamp": "2025-07-09T10:00:00Z" },
    { "printerId": "printer-2", "status": "finish", "timestamp": "2025-07-09T10:00:00Z" },
    { "printerId": "printer-3", "status": "work", "timestamp": "2025-07-09T10:00:00Z" }
  ]
}
```

#### 2.2.2 Topic: device/printer/{printerId}/progress

Printer publishes its status on this topic. See [Printer Readme](../printers/README.md) for details.

When the printer is actively printing, it sends updates on the job progress. This includes the current job ID, status, and progress percentage.

When the printer is idle (no job is active or assigned), including on start-up, it **periodically** sends a status update with:

- `printerId`: the printer's ID
- `status`: "idle"
- `jobId`: empty string
- `progress`: 100%

When the printer completes a job, it sends a status update with status "completed" and the just completed job ID.

**Type:** PrinterProgress

- `printerId` - string
- `jobId` - string
- `status` - "printing"|"idle"|"completed"|"error"
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

#### 2.2.3 Topic: device/printer/{printerId}/assignment

**Type:** PrinterAssignment

- `jobId` - string
- `modelUrl` - string (URL to GCODE/model file)
- `filamentType` - string
- `estimatedTime` - number (seconds)
- `priority` - number
- `assignedAt` - string (ISO 8601)
- `parameters` - dictionary
  - `layerHeight` - number (mm)
  - `infill` - number (percentage)
  - `nozzleTemp` - number (°C)

**Example:**

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
  }
}
```

### 2.3 Robot (Plate-Changer) Coordination

#### 2.3.1 Topic: device/robot/{robotId}/coordinates

**Type:** RobotCommand

- `robotId` - string
- `printerId` – string
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
- `printerId` – string
- `jobId?` - string (if tied to a print/job)
- `action` - "pick"|"place"|"idle"
- `status` - "in_progress"|"completed"|"error"
- `timestamp` - string (ISO 8601)

**Example:**

```json
{ "robotId": "rob-1", "action": "pick", "status": "in_progress", "timestamp": "2025-06-15T08:32:10Z" }
```

### 2.4 Fan Control & Safety

#### 2.4.1 Topic: device/fan/controller/status

The global temperature service publishes to the fan controller, an interpreted temperature level in order to communicate the need for cooling (handled by the fan controller).

It is not an emergency cooling command, but a **periodic** heat level based on temperature analysis.

**Type:** FanControllerTemp

- `heat_level` - number (0–10) (0 = no cooling needed, 10 = maximum cooling)
- `timestamp?` - string (ISO 8601, optional)

**Example:**

```json
{ "heat_level": 75, "timestamp": "2025-06-15T08:32:15Z" }
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

- `action` - "emergency" | "emergency_finished"
- `type` - "overheat"|"thermal_runaway"  #Thermal runaway is a too rapid temperature increase (increase rate)
- `source` - "printer"|"room"
- `id` - string (e.g. printerId or sensorId)
- `timestamp` - string (ISO 8601)

**Example:**

```json
{ "action": "emergency", "type": "overheat", "source": "printer", "id": "printer-2", "timestamp": "2025-06-15T08:32:20Z" }
```

## 3. MQTT QoS (Quality of Service) Levels

### Recap of MQTT QoS Levels

- **QoS 0 (At most once)**:
The message is delivered once, with no confirmation. It may be lost if the client or broker disconnects. Fastest, but least reliable.

- **QoS 1 (At least once)**:
The message is delivered at least once, with confirmation. It may be delivered multiple times (duplicates possible), but delivery is guaranteed.

- **QoS 2 (Exactly once)**:
The message is delivered exactly once, using a handshake process. Most reliable, prevents duplicates, but has the highest overhead. Used for critical commands.

### Summary Table

| Topic                                   | Schema Type                           | QoS   |
|------------------------------------------|--------------------------------------|-------|
| device/room/temperature                  | 2.1.1) TemperatureReadingRoom        | Qos 0 |
| device/printer/{printerId}/temperature   | 2.1.2) TemperatureReadingPrinter     | Qos 1 |
| device/printers                          | 2.2.1) PrinterStatusUpdate           | Qos 0 |
| device/printer/{printerId}/progress      | 2.2.2) PrinterProgress               | Qos 0 |
| device/printer/{printerId}/assignment    | 2.2.3) PrinterAssignment             | Qos 1 |
| device/robot/{robotId}/coordinates       | 2.3.1) RobotCommand                  | Qos 0 |
| device/robot/{robotId}/progress          | 2.3.2) RobotProgress                 | Qos 0 |
| device/fan/controller/status             | 2.4.1) FanControllerTemp             | Qos 0 |
| device/fan/{fanId}/speed                 | 2.4.2) FanSpeedStatus                | Qos 1 |
| device/fan/controller/emergency          | 2.4.3) EmergencyCommand              | Qos 2 |

### Reasons for QoS Choices

- **device/room/temperature** (QoS 0):  
  Room temperature readings are important for monitoring but not critical. QoS 0 is chosen for speed and low overhead. Occasional loss is acceptable, and consumers do not need to handle duplicates.

- **device/printer/{printerId}/temperature** (QoS 1):  
  Printer temperature readings are needed for safety and monitoring. QoS 1 guarantees delivery, so temperature data is not lost. Consumers must be able to handle possible duplicate messages -> **using timestamp**.

- **device/printers** (QoS 0):  
  Printer status updates are sent frequently. Occasional loss is acceptable, so QoS 0 is used for speed and low overhead. No need to handle duplicates.

- **device/printer/{printerId}/progress** (QoS 0):  
  Progress updates are sent often. If a message is lost, the next update will arrive soon. QoS 0 minimizes network load. No need to handle duplicates.

- **device/printer/{printerId}/assignment** (QoS 1):  
  Print job assignments are critical and must be delivered reliably. QoS 1 ensures at least one delivery. Consumers must handle possible duplicate assignments to avoid processing the same job twice -> **using Job ID**.

- **device/robot/{robotId}/coordinates** (QoS 0):  
  Robot movement commands are sent rapidly. If a message is lost, the next command will update the robot. QoS 0 is sufficient. No need to handle duplicates.

- **device/robot/{robotId}/progress** (QoS 0):  
  Robot progress updates are frequent and not critical. QoS 0 reduces latency and network usage. No need to handle duplicates.

- **device/fan/controller/status** (QoS 0):  
  Fan status is updated regularly. Loss of a single message is not important, so QoS 0 is chosen. No need to handle duplicates.

- **device/fan/{fanId}/speed** (QoS 1):  
  Fan speed commands should be delivered reliably, but duplicates can be handled. QoS 1 ensures at least one delivery. Consumers must handle possible duplicate speed commands -> **using timestamp**.

- **device/fan/controller/emergency** (QoS 2):  
  Emergency commands (shutdown/restart) must be delivered exactly once to **avoid unsafe** repeated actions. QoS 2 prevents duplicates, so consumers do not need to handle them.
