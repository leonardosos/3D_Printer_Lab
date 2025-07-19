# Robot management
This microservice is responsible to manage the robot operations, assigning missions and managing the Robot device (other microservice), where now there is only 1 robot device, but hypotetically there can be more than one.
This microservice is assigned to the port 8120

## Class Structure
mermaid diagram

## folder structure


## Communications

This microservice communicates via MQTT protocol.

### Topics

Robot management is subscribed to the topics:
    
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

    where status can be  "work" or "finish"

Messages over the "device/robot/robot{id}/coordinates" topic have the following json structure:

    { "robotId": "rob-1", "x": 120, "y": 45, "z": 10, "speed": 200, "timestamp": "2025-06-15T08:32:05Z" }

    where speed is optional and coordinates are expressed in mm

Messages over the "device/robot/robot{id}/progress" topic have the following json structure:

    { "robotId": "rob-1", "action": "pick", "status": "in_progress", "timestamp": "2025-06-15T08:32:10Z" }

    where action can be "pick"|"place"|"idle"
    status can be "in_progress"|"completed"|"error"
    where there can be also jobId as optional parameter and is a string

## Internal logic

- listens to "device/printers" topic 

- when a message is published there, validate it with a dto, following the expected json structure

- Robot management has an internal queue (called robot_queue), in which cronologically the published messages over device/printers are appended (if validated with dto)
    - then the first element of the robot_queue will be the less recent, if more than one message are stored there

- robot management has also an other list where the it stores the robots devices (actually is only 1)

- check the robot_queue
    - if list is empty do nothing
    - if there is at least one element in the queue keep the first element
        - if status is "finished" in that element keep it
            - read the message and extract "printerId" value
                - go to check into a config file which are the coordinates of that printer with "printerId"
                - publish over device/robot/{robotId}/coordinates that coordinates, without setting speed
                - wait and listens on device/robot/robot{id}/progress topic. when a message is publicated, validate with dto and if "status" is completed, measn that the robot has finished the procedure
- repeat everything

## docker

this microservice is dockerized