# MQTT Broker - Eclipse Moquitto

In this configuration we are going to use Eclipse Mosquitto Broker already available on Docker Hub at the following link: [https://hub.docker.com/_/eclipse-mosquitto](https://hub.docker.com/_/eclipse-mosquitto)

The target used image and version for this playground is: `eclipse-mosquitto:2.0.21`

**The mosquitto image can be pulled from Docker Hub and run with docker or using the docker-compose file. Follow the instructions below to set up your chosen method.**

## Docker configuration file

The configuration file is `mosquitto.conf` and it is available in the `mqtt-broker` folder of the project. The configuration file is set to save log messages to a file, and allow anonymous connections.

Below is the chosen configuration file content:

```config

    # Log messages to a file in the mounted log directory
    log_dest file /mosquitto/log/mosquitto.log

    # Listen on the default MQTT port
    listener 1883

    # Allow anonymous connections (default is true)
    allow_anonymous true

```

## Manual Docker pull and Run

### Docker pull command to download the image is

```bash
docker pull eclipse-mosquitto:2.0.21
```

### Docker Run command

We are customizing our MQTT Broker using the following customization at runtime:

- local configuration file `mosquitto.conf` using `-v <LOCAL_PATH>/mosquitto.conf:/mosquitto/config/mosquitto.conf`
- if exist some persistence folder for data: use `-v <LOCAL_PATH>/data:/mosquitto/data`
- local folder to collect logs locally using `-v <LOCAL_PATH>/log:/mosquitto/log` and having access also if the container will be destroyed
- mapping port with `-p 1883:1883`
- restart always parameter `--restart always`
- daemon mode `-d`

The resulting Run Linux command is:

Assure to be in the `mqtt-broker` folder of the project before running the command below.

```bash
    docker run --name my-mosquitto-broker \
    -p 1883:1883 \
    -v ${PWD}/mosquitto.conf:/mosquitto/config/mosquitto.conf \
    -v ${PWD}/data:/mosquitto/data \
    -v ${PWD}/log:/mosquitto/log \
    --restart always \
    -d eclipse-mosquitto:2.0.21
```

### Docker Stop command

To restart the existing container, use:

```bash
docker start my-mosquitto-broker
```

To stop and remove the container before creating a new one, use:

```bash
docker stop my-mosquitto-broker
docker rm my-mosquitto-broker
```

## Docker Compose Configuration

To use Docker Compose, look for the `docker-compose.yml` file in the root of your project.
