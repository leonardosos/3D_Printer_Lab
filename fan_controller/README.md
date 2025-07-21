# Fan Controller Microservice

The `fan_controller` microservice manages the speed of a fan unit based on ambient temperature and emergency alerts. It subscribes to MQTT topics to receive updates, determines the correct fan speed, and publishes speed commands accordingly.

---

## Overview

### MQTT Topics

**Subscribed:**

- `device/fan/controller/status` – Global temperature updates
- `device/fan/controller/emergency` – Emergency alerts

**Published:**

- `device/fan/<id>/speed` – Fan speed commands

---

## Behavior

The microservice reacts to both **status** and **emergency** messages to compute the appropriate fan speed. Logic flow:

1. **Emergency Active**:
   - If `type` is `"overheat"` or `"thermal_runaway"`, fan speed is set to 100%.
   - If `action` is `"shutdown"`, fan speed is set to 0%.
   - If `type` is `"thermal_runaway"`, speed is 100% for 30 seconds, then reset.
   - If `type` is `"solved"`, emergency state is cleared and normal operation resumes.

2. **Status Only**:
   - Speed is calculated from severity: `value * 10`, clamped between 0–100.

3. **No Input**:
   - No speed update is published.

---

## Message Formats

### Status Input

**Topic:** `device/fan/controller/status`  
**Payload:**

```json
{
  "value": 4,
  "timestamp": "2025-06-15T08:32:20Z"
}
```

- `value`: Integer from 1–10, indicating temperature severity.
- `timestamp`: ISO 8601 string.

---

### Emergency Input

**Topic:** `device/fan/controller/emergency`  
**Payload:**

```json
{
  "action": "shutdown",
  "type": "thermal_runaway",
  "source": "printer",
  "id": "printer-2",
  "timestamp": "2025-06-15T08:32:20Z"
}
```

- `action`: `"shutdown"` or `"max_speed"`.
- `type`: `"overheat"`, `"thermal_runaway"`, `"solved"`, etc.
- `source`: Device name triggering the alert.
- `id`: Unique source identifier.
- `timestamp`: ISO timestamp.

---

### Fan Speed Output

**Topic:** `device/fan/<id>/speed`  
**Payload:**

```json
{
  "fanId": "fan-1",
  "speed": 75,
  "actual": 75,
  "timestamp": "2025-06-15T08:32:15Z"
}
```

- `fanId`: Target fan identifier.
- `speed`: Intended fan speed (0–100).
- `actual`: Measured/assumed speed.
- `timestamp`: When the message is published.

---

## Class Overview

### `FanController`

Handles logic and publishes fan speed.

```python
class FanController:
    def __init__(self, fan_id, repository, publisher)
    def on_status_received(payload)
    def on_emergency_received(payload)
    def update_speed()
    def calculate_speed(status, emergency=None) -> int
    def publish_speed(speed: int)
```

- **Emergency takes precedence** over temperature updates.
- **Thermal runaway** triggers a **30-second timer** after which speed resets.
- `"solved"` emergency clears the active alert and re-enables status-based logic.

---

## Architecture

### Directory Structure

```
fan_controller/
├── README.md
├── dockerfile
├── config/
│   └── fan_controller_config.yaml
├── app/
│   ├── main.py
│   ├── model/
│   │   └── status.py
│   ├── dto/
│   │   ├── status_dto.py
│   │   ├── emergency_dto.py
│   │   └── fan_speed_dto.py
│   ├── mqtt/
│   │   ├── publisher.py
│   │   └── subscriber.py
│   └── persistence/
│       └── repository.py
```

### DTOs (`app/dto/`)

```python
@dataclass
class StatusDTO:
    value: int
    timestamp: float

@dataclass
class EmergencyDTO:
    action: str
    type: str
    source: str
    id: str
    timestamp: float

@dataclass
class FanSpeedDTO:
    fanId: str
    speed: int
    actual: int
    timestamp: str
```

---

## Deployment

### Docker

```bash
docker build -t fan_controller .
docker run -d --name fan_controller fan_controller
```

### Configuration

Custom behavior (e.g., thresholds, MQTT broker) may be defined in:

```
config/fan_controller_config.yaml
```

---

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## Notes

- Thermal runaway mode includes a built-in **30s safety timer**.
- `"solved"` messages gracefully clear emergency state.
- Repository pattern is used to maintain internal state (`status`, `emergency`).
- Fan speed messages are printed to stdout for inspection and logged via `logging`.

---