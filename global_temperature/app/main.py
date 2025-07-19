from app.mqtt.client import MQTTClient
from app.models.global_temperature_service import GlobalTemperatureService
from app.http.api_endpoint import ApiEndpoint
import time
import os

def main():

    debug_service = os.getenv("DEBUG", "False")
    timer = int(os.getenv("timer_hear", 60))

    # Initialize MQTT client
    client = MQTTClient(debug=True)  # Enable debug mode for MQTT communication

    service = GlobalTemperatureService(mqtt_client=client, 
                                       debug=debug_service, 
                                       discover_printers_timeout=timer)
    service.start()

    api = ApiEndpoint(global_temp_service=service,
                      debug=True) # let communication for the API endpoint
    api.start()

    # Keep the service running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Service stopped by user.")


if __name__ == "__main__":

    main()