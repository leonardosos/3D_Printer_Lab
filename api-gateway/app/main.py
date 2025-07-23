import os
import logging
import yaml
from flask import Flask, jsonify, make_response
from werkzeug.exceptions import HTTPException
from logging.handlers import RotatingFileHandler

from app.routes.temperature import temperature_bp
from app.routes.jobs import jobs_bp
from app.routes.printers import printers_bp

# Create Flask application
app = Flask(__name__)

# Load configuration
def load_config():
    """Load configuration with environment variable overrides"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    
    # Load base configuration
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Override with environment variables if present
    if 'API_GATEWAY_PORT' in os.environ:
        config['server']['port'] = int(os.environ['API_GATEWAY_PORT'])
    
    if 'GLOBAL_TEMP_SERVICE_URL' in os.environ:
        config['services']['global_temperature']['base_url'] = os.environ['GLOBAL_TEMP_SERVICE_URL']
    
    if 'PRIORITY_QUEUE_SERVICE_URL' in os.environ:
        config['services']['priority_queue']['base_url'] = os.environ['PRIORITY_QUEUE_SERVICE_URL']
    
    if 'PRINTER_MONITORING_SERVICE_URL' in os.environ:
        config['services']['printer_monitoring']['base_url'] = os.environ['PRINTER_MONITORING_SERVICE_URL']
    
    return config

# Initialize app with config
config = load_config()
app.config['HOST'] = config['server']['host']
app.config['PORT'] = config['server']['port']
app.config['DEBUG'] = config['server']['debug']

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = config['logging']['file']
log_path = os.path.join(os.path.dirname(__file__), '..', log_file)

# Set up rotating file handler
handler = RotatingFileHandler(
    log_path,
    maxBytes=config['logging'].get('max_size', 10485760),
    backupCount=config['logging'].get('backup_count', 5)
)

# Configure logging format
logging.basicConfig(
    level=config['logging']['level'],
    format=config['logging'].get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    handlers=[handler]
)

logger = logging.getLogger('api-gateway')
logger.info("API Gateway starting up with configuration loaded")

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
        return make_response(jsonify(response), e.code)
    
    # For other exceptions, return a 500 error
    response = {
        "error": {
            "code": 500,
            "message": "Internal Server Error",
            "details": str(e) if app.config['DEBUG'] else None
        }
    }
    return make_response(jsonify(response), 500)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok", 
        "service": "api-gateway",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
