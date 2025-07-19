import yaml
from flask import Flask, request
from app.routes.dashboard import dashboard_bp
from app.routes.temperature import temperature_bp
from app.routes.printers import printers_bp
from app.routes.queue import queue_bp
import os
import threading

class WebServer:
    def __init__(self, config_path='app/web_conf.yaml', debug=True):
        
        self.debug = debug
        
        if self.debug:
            print(f"[WEB UI DEBUG] Initializing WebServer with config path: {config_path}")

        self.config = self._load_config(config_path)
        
        if self.debug:
            print(f"[WEB UI DEBUG] Loaded config: {self.config}")

        self.app = Flask(__name__)
        
        self._register_blueprints()

        # Define reload time in milliseconds
        self.reload_page_timer = 30000 # 30 seconds
        self._register_context_processors()  

        # Start the server in a separate thread
        self.server_thread = None

        if self.debug:
            print("[WEB UI DEBUG] WebServer initialization complete.")

    def _load_config(self, path):
        if self.debug:
            print(f"[WEB UI DEBUG] Attempting to load config from: {path}")

        config = {
            "web": {"host": "0.0.0.0", "port": 8000, "debug": False},
            "api_gateway": {"base_url": "http://localhost:8080"}
        }
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    loaded = yaml.safe_load(f)
                    print(f"YAML loaded: {loaded}")
                    if isinstance(loaded, dict):
                        config.update(loaded)

                        if self.debug:
                            print("[WEB UI DEBUG] Config updated with YAML file.")
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            print(f"Config file {path} not found. Using default config.")
        return config

    def _register_blueprints(self):
        self.app.register_blueprint(dashboard_bp=dashboard_bp)
        self.app.register_blueprint(temperature_bp=temperature_bp)
        self.app.register_blueprint(printers_bp=printers_bp)
        self.app.register_blueprint(queue_bp=queue_bp)

        if self.debug:
            print("[WEB UI DEBUG] All blueprints registered.")

    def _register_context_processors(self):
        reload_time_ms = self.config.get("web", {}).get("reload_time_ms", self.reload_page_timer)
        @self.app.context_processor
        def inject_reload_time():
            return dict(RELOAD_TIME_MS=reload_time_ms)

    def _run_server(self):
        web_conf = self.config.get("web", {})
        host = web_conf.get("host", "0.0.0.0")
        port = web_conf.get("port", 8000)
        debug = web_conf.get("debug", False)
        print(f"Starting server with host={host}, port={port}, debug={debug}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)

    def start(self):
        print("Starting web-ui server...")

        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

    def stop(self):
        print("Stopping server...")
        # No need to send shutdown request; just join the thread if needed
        if self.server_thread:
            self.server_thread.join(timeout=2)
        print("Server stopped.")



