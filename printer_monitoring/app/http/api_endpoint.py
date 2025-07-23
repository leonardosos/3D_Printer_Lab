from flask import Flask, jsonify
import yaml  # Add this import
from app.models.printer_monitoring_service import PrinterMonitoringService

class ApiEndpoint:
    def __init__(self, printer_monitoring_service: PrinterMonitoringService, config_path="app/web_config.yaml", debug=True):

        # Initialize the passed PrinterMonitoringService instance
        self.printer_monitoring_service = printer_monitoring_service

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
                print(f"[API STATUS ENDPOINT DEBUG] Loaded config: {self.config}")

        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {config_path}: {e}")
        
    def setup_routes(self):
        @self.app.route("/printers/status", methods=["GET"])
        def get_printer_status():
            if self.debug:
                print("[API PRINTER STATUS ENDPOINT DEBUG] Handling GET request for /printers/status")
            # Should return a dict with printer status information
            return jsonify(self.printer_monitoring_service.get_status_api_response())

    def start(self, host=None, port=None, reloader=False):
        # Use config values if not provided
        host = host or self.app.config.get("printer_monitoring", {}).get("host", "0.0.0.0")
        port = port or self.app.config.get("printer_monitoring", {}).get("port", 5000)
        self.app.run(host=host, port=port, threaded=True, use_reloader=reloader)



