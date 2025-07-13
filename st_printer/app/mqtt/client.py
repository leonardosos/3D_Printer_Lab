import paho.mqtt.client as mqtt
import yaml

class MQTTClient:
    def __init__(self, config_path, debug=True):
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
                if debug:
                    print(f"\n[MQTT CLIENT DEBUG] loaded config from {config_path}")
                    print(f"[MQTT CLIENT DEBUG] Config: {config}\n")
                # Prefer broker_ip and broker_port if present, else fallback
                self.broker = config.get('broker_ip')
                self.port = config.get('broker_port')
        except Exception as e:
            raise RuntimeError(f"Failed to load config file '{config_path}': {e}")

        # Initialize MQTT client with callback API version
        from paho.mqtt.client import CallbackAPIVersion
        self.client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
        
        # Define connection callback
        self.client.on_connect = self.on_connect

        self.debug = debug

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            if self.debug:
                print(f"[MQTT CLIENT DEBUG] Connected to MQTT broker at {self.broker}:{self.port}")
        else:
            if self.debug:
                print(f"[MQTT CLIENT DEBUG] Failed to connect, return code {rc}")

    def connect(self):
        # Connect to the MQTT broker
        self.client.connect(self.broker, self.port)

    def publish(self, topic, payload):
        # Publish a message to a topic and wait for confirmation
        infot = self.client.publish(topic, payload)
        infot.wait_for_publish()

    def subscribe(self, topic, callback):
        # Subscribe to a topic and set a callback for messages
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback)

    def loop_start(self):
        # Start the MQTT network loop in a background thread
        self.client.loop_start()

    def loop_stop(self):
        # Stop the MQTT network loop
        self.client.loop_stop()

