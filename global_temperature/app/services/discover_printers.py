## Discover Printers Service
# launched periodically by the global temperature
#  service to discover printers
#  update the printer list

def discover_printers(subscriber, timeout=5, debug=False):
    """
    Listens for incoming printer temperature messages for a short period,
    and returns a set of discovered printer IDs.

    Args:
        subscriber: MQTTSubscriber instance
        timeout: seconds to listen for printer messages

    Returns:
        Set of printer IDs discovered
    """

    import threading
    import time

    discovered = set()

    def printer_callback(client, userdata, dto):
        if hasattr(dto, "printerId"):
            discovered.add(dto.printerId)

    if debug:
        print(f"[DISCOVER DEBUG] Listening for printers for {timeout} seconds...")

    subscriber.subscribe_printer_temperature(printer_callback)

    # Collect for the entire timeout period
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(0.2)  # allow time for messages to arrive

    if debug:
        print(f"[DISCOVER DEBUG] Discovered printers: {discovered}")

    return discovered

if __name__ == "__main__":
    # Example usage for testing
    #
    # From global_temperature directory:
    #    #    cd IoT_Project/global_temperature
    #    #    python3 -m app.services.discover_printers
    #
    from app.mqtt.client import MQTTClient
    from app.mqtt.subscriber import MQTTSubscriber

    client = MQTTClient("app/mqtt_config.yaml")
    client.connect()
    client.loop_start()
    subscriber = MQTTSubscriber(client)
    timeout = 60  # seconds to wait for printer messages
    print(f"Listening for printers for {timeout} seconds...")
    printers = discover_printers(subscriber, timeout=timeout)
    print("Discovered printers:", printers)
    client.loop_stop()
    client.client.disconnect()