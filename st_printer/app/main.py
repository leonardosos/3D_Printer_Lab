from app.classes.printing_service import PrintingService
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "printer_config.yaml")
MQTT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "printer_mqtt_config.yaml")

def main():
    service = PrintingService(CONFIG_PATH, MQTT_CONFIG_PATH)
    service.start()
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting subscriber...")

if __name__ == "__main__":
    main()
