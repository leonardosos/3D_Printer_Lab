# MQTT Tester

This component is designed to test MQTT communication using a sender and a receiver that interact through an MQTT broker. It helps verify that the broker is working correctly by sending and receiving messages.

## Overview

- **Sender**: Publishes temperature messages to the broker.
- **Receiver**: Subscribes to temperature topics and prints received messages.
- **MQTT Broker**: See [mqtt-broker/README.md](mqtt-broker/README.md) for broker setup and configuration details.

## Usage Modes

- **Local**: Run sender and receiver scripts directly on your machine for quick testing.
- **Single Docker**: Containerize sender and receiver for isolated testing.
- **Docker Compose**: Use `docker-compose.yml` to launch broker, sender, and receiver together for full integration testing.

## How It Works

1. The sender publishes messages to topics like `device/<device_id>/temperature`.
2. The receiver subscribes to topics (e.g., `device/+/temperature`) and prints incoming messages.
3. Both components use the [Paho MQTT](https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html) library.

## Getting Started

1. **Set up the MQTT broker**  
   Follow instructions in [mqtt-broker/README.md](mqtt-broker/README.md).

2. **Local Testing**  
   - Install dependencies present in `local/requirements.txt`
   - Run the sender and receiver scripts on local folder.

3. **Docker Testing**  
   - Build and run sender/receiver containers using provided Dockerfiles in `docker_send` and `docker_recv`.

4. **Docker Compose**  
   - Launch all services together using `docker-compose up` in the mqtt-tester directory.

## Folder Structure

- `local/` – Scripts for local testing.
- `docker_send/` – Dockerized sender.
- `docker_recv/` – Dockerized receiver.
- `mqtt-broker/` – Broker configuration and data.
