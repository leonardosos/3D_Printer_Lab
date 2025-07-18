from app.models.anomaly_detection_service import AnomalyDetectionService
from app.mqtt.client import MQTTClient 
import time

def main():

    client = MQTTClient()
    service = AnomalyDetectionService(mqtt_client=client, debug=True, discover_printers_timeout=60)
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