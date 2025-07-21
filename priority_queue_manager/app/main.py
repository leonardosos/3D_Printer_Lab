import logging
import os
import sys
from flask import Flask
from app.api.routes import app

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

"""
try:
    from priority_queue_manager.app.api.routes import app
except ImportError:
    # Fallback for different import paths
    try:
        from priority_queue_manager.app.api.routes import app
    except ImportError:
        print("Error: Could not import routes. Make sure you're in the correct directory.")
        sys.exit(1)
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    # Ensure data directory exists (relative to main.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    data_dir = os.path.abspath(data_dir)  # Normalize path
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Created data directory: {data_dir}")
    
    logger.info("Priority Queue Manager service initialized")
    logger.info(f"Data directory: {data_dir}")
    return app

def test_endpoints():
    """Simple test function to verify endpoints work"""
    logger.info("=== Testing Priority Queue Manager ===")
    
    with app.test_client() as client:
        # Test health check (if exists)
        try:
            response = client.get('/health')
            logger.info(f"Health check: {response.status_code}")
        except:
            logger.info("No health endpoint found")
        
        # Test get all jobs (should be empty initially)
        response = client.get('/jobs')
        logger.info(f"GET /jobs: {response.status_code} - {len(response.get_json().get('jobs', []))} jobs")
        
        # Test create job
        test_job = {
            "modelId": "test-model-123",
            "priority": 5
        }
        response = client.post('/jobs', json=test_job)
        logger.info(f"POST /jobs: {response.status_code}")
        
        if response.status_code == 201:
            job_data = response.get_json()
            logger.info(f"Created job: {job_data.get('job', {}).get('id')}")
        
        # Test get priority job
        response = client.get('/prioritary_job')
        logger.info(f"GET /prioritary_job: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("✅ All basic tests passed!")
        else:
            logger.warning("⚠️ Some tests failed")

if __name__ == '__main__':
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        logger.info("Running in TEST mode")
        flask_app = create_app()
        test_endpoints()
        sys.exit(0)
    
    # Normal startup
    # Get configuration from environment variables (with defaults)
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Priority Queue Manager on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Create and run the app
    flask_app = create_app()
    
    try:
        flask_app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)