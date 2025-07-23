import json
from app.dto.printer_progress_dto import PrinterProgressDTO
class MQTTSubscriber:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def subscribe_progress(self, callback):
        """
        Subscribes to printer progress updates.
        Topic: device/printer/{printerId}/progress
        Type: PrinterProgressDTO
        QoS: 0
        """
        topic = "device/printer/+/progress"
        def dto_callback(client, userdata, message):
            payload = json.loads(message.payload.decode())
            dto = PrinterProgressDTO(
                printerId=payload.get("printerId"),
                jobId=payload.get("jobId"),
                status=payload.get("status"),
                progress=payload.get("progress"),
                timestamp=payload.get("timestamp")
            )
            callback(client, userdata, dto)
        self.mqtt_client.subscribe(topic, dto_callback, qos=0)


