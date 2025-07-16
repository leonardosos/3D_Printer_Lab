import os
import logging
import yaml
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.routes.temperature import temperature_bp
from app.routes.jobs import jobs_bp
from app.routes.printers import printers_bp

# Create and configure the Flask application
app = Flask(__name__)

# Load configuration
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Initialize app with config
config = load_config()

# Configure logging
logging.basicConfig(
    level=config['logging']['level'],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config['logging']['file'] if 'file' in config['logging'] else None
)
logger = logging.getLogger('api-gateway')

# Register blueprints
app.register_blueprint(temperature_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(printers_bp)

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    
    if isinstance(e, HTTPException):
        response = {
            "error": {
                "code": e.code,
                "message": e.description
            }
        }
        return jsonify(response), e.code
    
    # For other exceptions, return a 500 error
    response = {
        "error": {
            "code": 500,
            "message": "Internal Server Error",
            "details": str(e) if app.debug else None
        }
    }
    return jsonify(response), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "api-gateway"})

if __name__ == '__main__':
    app.run(
        host=config['server']['host'],
        port=config['server']['port'],
        debug=config.get('debug', False)
    )
