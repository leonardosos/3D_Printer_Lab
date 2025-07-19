from app.classes.anomaly_detection_service import AnomalyDetectionService
from app.mqtt.client import MQTTClient 
import time
import os

def main():

    debug_service = os.getenv("DEBUG", "False")
    timer_hear = os.getenv("timer_hear", "60")

    client = MQTTClient(debug=True) # let communication with the broker

    service = AnomalyDetectionService(mqtt_client=client, 
                                      debug=debug_service, 
                                      discover_printers_timeout=timer_hear)
    
    service.start()

    service.periodic_csv_dump(file_path="app/persistence/save")  

    print("[ANOMALY_DETECTION] Service started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Service stopped by user.")
        service.mqtt_client.loop_stop()

if __name__ == "__main__":
    main()