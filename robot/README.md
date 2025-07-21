# 🤖 Robot Device Microservice

## Overview

This microservice implements a Cartesian robot device responsible for unloading completed prints from 3D printers in the laboratory. The robot navigates to specified coordinates, picks up printed objects, transports them to an unloading area, and returns to its home position.

- **Supports multiple robots:** Each robot instance is initialized with a unique ID and port (configured via Docker Compose).
- **Communication:** Uses MQTT for all messaging.

---

## Architecture

The robot microservice is modular, with clear separation of concerns:

- **MQTT Client:** Handles connection, subscriptions, and publications.
- **DTOs (Data Transfer Objects):** Validate and parse incoming/outgoing messages.
- **Robot Controller:** Orchestrates the robot's operation workflow.
- **Configuration Loader:** Loads environment variables and YAML config.
- **State Machine:** Tracks the robot's current state (idle, navigating, picking, transporting, returning).

### Class Responsibilities

| Class/Module         | Responsibility                                                      |
|----------------------|---------------------------------------------------------------------|
| `MQTTClient`         | Connects to broker, subscribes/publishes to topics                  |
| `CoordinateDTO`      | Validates and parses incoming coordinate commands                   |
| `ProgressDTO`        | Formats outgoing progress messages                                  |
| `RobotController`    | Main logic: receives commands, executes workflow, manages state     |
| `ConfigLoader`       | Loads and validates configuration from env and YAML                 |

---

## Folder Structure
robot/ 
├── app/ 
│ ├── init.py 
│ ├── main.py # Entry point 
│ ├── mqtt_client.py # MQTT client logic 
│ ├── controller.py # RobotController class 
│ ├── dto/ 
│ │ ├── coordinate_dto.py # CoordinateDTO class 
│ │ └── progress_dto.py # ProgressDTO class 
│ ├── config.py # ConfigLoader class 
| ├── config.yaml # Default configuration file
│ └── state.py # State machine logic 
├── Dockerfile 
├── requirements.txt 
└── README.md


## Communication Protocol

### MQTT Topics

- **Subscribed:**  
  `device/robot/{robotId}/coordinates`
- **Published:**  
  `device/robot/{robotId}/progress`

### Message Schemas

#### Coordinate Command (Incoming)

```json
{
  "robotId": "rob-1",
  "printerId": "printer-1",
  "x": 120,
  "y": 45,
  "z": 10,
  "speed": 200,          // optional
  "timestamp": "2025-06-15T08:32:05Z"
}
```

Coordinates in mm.
speed is optional.

#### Progress Update (Outgoing)

```json
{
  "robotId": "rob-1",
  "printerId": "printer-1",
  "action": "idle",      // "pick" | "place" | "idle"
  "status": "completed", // "in_progress" | "completed" | "error"
  "timestamp": "2025-06-15T08:35:45Z"
}
```

## Operation Workflow

### Initialization
Load configuration (env + YAML)
Connect to MQTT broker
Subscribe to coordinate topic
Set initial state to idle

### Coordinate Reception
Receive and validate coordinate message (CoordinateDTO)
Parse target coordinates, printer ID, and optional speed
Store printer ID for progress reporting

### Navigation
Simulate movement to printer position (delay/fake behavior)
(don't publish over topic)

### Pick Operation
Simulate 3d printed object pick (delay/fake behavior)
(don't publish over topic)

### Transport
Read unloading area coordinates from config
Simulate movement to unloading area (delay/fake behavior)
(don't publish over topic)

### Return to Home
Read home position from config
Simulate return (delay/fake behavior)
Publish progress message (ProgressDTO) with action "idle" and status "completed"
Set state to idle, ready for next task


## Configuration
### Environment Variables

| Variable            | Description                | Default     |
|---------------------|----------------------------|-------------|
| ROBOT_ID            | Unique robot identifier    | rob-1       |
| MQTT_BROKER_HOST    | MQTT broker hostname       | broker      |
| MQTT_BROKER_PORT    | MQTT broker port           | 1883        |
| HOME_X              | Home X coordinate          | 0           |
| HOME_Y              | Home Y coordinate          | 0           |
| HOME_Z              | Home Z coordinate          | 0           |

### YAML Configuration Example
```yaml
robot:
  id: "rob-1"
  home_position:
    x: 0
    y: 0
    z: 0
  unloading_area:
    x: 500
    y: 500
    z: 50
mqtt:
  broker_host: "broker"
  broker_port: 1883
  qos: 0
  client_id: "robot-client"
```

## Deployment
### Docker
The microservice is dockerized for easy deployment.

To build the Docker image:
```bash
docker build -t robot-microservice .
```

To run a standalone container:
```bash
docker run -d --name robot \
  -e ROBOT_ID=rob-1 \
  -e MQTT_BROKER_HOST=broker \
  -e MQTT_BROKER_PORT=1883 \
  robot-microservice
```

### Docker Compose
For easy deployment with the whole system, use Docker Compose:

```bash
docker-compose up -d
```

This will start the robot service along with all other microservices.

## Extending for Multiple Robots
To run multiple robot instances, duplicate the robot service in docker-compose.yml with different ROBOT_ID values:

```yaml
robot-2:
  build:
    context: ./robot
    dockerfile: Dockerfile
  container_name: robot-2-container
  volumes:
    - ./robot/app/config.yaml:/app/app/config.yaml
  environment:
    - ROBOT_ID=rob-2
    - MQTT_BROKER_HOST=broker
    - MQTT_BROKER_PORT=1883
  networks:
    - iot_network
```

Each robot listens and publishes on its own topics based on its ROBOT_ID.

## References
- MQTT Protocol
- paho-mqtt Python Client