from app.mqtt.client import MQTTClient
from app.models.global_temperature_service import GlobalTemperatureService
from app.http.api_endpoint import ApiEndpoint
import time
import os

def main():

    # Initialize MQTT client
    client = MQTTClient()

    # Get timer from environment or use default
    timer = int(os.getenv("timer", 60))

    service = GlobalTemperatureService(mqtt_client=client, 
                                       debug=True, 
                                       discover_printers_timeout=timer)
    service.start()
    
    api = ApiEndpoint(service)
    api.start()

    # Keep the service running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Service stopped by user.")


if __name__ == "__main__":

    main()