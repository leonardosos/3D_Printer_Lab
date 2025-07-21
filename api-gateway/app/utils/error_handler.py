import logging
from functools import wraps
from flask import jsonify, request
from app.utils.service_exception import ServiceException

logger = logging.getLogger('api-gateway')

def handle_service_error(f):
    """Decorator to handle service exceptions uniformly"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ServiceException as e:
            logger.error(f"Service error: {str(e)}")
            response = {
                "error": {
                    "code": e.status_code,
                    "message": e.message,
                    "details": e.details
                }
            }
            return jsonify(response), e.status_code
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            response = {
                "error": {
                    "code": 400,
                    "message": "Bad Request",
                    "details": str(e)
                }
            }
            return jsonify(response), 400
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            response = {
                "error": {
                    "code": 500,
                    "message": "Internal Server Error",
                    "details": str(e)
                }
            }
            return jsonify(response), 500
    return decorated_function

def validate_json_request(f):
    """Decorator to validate that the request contains valid JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            response = {
                "error": {
                    "code": 400,
                    "message": "Bad Request",
                    "details": "Request must be JSON"
                }
            }
            return jsonify(response), 400
        return f(*args, **kwargs)
    return decorated_function
