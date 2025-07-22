import os
import logging
import yaml
from flask import Flask
from logging.handlers import RotatingFileHandler

from app.api.routes import api_bp
from app.model.priority_queue_service import PriorityQueueManager

# Create Flask application
app = Flask(__name__)

def load_config():
    """Load configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        # Return default config
        return {
            'server': {'host': '0.0.0.0', 'port': 8090, 'debug': True},
            'logging': {'level': 'INFO', 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}
        }

def setup_logging(config):
    """Setup logging configuration"""
    log_config = config.get('logging', {})
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Setup file handler if log file is specified
    if 'file' in log_config:
        log_file = log_config['file']
        log_path = os.path.join(os.path.dirname(__file__), '..', log_file)
        
        handler = RotatingFileHandler(
            log_path,
            maxBytes=log_config.get('max_size', 10485760),
            backupCount=log_config.get('backup_count', 5)
        )
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[handler, logging.StreamHandler()]  # Both file and console
        )
    else:
        # Console only
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )

# Load configuration
config = load_config()

# Setup logging
setup_logging(config)

# Create logger
logger = logging.getLogger(__name__)

# Configure Flask app
app.config['HOST'] = config['server']['host']
app.config['PORT'] = config['server']['port']
app.config['DEBUG'] = config['server']['debug']

# Initialize service (singleton)
priority_queue_manager = PriorityQueueManager()

# Register blueprints
app.register_blueprint(api_bp)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    service_info = config.get('service', {})
    try:
        job_count = priority_queue_manager.get_job_count()
        
        return {
            "status": "healthy",
            "service": service_info.get('name', 'priority-queue-manager'),
            "version": service_info.get('version', '1.0.0'),
            "jobs_count": job_count
        }, 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": service_info.get('name', 'priority-queue-manager'),
            "error": str(e)
        }, 500

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return {"error": "Internal server error"}, 500

if __name__ == '__main__':
    logger.info(f"Starting Priority Queue Manager on {app.config['HOST']}:{app.config['PORT']}")
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )