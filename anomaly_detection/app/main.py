from app.classes.anomaly_detection_service import AnomalyDetectionService
from app.mqtt.client import MQTTClient 
import time
import os

def str2bool(val):
    return str(val).lower() in ("true", "1", "yes")

def main():

    debug_communication = str2bool(os.getenv("DEBUG_COMMUNICATION", "True"))
    debug_alerts = str2bool(os.getenv("DEBUG_ALERTS", "False"))
    debug_analysis = str2bool(os.getenv("DEBUG_ANALYSIS", "False"))
    debug_service = str2bool(os.getenv("DEBUG", "False"))
    timer_hear = int(os.getenv("timer_hear", "60"))

    client = MQTTClient(debug=debug_communication) # let communication with the broker

    service = AnomalyDetectionService(mqtt_client=client, 
                                      debug_service=debug_service,
                                      debug_alerts=debug_alerts,
                                      debug_analysis=debug_analysis,
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