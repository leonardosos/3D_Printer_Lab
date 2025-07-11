# For this example we rely on the Paho MQTT Library for Python
# You can install it through the following command: pip install paho-mqtt

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion  # Added for new API version
from model.message_descriptor import MessageDescriptor
import json


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc, properties):  # Added 'properties' for new API
    print("Connected with result code " + str(rc))
    client.subscribe(target_topic_filter)  # Use 'client' instead of global 'mqtt_client'
    print("Subscribed to: " + target_topic_filter)


# Define a callback method to receive asynchronous messages
def on_message(client, userdata, message):
    if mqtt.topic_matches_sub(target_topic_filter, message.topic):
        message_payload = str(message.payload.decode("utf-8"))
        message_descriptor = MessageDescriptor(**json.loads(message_payload))
        print(f"Received IoT Message: Topic: {message.topic} Timestamp: {message_descriptor.timestamp} Type: {message_descriptor.type} Value: {message_descriptor.value}")


# Configuration variables
client_id = "clientId0001-Consumer"
broker_ip = "127.0.0.1"
broker_port = 1883
target_topic_filter = "device/+/temperature"
message_limit = 1000

# Create a new MQTT Client with the new callback API version
mqtt_client = mqtt.Client(client_id=client_id, callback_api_version=CallbackAPIVersion.VERSION2)

mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect

# Connect to the target MQTT Broker
mqtt_client.connect(broker_ip, broker_port)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqtt_client.loop_forever()
