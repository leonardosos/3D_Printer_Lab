import json
from app.dto.printer_assignment_dto import PrinterAssignmentDTO, AssignmentParameters

class MQTTSubscriber:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def subscribe_assignment(self, printer_id, callback):
        topic = f"device/printer/{printer_id}/assignment"
        # Wrap the callback to parse the payload as DTO
        def dto_callback(client, userdata, message):
            payload = json.loads(message.payload.decode())
            param_dict = payload.get("parameters", {})
            params = AssignmentParameters(
                layerHeight=param_dict.get("layerHeight"),
                infill=param_dict.get("infill"),
                nozzleTemp=param_dict.get("nozzleTemp")
            )
            assignment_dto = PrinterAssignmentDTO(
                jobId=payload.get("jobId"),
                modelUrl=payload.get("modelUrl"),
                filamentType=payload.get("filamentType"),
                estimatedTime=payload.get("estimatedTime"),
                priority=payload.get("priority"),
                assignedAt=payload.get("assignedAt"),
                parameters=params
            )
            callback(client, userdata, assignment_dto)
        self.mqtt_client.subscribe(topic, dto_callback, qos=1)


if __name__ == "__main__":
    # Example usage for testing
    #
    #from st_printer directory:
    #
    #    cd /home/leonardo/iot/IoT_Project/st_printer
    #    python3 -m app.mqtt.subscriber
    #
    
    from app.mqtt.client import MQTTClient
    def dummy_callback(client, userdata, assignment_dto):
        print("Received assignment DTO:", assignment_dto)
    client = MQTTClient("app/printer_mqtt_config.yaml")
    client.connect()
    client.loop_start()
    subscriber = MQTTSubscriber(client)
    subscriber.subscribe_assignment("printer_001", dummy_callback)
    print("Subscribed to printer assignment topic.")
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting subscriber...")
        client.loop_stop()
        client.client.disconnect()

