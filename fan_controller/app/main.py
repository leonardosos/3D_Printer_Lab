import logging
import sys
from app.model.status import FanController
from app.persistence.repository import FanControllerRepository
from app.mqtt.publisher import MqttPublisher
from app.mqtt.subscriber import MqttSubscriber

def load_config():
    from app.mqtt.subscriber import CONFIG_PATH
    import yaml
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def create_fan_controllers(config):
    fan_controllers = {}
    for fan in config["fans"]:
        fan_id = fan["id"]
        repo = FanControllerRepository()
        publisher = MqttPublisher()
        publisher.connect()
        fan_controllers[fan_id] = FanController(fan_id, repo, publisher)
    return fan_controllers

def main():
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    fan_controllers = create_fan_controllers(config)

    def on_status(payload):
        fan_id = payload.get("fanId") or payload.get("id")
        if fan_id and fan_id in fan_controllers:
            fan_controllers[fan_id].on_status_received(payload)
        else:
            # No fanId: broadcast to all
            for controller in fan_controllers.values():
                controller.on_status_received(payload)

    def on_emergency(payload):
        fan_id = payload.get("fanId") or payload.get("id")
        if fan_id and fan_id in fan_controllers:
            fan_controllers[fan_id].on_emergency_received(payload)
        else:
            # No fanId: broadcast to all
            for controller in fan_controllers.values():
                controller.on_emergency_received(payload)

    # Test mode: simulate messages instead of starting MQTT
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        logging.info("Running in test mode.")
        # Simulate a status and emergency message for each fan
        for fan_id, controller in fan_controllers.items():
            status_payload = {"heatLevel": 5, "timestamp": "2025-07-19T12:00:00Z"}
            emergency_payload = {"action": "none", "type": "overheat", "source": "test", "id": "em1", "timestamp": "2025-07-19T12:01:00Z"}
            logging.info(f"Simulating status for {fan_id}")
            controller.on_status_received(status_payload)
            logging.info(f"Simulating emergency for {fan_id}")
            controller.on_emergency_received(emergency_payload)
        print("Test mode complete.")
        return

    # Start the MQTT subscriber (single instance, handles all fans)
    subscriber = MqttSubscriber(on_status=on_status, on_emergency=on_emergency)
    logging.info("FanController microservice running. Waiting for MQTT messages...")
    subscriber.start()

if __name__ == "__main__":
    main()