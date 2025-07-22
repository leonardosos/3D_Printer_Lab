# Room Temperature Sensor Microservice

This microservice simulates a temperature sensor device. It generates realistic temperature data and publishes it to an MQTT broker at regular intervals.

## Architecture

The microservice follows a simple modular architecture:

1. **Main Application**: Coordinates the components and manages the lifecycle
2. **Sensor Simulator**: Generates realistic temperature readings
3. **MQTT Client**: Handles communication with the MQTT broker
4. **Configuration Manager**: Loads and provides access to configuration

### Class Responsibilities

- **SensorSimulator**: 
  - Simulates temperature readings with realistic patterns
  - Maintains current temperature state
  - Generates gradual temperature changes over time
  
- **MQTTClient**:
  - Manages connection to the MQTT broker
  - Handles publishing messages
  - Implements reconnection logic
  
- **ConfigManager**:
  - Loads configuration from YAML file
  - Provides access to configuration parameters
  
- **Application**:
  - Initializes all components
  - Manages the main application loop
  - Handles graceful shutdown

## Folder Structure

```
room_temperature_sensor/
├── app/
│   ├── main.py              # Entry point and application lifecycle
│   ├── sensor.py            # Temperature sensor simulation
│   ├── mqtt_client.py       # MQTT connection handling
│   └── config_manager.py    # Configuration loading and management
├── config/
│   └── config.yaml          # Configuration file
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Communication

### MQTT Protocol

This microservice communicates exclusively using the MQTT protocol via the Paho MQTT library.

### Broker Configuration

- **Host**: Configurable in config.yaml (default: "localhost")
- **Port**: 1883 (standard MQTT port)
- **QoS**: 0 (at most once)
- **Client ID**: Generated using the sensor ID with a random suffix

### Topic

The microservice publishes to a single topic:

```
device/room/temperature
```

### Message Format

Messages are published in JSON format:

```json
{
  "sensorId": "room-sensor-1",
  "temperature": 22.9,
  "unit": "C",
  "timestamp": "2023-11-15T08:31:20Z"
}
```

Fields:
- `sensorId`: Unique identifier for the sensor (from config)
- `temperature`: Current temperature reading (float, in Celsius)
- `unit`: Temperature unit (from config)
- `timestamp`: ISO 8601 formatted timestamp

## Business Logic

### Temperature Simulation

The sensor simulation:

1. Initializes with a random temperature between 18°C and 25°C
2. Every update cycle:
   - Randomly decides to increase or decrease the temperature
   - Changes temperature by a small amount (0.1°C to 0.5°C)
   - Ensures temperature stays within realistic bounds (11°C to 49°C)
   - Applies inertia to prevent unrealistic rapid changes

### Operation Flow

1. Load configuration from YAML file
2. Initialize temperature sensor with configuration parameters
3. Connect to MQTT broker
4. Enter main loop:
   - Generate new temperature reading
   - Create JSON message with temperature data
   - Publish message to MQTT topic
   - Wait for configured interval
5. On shutdown, disconnect from MQTT broker gracefully

## Configuration

The `config.yaml` file should contain:

```yaml
sensor:
  id: "room-sensor-1"
  min_temperature: 11.0
  max_temperature: 49.0
  update_interval_seconds: 5
  
mqtt:
  broker_host: "localhost"
  broker_port: 1883
  topic: "device/room/temperature"
  
logging:
  level: "INFO"
```

## Docker

### Building the Container

```bash
docker build -t room-temperature-sensor .
```

### Running the Container

```bash
docker run -d --name room-temp-sensor \
  -v $(pwd)/config:/app/config \
  room-temperature-sensor
```

### Docker Compose Integration

The microservice can be integrated into a larger system using docker-compose:

```yaml
services:
  room-temperature-sensor:
    build: ./room_temperature_sensor
    volumes:
      - ./room_temperature_sensor/config:/app/config
    restart: unless-stopped
    depends_on:
      - mqtt-broker
```

## Development

### Dependencies

Install dependencies:

```bash
pip install -r requirements.txt
```

Main dependencies:
- paho-mqtt: MQTT client
- pyyaml: Configuration parsing
- pytest: Testing framework

### Running Tests

```bash
pytest tests/
```

### Running Locally

```bash
python -m app.main
```