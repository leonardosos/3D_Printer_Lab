from app.classes.printing_service import PrintingService
import os
from app.mqtt.client import MQTTClient



def main():

    # Load debug mode from environment variable
    debug_service = os.getenv("DEBUG", default="True")
    printer_id = os.getenv("PRINTER_ID", default="printer_001")

    # Define paths for configuration files
    printer_config_path = os.path.join(os.path.dirname(__file__), "printer_config.yaml")
    mqtt_config_path = os.path.join(os.path.dirname(__file__), "printer_mqtt_config.yaml")

    client = MQTTClient(debug=True, mqtt_config_path=mqtt_config_path)  # Enable debug mode for MQTT communication

    service = PrintingService(config_path=printer_config_path, 
                              debug=debug_service,
                              mqtt_client=client,
                              printer_id=printer_id)

    service.start()

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting subscriber...")

if __name__ == "__main__":
    main()
