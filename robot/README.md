# 🤖 Robot Device Microservice

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Communication Protocol](#communication-protocol)
  - [MQTT Topics](#mqtt-topics)
  - [Message Structure](#message-structure)
- [Operation Workflow](#operation-workflow)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Overview

This microservice implements a Cartesian robot device that handles the physical task of unloading completed prints from 3D printers in the laboratory. The robot can navigate to specific coordinates, pick up printed objects, transport them to a designated unloading area, and return to its home position.

While the current implementation includes only one robot instance, the modular architecture supports multiple robots by initializing them with distinct IDs in the Docker Compose configuration.

## Features

- **Coordinate-based Navigation**: Moves to specific X, Y, Z coordinates using path planning
- **Automated Actions**: Performs pick, place, and return operations
- **Real-time Status Updates**: Publishes progress and status information
- **Error Handling**: Detects and reports operation failures
- **Configurable Parameters**: Customizable home position, speed, and unloading area
- **Scalable Design**: Supports multiple robot instances

## Architecture

The robot microservice follows a modular architecture with the following components:

```mermaid
classDiagram
    class RobotController {
        -String robotId
        -MqttClient mqttClient
        -CoordinateValidator validator
        -PathPlanner pathPlanner
        -RobotState state
        +initialize()
        +subscribeToTopics()
        +handleCoordinateMessage()
        +moveToCoordinates()
        +performAction()
        +publishProgress()
    }
    
    class CoordinateValidator {
        +validate(CoordinateDTO dto)
    }
    
    class PathPlanner {
        -Point3D currentPosition
        +calculatePath(Point3D target)
        +estimateTimeToTarget()
    }
    
    class RobotState {
        -Point3D position
        -RobotAction currentAction
        -ActionStatus status
        +updatePosition()
        +updateAction()
        +updateStatus()
    }
    
    class CoordinateDTO {
        +String robotId
        +double x
        +double y
        +double z
        +int speed
        +String timestamp
    }
    
    class ProgressDTO {
        +String robotId
        +String action
        +String status
        +String timestamp
    }
    
    RobotController --> CoordinateValidator
    RobotController --> PathPlanner
    RobotController --> RobotState
    CoordinateValidator --> CoordinateDTO
    RobotController --> ProgressDTO
```

## Communication Protocol

The robot device communicates exclusively using the MQTT protocol, providing a lightweight and reliable publish/subscribe messaging system.

### MQTT Topics

#### Subscribed Topics
The robot subscribes to:
```
device/robot/{robotId}/coordinates
```

#### Published Topics
The robot publishes to:
```
device/robot/{robotId}/progress
```

### Message Structure

All messages use JSON format for data interchange.

#### Coordinate Command (Incoming)

```json
{
  "robotId": "rob-1",
  "x": 120,
  "y": 45,
  "z": 10,
  "speed": 200,
  "timestamp": "2025-06-15T08:32:05Z"
}
```

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `robotId` | String | Unique identifier for the robot | Yes |
| `x` | Number | X-coordinate in millimeters | Yes |
| `y` | Number | Y-coordinate in millimeters | Yes |
| `z` | Number | Z-coordinate in millimeters | Yes |
| `speed` | Number | Movement speed in mm/s | No |
| `timestamp` | String | ISO 8601 formatted timestamp | Yes |

#### Progress Update (Outgoing)

```json
{
  "robotId": "rob-1",
  "action": "pick",
  "status": "in_progress",
  "timestamp": "2025-06-15T08:32:10Z"
}
```

| Field | Type | Description | Possible Values |
|-------|------|-------------|----------------|
| `robotId` | String | Unique identifier for the robot | Any valid robot ID |
| `action` | String | Current action being performed | `pick`, `place`, `idle` |
| `status` | String | Status of the current action | `in_progress`, `completed`, `error` |
| `timestamp` | String | ISO 8601 formatted timestamp | Current time |

## Operation Workflow

The robot follows a defined sequence of operations:

1. **Initialization**:
   - Load configuration parameters
   - Connect to MQTT broker
   - Subscribe to coordinate topic
   - Set initial state to idle

2. **Coordinate Reception**:
   - Receive coordinate message
   - Validate message format and values
   - Parse target coordinates and optional parameters

3. **Navigation**:
   - Calculate path to target coordinates
   - Begin movement
   - Publish status updates during transit
   - Arrive at 3D printer location

4. **Pick Operation**:
   - Publish "pick" action with "in_progress" status
   - Execute pick operation sequence
   - Retrieve printed object
   - Publish "pick" action with "completed" status

5. **Transport**:
   - Calculate path to unloading area
   - Navigate to unloading area
   - Publish status updates during transit

6. **Place Operation**:
   - Publish "place" action with "in_progress" status
   - Execute place operation sequence
   - Deposit printed object
   - Publish "place" action with "completed" status

7. **Return to Home**:
   - Calculate path to home position
   - Navigate to home position
   - Publish "idle" action with "completed" status
   - Ready for next task

## Configuration

The robot can be configured using environment variables and a configuration file:

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROBOT_ID` | Unique identifier for the robot | `rob-1` |
| `MQTT_BROKER_HOST` | Hostname of the MQTT broker | `broker` |
| `MQTT_BROKER_PORT` | Port of the MQTT broker | `1883` |
| `HOME_X` | X-coordinate of home position | `0` |
| `HOME_Y` | Y-coordinate of home position | `0` |
| `HOME_Z` | Z-coordinate of home position | `0` |

### Configuration File

```yaml
robot:
  id: "rob-1"
  default_speed: 150
  max_speed: 300
  acceleration: 50
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

### Docker Container

```yaml
robot:
  build:
    context: ./robot
  container_name: robot-container
  restart: always
  volumes:
    - ./robot/config:/app/config
  environment:
    - ROBOT_ID=rob-1
  networks:
    - iot_network
```

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the robot service
python robot_service.py
```

## Development

### Required Dependencies

- Python 3.9+
- Paho MQTT Client
- PyYAML
- Dataclasses

### Testing

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest integration_tests/
```

## Troubleshooting

### Common Issues

1. **Connection Issues**:
   - Verify MQTT broker is running
   - Check network connectivity
   - Confirm correct broker hostname and port

2. **Message Not Received**:
   - Verify topic subscription
   - Check message format (valid JSON)
   - Ensure correct robotId in messages

3. **Unexpected Behavior**:
   - Check logs for validation errors
   - Verify configuration parameters
   - Restart the robot service

For more assistance, please refer to the main project documentation or contact the development team.