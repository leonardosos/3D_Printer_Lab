# IoT_Project : 3D Printers Lab

This repository contains the implementation of a distributed IoT system for automated 3D printing lab management, developed as part of the **Distributed and Internet of Things Software Architectures** course. (The project is not related to any other course.)

## Team Members

- **Leonardo Brighenti**
- **Simone Giovanardi**
- **Lorenzo Sartorelli**

## Meeting Notes

- [First Meeting (26-06-2025) Notes](meeting_notes/first_meeting.md)

## Components Explanation

Difficult Tier: [Tier List](flowchart/tier_list.mmd)

Leonardo:

- [Anomaly Detection (AT)](anomaly_detection/README.md)
- [Web Interface (GUI)](web-ui/README.md)
- [Printer (ST)](st_printer/README.md)
- [Global Temperatures (GT)](global_temperatures/README.md)

Simone:

Lorenzo:

## Project Structure

This project is organized into multiple components, each handling a specific aspect of the IoT system. Every component has its own folder containing a `README.md` with details about its functionality and usage. Each service is containerized with a dedicated `Dockerfile`, and the root directory includes a `docker-compose.yml` file to build and deploy the entire system seamlessly.

**Extra folder: Broker Folders:**

The broker related folders are used to set up and test the MQTT broker, which is essential for communication between the various components of the IoT system. The MQTT broker is implemented using Eclipse Mosquitto, a lightweight and widely used MQTT broker. For more information, see [mqtt-broker/README.md](mqtt-broker/README.md) and the section "MQTT Broker - Eclipse Mosquitto."

- **mqtt-broker**: Configuration and setup for the MQTT broker using Eclipse Mosquitto.
- **mqtt-tester**:
  - **local** Scripts for local testing of MQTT communication with the broker only for local testing purposes. -> **Note**: This is not part of the final project and is used only for testing purposes.
  - **mqtt-tester-docker**: Docker setup for the MQTT tester, allowing for easy deployment and testing of MQTT communication in a containerized environment using Docker and Docker Compose.

---
---

## Application Scenario

**An automated lab involved in the production of 3D printed objects**.

### Project Description  

The project idea has already been explained in general in the Project Proposal. In the following, a more detailed description related to the implementation will be discussed. To refresh the project goal, here is a short summary:

Inside an automated room, there are several 3D printers, each responsible for printing its own project. A robot (Cartesian manipulator) is present to unload all the printed elements. The room can manage anomalies such as overheating or fires through sensors installed on each printer and in the room itself. The working process is also autonomously decided. A human user can initiate print jobs through a web interface and monitor the situation in the room.

---

### Project Implementation  

The architecture is based on a **microservice** approach. Humans can interact with the system through a **GUI** that allows them to monitor information and act on the system. In particular, the user interface communicates via **HTTP** protocol with various microservices, coordinated by an **API Gateway** which redirects requests appropriately.

The **API Gateway** can retrieve information from:

- **Global Temperatures (GT)**  
- **Printer Monitoring (PM)**  

These provide updates about the percentage of ongoing print jobs and the temperatures of both the printers and the room.

A complete **CRUD** interface is implemented in the **Priority Queue Management (PQM)** microservice, where print orders (files) are stored while waiting to be sent to the printers.

**GT** and **PM** support both **HTTP** and **MQTT** protocols.

- **GT** subscribes to temperature topics (for the room and each printer) to inform the user and manage fan speed.
- **Room temperature** is provided by a sensor.  
- **GT** publishes messages to the **Fan Controller (FC)**, which adjusts fan speed in case of overheating (of either a single printer or the room).  

**FC** also listens to anomalies detected by **Anomaly Detection (AT)**, which might implement a **machine learning model** to detect unexpected temperature behavior over time. In case of anomalies, the user is notified of possible malfunctions.

Returning to **PQM**, it sends files to be printed when requested by the **Job Handler (JH)** microservice.

- **PQM** communicates only via **HTTP**.  
- **JH** is responsible for managing the printing process: sending files to available 3D printers and monitoring the printing status (e.g., percentage completed).  
- **JH** communicates via **MQTT** with **Robot Management (RM)**.

**Robot Management (RM)**:

- Listens for messages over a specific topic that alert when a print job is complete and the printer is ready to be unloaded.  
- Stores this information in a queue.  
- If the Cartesian robot is available, **coordinates** are sent so the robot can go to the printer, unload the object, and prepare the printer for a new job.

The **robot**, once it receives the coordinates, autonomously navigates to the target printer, collects the printed object, and updates **PM** and **JH** with its status for monitoring and coordination.

### Devices Table

| Device      | Number | Sensor | Actuator | Read                                    | Write                                   |
|-------------|--------|--------|----------|----------------------------------------|-----------------------------------------|
| 3D Printer  | 3      | Yes    | Yes      | - Print assignments<br>- Job commands  | - Temperature data<br>- Print progress<br>- Status updates |
| Room        | 1      | Yes    | No       | N/A                                    | - Temperature readings |
| Robot       | 1      | Yes    | Yes      | - Movement coordinates<br>- Job tasks  | - Progress updates<br>- Position status<br>- Completion signals |
| Fan         | 1      | No     | Yes      | - Speed commands| N/A   |

---
---

## Official documentation

Here you can find the documentation related to metods used during the project:

### Flowchart schemas

Components and their interactions are represented in flowcharts, which help visualize the system architecture and communication patterns.

- [Basic Flowchart of the IoT System](flowchart/basic_flowchart.mmd)
- [Full Flowchart with MQTT Topics](flowchart/full_flowchart.mmd); 
  - This flowchart includes arrows indicating the direction of communication between components, with MQTT topics specified for each interaction. Where up: and down: label means the direction of who is sending the message.

### Communication Schemas

- [Communication Schemas and Message Types](communication.md)
- [Port Schema Flowchart](flowchart/port_flowchart.mmd)

### PAHO (MQTT)

Below you can find the helpful methods for pub/sub:

<https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html>

### Docker + Docker Compose

To install Docker, run the following command:

    sudo snap install docker         # version 28.1.1+1

check if Docker is installed correctly by running:

    # Start Docker daemon
    sudo snap start docker

    # Check Docker status
    snap services docker

    # Verify Docker is working
    docker ps

#### Post-installation permissions problems

running the following command tests if you have the correct permissions to run Docker commands without `sudo`:

    docker ps

You might encounter an error like this:

    permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.51/containers/json": dial unix /var/run/docker.sock: connect: permission denied

Follow the instructions in the Docker documentation to resolve this issue:
<https://docs.docker.com/engine/install/linux-postinstall/>

### MQTT Broker - Eclipse Mosquitto

This section provides a guide for setting up and customizing an MQTT broker using Eclipse Mosquitto. We use the official eclipse-mosquitto Docker image on Docker Hub: <https://hub.docker.com/_/eclipse-mosquitto>.

The version used in this project is `2.0.21`.

Follow [the instructions in the README file](mqtt-broker/README.md):

- to set up the broker with custom configurations, including local configuration files, data persistence, and logging.
- to run the broker with specific parameters such as port mapping, restart policies, and daemon mode.
- to stop the broker when needed.
