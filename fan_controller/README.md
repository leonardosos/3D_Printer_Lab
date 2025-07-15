# Fan Controller Microservice

The `fan_controller` microservice is responsible for managing the speed of a fan unit based on ambient temperature and emergency conditions. It receives temperature updates and emergency alerts, computes the appropriate fan speed, and publishes speed commands to the fan unit.

---

## Overview

This service listens to two main MQTT topics:

- **Global temperature updates** (`device/fan/controller/status`)
- **Emergency alerts** (`device/fan/controller/emergency`)

Based on these inputs, the service calculates the optimal fan speed and publishes it to:

- **Fan command topic**: `device/fan/-id-/speed`

If an emergency condition is detected (e.g., fire, overheating), it bypasses normal temperature-based logic and prioritizes the emergency action (e.g., fan shutdown or full-speed override).

---

## Message Formats

### Temperature Status Input

**Topic:** `device/fan/controller/status`\
**Payload:**

```json
{
  "value": 4,
  "timestamp": "2025-06-15T08:32:20Z"
}
```

- `value`: Integer indicating temperature severity.
- `timestamp`: ISO 8601 timestamp of the reading.

---

### Emergency Input

**Topic:** `device/fan/controller/emergency`\
**Payload:**

```json
{
  "action": "shutdown",
  "type": "overheat",
  "source": "printer",
  "id": "printer-2",
  "timestamp": "2025-06-15T08:32:20Z"
}
```

- `action`: `"shutdown"` or `"max_speed"`, the emergency directive.
- `type`: Type of emergency (`overheat`, `fire`, etc.).
- `source`: Device that triggered the alert.
- `id`: Unique identifier for the source device.
- `timestamp`: ISO timestamp of the alert.

---

### Fan Speed Output

**Topic:** `device/fan/-id-/speed`\
**Payload:**

```json
{
  "fanId": "fan-1",
  "speed": 75,
  "actual": 72,
  "timestamp": "2025-06-15T08:32:15Z"
}
```

- `fanId`: Target fan identifier.
- `speed`: Intended fan speed (0–100).
- `actual`: Measured speed (for logging/simulation).
- `timestamp`: When the command was issued.

---

## Architecture

### DTOs

Located in `app/dto`, the following Data Transfer Object classes are used:

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
```

---

### FanController Logic

Main service logic is encapsulated in the `FanController` class:

```python
class FanController:

    def __init__(self):
        self.latest_status = None
        self.latest_emergency = None

    def on_status_received(self, json_input):
        # Deserialize and store new status

    def on_emergency_received(self, json_input):
        # Deserialize and store emergency info

    def update_speed(self):
        # Decide if fan speed update is needed

    def calculate_speed(self, status, emergency=None):
        # Compute speed based on status or emergency

    def publish_speed(self, speed):
        # Publish command to MQTT topic
```

Logic priority:

1. If an **emergency** is active, it overrides normal operations.
2. If only **temperature status** is updated, it recalculates speed accordingly.
3. If no new data is received, no update is sent.

---

## Directory Structure

```
fan_controller/
├── app/
│   ├── dto/
│   │   ├── __init__.py
│   │   ├── status_dto.py
│   │   ├── emergency_dto.py
│   │   ├── fan_speed_dto.py
│   ├── model/
│   │   ├── __init__.py
│   │   └── status.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   └── repository.py
│   ├── mqtt/
│   │   ├── __init__.py
│   │   ├── subscriber.py
│   │   └── publisher.py
│   ├── main.py
├── requirements.txt
├── Dockerfile
```

---

## Docker Usage

A `Dockerfile` is provided to containerize the service. Typical usage:

```bash
docker build -t fan_controller .
docker run -d --name fan_controller fan_controller
```

---

## Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

---

## Final Notes & Adjustments

- `value` is now correctly parsed as an integer, aligning with `StatusDTO.value: int`.
- The `id` field in `EmergencyDTO` has been corrected to `str`.
- Duplicate `publisher.py` files were identified; only the one under `services/` was kept.
- Typo fixed: all mentions now use the correct class name `FanController`.

Feel free to expand this README with API testing instructions or deployment configurations as needed.

