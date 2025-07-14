import time
from app.dto.temperature_reading_printer_dto import TemperatureReadingPrinterDTO
from app.dto.printer_progress_dto import PrinterProgressDTO

class MQTTPublisher:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client  # MQTT client instance

    def publish_temperature(self, printer_id, temperature):
        # Publish the current temperature of the printer using DTO
        dto = TemperatureReadingPrinterDTO(
            printerId=printer_id,
            temperature=temperature,
            unit="C",
            timestamp=str(time.time())
        )
        self.mqtt_client.publish(
            f"device/printer/{printer_id}/temperature",
            dto.to_json(),
            qos=1
        )

    def publish_progress(self, printer_id, job_id, status, progress):
        # Publish the print progress for a job using DTO
        dto = PrinterProgressDTO(
            printerId=printer_id,
            jobId=job_id,
            status=status,
            progress=progress,
            timestamp=str(time.time())
        )
        self.mqtt_client.publish(f"device/printer/{printer_id}/progress", dto.to_json())



if __name__ == "__main__":
    # Example usage for testing
    #
    #from st_printer directory:
    #
    #    cd /home/leonardo/iot/IoT_Project/st_printer
    #    python3 -m app.mqtt.publisher
    #
    from app.mqtt.client import MQTTClient
    client = MQTTClient("app/printer_mqtt_config.yaml")
    client.connect()
    client.loop_start()
    publisher = MQTTPublisher(client)
    publisher.publish_temperature("printer_001", 200)
    publisher.publish_progress("printer_001", "job_001", "printing", 50)
    time.sleep(1)
    client.loop_stop()
    print("MQTT messages published for testing.")