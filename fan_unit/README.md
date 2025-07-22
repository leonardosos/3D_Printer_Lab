# Fan Unit Microservice

This microservice represents a fan unit (device) inside a room. It simulates a fan that can be controlled remotely via MQTT messages, allowing dynamic adjustment of the fan speed.

## Features

- MQTT-based communication
- Speed control from 0-100%
- Current simulation based on speed setting
- Message validation using DTOs
- Configurable via YAML file or environment variables

## Class Structure

- `FanUnit`: The main class that handles MQTT communication and fan operations
- `FanSpeedMessage`: A Pydantic DTO for validating incoming messages

## Folder Structure

```
fan_unit/
├── app/
│   ├── main.py       # Main application logic
│   ├── dto.py        # Data Transfer Objects for message validation
│   └── config.yaml   # Configuration file
├── Dockerfile        # Docker image definition
├── requirements.txt  # Python dependencies
└── README.md         # This documentation
```

## Communication 

- This microservice communicates only with MQTT protocol
- Paho MQTT client is used for communication

## MQTT Broker

The MQTT broker is located at port 1883 and is accessed via the `broker` service name in the Docker network.

### Topics

This device listens over a single topic:

```
device/fan/{fanId}/speed
```

The quality of service is set to QoS=1

### Topic Messages

An example message published over the topic is:

```json
{
  "fanId": "fan1", 
  "speed": 75, 
  "actual": 75, 
  "timestamp": "2025-06-15T08:32:15Z"
}
```

Where:
- `fanId`: Identifier of the fan unit
- `speed`: Target speed expressed as a percentage (0-100)
- `actual`: Current actual speed (optional)
- `timestamp`: ISO 8601 formatted timestamp

## Logic 

1. The microservice subscribes to the topic at startup
2. It waits for messages published to the topic
3. When a message is received, it validates the message with a DTO
4. If valid and intended for this fan, it updates the fan speed
5. Based on the speed value, it calculates a proportional current value
6. In a real implementation, this current would control an open-loop, current-controlled fan

## Configuration

The fan unit can be configured via:

1. The `config.yaml` file
2. Environment variables:
   - `FAN_ID`: The ID of the fan (default: "fan1")
   - `DEBUG`: Enable debug logging (default: False)

## Docker

This microservice has its own Dockerfile for standalone operation, but it can also be integrated into a larger architecture via docker-compose.

### Building and Running

```bash
# Build the Docker image
docker build -t fan-unit .

# Run as standalone container
docker run -d --name fan-unit -e FAN_ID=fan1 fan-unit
```

### Testing

You can test the fan unit by publishing a message to its topic:

```bash
# Using mosquitto_pub
mosquitto_pub -h localhost -t device/fan/fan1/speed -m '{"fanId": "fan1", "speed": 75, "timestamp": "2023-11-17T10:00:00Z"}'

