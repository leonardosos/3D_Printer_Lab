import paho.mqtt.publish as publish

publish.single(
    topic="device/fan/controller/status",
    payload='{"speed": 75}',
    hostname="test-mosquitto",
    port=1883
)

print("Messaggio inviato!")
