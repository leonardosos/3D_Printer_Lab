from flask import Flask, jsonify
import yaml  # Add this import
from app.models.global_temperature_service import GlobalTemperatureService

class ApiEndpoint:
    def __init__(self, global_temp_service, config_path="app/web_config.yaml", debug=True):
        
        # Initialize the passed GlobalTemperatureService instance
        self.global_temp_service = global_temp_service

        # Create Flask app instance
        self.app = Flask(__name__)

        # Set debug mode BEFORE loading config
        self.debug = debug

        # Load configuration and routes
        self.load_config(config_path)
        self.setup_routes()

    def load_config(self, config_path):
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)  # Use yaml.safe_load instead of json.load
            self.app.config.update(self.config)
            
            if self.debug:
                print(f"[API ENDPOINT DEBUG] Loaded config: {self.config}")
        
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {config_path}: {e}")
        
    def setup_routes(self):
        @self.app.route("/temperature/global", methods=["GET"])
        def get_temperature():
            if self.debug:
                print("[API ENDPOINT DEBUG] Handling GET request for /temperature/global")
            # Should return a dict with top-level keys 'temperatures' and 'lastUpdated'
            return jsonify(self.global_temp_service.get_temperature_api_response())

    def start(self, host=None, port=None, reloader=False):
        # Use config values if not provided
        host = host or self.app.config.get("global_temperature", {}).get("host", "0.0.0.0")
        port = port or self.app.config.get("global_temperature", {}).get("port", 5000)
        self.app.run(host=host, port=port, threaded=True, use_reloader=reloader)




if __name__ == "__main__":
    # Example usage for testing
    #
    # From global_temperature directory:
    #    #    cd IoT_Project/global_temperature
    #    #    python3 -m app.http.api_endpoint
    #
    
    
    from app.mqtt.client import MQTTClient
    import time

    client = MQTTClient()

    service = GlobalTemperatureService(mqtt_client=client, 
                                       debug=True, 
                                       discover_printers_timeout=15)
    service.start()
    api = ApiEndpoint(service)
    api.start()

    # Keep the service running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Service stopped by user.")

