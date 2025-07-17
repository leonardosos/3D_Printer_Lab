# Robot management

this microservice is responsible to manage the robot operations, assigning missions.
This microservice is assigned to the port 8120

## Communications

this microservice communicates via MQTT protocol.

### Topics

Robot management is subscribed to the topic:
    
    device/printers
    device/robot/robot{id}/coordinates

Robot management publishes over the topic:

    device/robot/robot{id}/progress

### Broker

The mqtt mosquitto broker is available at ther port 1883

### Topic messages

Messages over the "device/printers" topic have the following json structure:

    {
    "printers": [
    { "printerId": "printer-1", "status": "work", "timestamp": "2025-07-09T10:00:00Z" },
    { "printerId": "printer-2", "status": "finish", "timestamp": "2025-07-09T10:00:00Z" },
    { "printerId": "printer-3", "status": "work", "timestamp": "2025-07-09T10:00:00Z" }
    ]
    }

    where status can be  "printing"|"completed"|"idle"

Messages over the "device/robot/robot{id}/coordinates" topic have the following json structure:

    { "robotId": "rob-1", "x": 120, "y": 45, "z": 10, "speed": 200, "timestamp": "2025-06-15T08:32:05Z" }

    where speed is optional

Messages over the "device/robot/robot{id}/progress" topic have the following json structure:

    { "robotId": "rob-1", "action": "pick", "status": "in_progress", "timestamp": "2025-06-15T08:32:10Z" }

    where action can be "pick"|"place"|"idle"
    where there can be also jobId as optional parameter and is a string

## Internal logic

- listens to "device/printers" topic 

- when a message is published there, validate it with a dto, following the expected json structure

- Robot management has an internal queue (called robot_queue), in which cronologically the published messages over device/printers are appended (if validated with dto)
    - then the first element of the robot_queue will be the less recent, if more than one message are stored there

- check the robot_queue
    - if list is empty do nothing
    - if there is at least one element in the queue keep the first element
        - read the message and extract "printerId" value
