from flask import Flask, request, jsonify
import logging

# Import DTOs
from app.dto.job_request_dto import JobRequestDTO
from app.dto.job_response_dto import JobResponseDTO
from app.dto.priority_update_dto import PriorityUpdateDTO

# Import Service
from app.services.priority_queue_service import PriorityQueueService

# Import Exceptions
from app.model.exceptions import (
    JobNotFoundError, 
    InvalidJobDataError, 
    QueueOperationError, 
    PersistenceError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize the service
queue_service = PriorityQueueService()

def job_to_response_dto(job) -> JobResponseDTO:
    """Convert Job model to JobResponseDTO"""
    return JobResponseDTO(
        id=job.id,
        modelId=job.modelId,
        assignedPrinterId=job.assignedPrinterId,
        priority=job.priority,
        status=job.status,
        submittedAt=job.submittedAt,
        updatedAt=job.updatedAt
    )

def handle_error(error: Exception, default_message: str = "Internal server error"):
    """Centralized error handling"""
    if isinstance(error, JobNotFoundError):
        logger.warning(f"Job not found: {error.message}")
        return jsonify({
            'error': 'Job not found',
            'message': error.message,
            'error_type': 'JOB_NOT_FOUND'
        }), 404
    
    elif isinstance(error, InvalidJobDataError):
        logger.warning(f"Invalid job data: {error.message}")
        return jsonify({
            'error': 'Invalid job data',
            'message': error.message,
            'error_type': 'INVALID_DATA'
        }), 400
    
    elif isinstance(error, QueueOperationError):
        logger.error(f"Queue operation error: {error.message}")
        return jsonify({
            'error': 'Queue operation failed',
            'message': error.message,
            'error_type': 'QUEUE_ERROR'
        }), 500
    
    elif isinstance(error, PersistenceError):
        logger.error(f"Persistence error: {error.message}")
        return jsonify({
            'error': 'Data persistence failed',
            'message': error.message,
            'error_type': 'PERSISTENCE_ERROR'
        }), 500
    
    else:
        logger.error(f"Unexpected error: {str(error)}")
        return jsonify({
            'error': default_message,
            'message': str(error),
            'error_type': 'INTERNAL_ERROR'
        }), 500

@app.route('/jobs', methods=['POST'])
def create_job():
    """Create a new job"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'error_type': 'INVALID_CONTENT_TYPE'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body cannot be empty',
                'error_type': 'EMPTY_BODY'
            }), 400
        
        # Validate required fields
        if 'modelId' not in data:
            return jsonify({
                'error': 'modelId is required',
                'error_type': 'MISSING_REQUIRED_FIELD'
            }), 400
        
        # Create job request DTO
        job_request = JobRequestDTO(
            modelId=data['modelId'],
            printerId=data.get('printerId'),
            priority=data.get('priority', 0)
        )
        
        # Validate priority
        if not isinstance(job_request.priority, int):
            return jsonify({
                'error': 'Priority must be an integer',
                'error_type': 'INVALID_DATA_TYPE'
            }), 400
        
        # Create new job through service
        new_job = queue_service.add_job(
            model_id=job_request.modelId,
            printer_id=job_request.printerId,
            priority=job_request.priority
        )
        
        # Return response
        response_dto = job_to_response_dto(new_job)
        logger.info(f"Successfully created job: {new_job.id}")
        
        return jsonify({'job': response_dto.to_dict()}), 201
        
    except Exception as e:
        return handle_error(e, "Failed to create job")

@app.route('/jobs/<job_id>', methods=['PUT'])
def update_job_priority(job_id: str):
    """Update job priority"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'error_type': 'INVALID_CONTENT_TYPE'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body cannot be empty',
                'error_type': 'EMPTY_BODY'
            }), 400
        
        # Validate required fields
        if 'priority' not in data:
            return jsonify({
                'error': 'priority is required',
                'error_type': 'MISSING_REQUIRED_FIELD'
            }), 400
        
        # Validate priority type
        if not isinstance(data['priority'], int):
            return jsonify({
                'error': 'Priority must be an integer',
                'error_type': 'INVALID_DATA_TYPE'
            }), 400
        
        # Update priority through service
        priority_update = PriorityUpdateDTO(priority=data['priority'])
        updated_job = queue_service.update_job_priority(job_id, priority_update.priority)
        
        # Return updated job
        response_dto = job_to_response_dto(updated_job)
        logger.info(f"Successfully updated job priority: {job_id}")
        
        return jsonify({'job': response_dto.to_dict()}), 200
        
    except Exception as e:
        return handle_error(e, "Failed to update job priority")

@app.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id: str):
    """Delete a single job"""
    try:
        queue_service.delete_job(job_id)
        logger.info(f"Successfully deleted job: {job_id}")
        return '', 204
        
    except Exception as e:
        return handle_error(e, "Failed to delete job")

@app.route('/jobs', methods=['DELETE'])
def delete_multiple_jobs():
    """Delete multiple jobs by IDs"""
    try:
        ids_param = request.args.get('ids')
        if not ids_param:
            return jsonify({
                'error': 'ids parameter is required',
                'error_type': 'MISSING_REQUIRED_PARAMETER'
            }), 400
        
        job_ids = [id.strip() for id in ids_param.split(',') if id.strip()]
        if not job_ids:
            return jsonify({
                'error': 'No valid job IDs provided',
                'error_type': 'INVALID_PARAMETER'
            }), 400
        
        # Delete jobs through service
        deleted_count = queue_service.delete_multiple_jobs(job_ids)
        
        logger.info(f"Successfully deleted {deleted_count} jobs")
        return '', 204
        
    except Exception as e:
        return handle_error(e, "Failed to delete multiple jobs")

@app.route('/jobs', methods=['GET'])
def get_all_jobs():
    """Get all jobs sorted by priority"""
    try:
        jobs = queue_service.get_all_jobs()
        
        # Convert to response DTOs
        jobs_response = [job_to_response_dto(job).to_dict() for job in jobs]
        
        logger.info(f"Successfully retrieved {len(jobs)} jobs")
        return jsonify({'jobs': jobs_response}), 200
        
    except Exception as e:
        return handle_error(e, "Failed to retrieve jobs")

@app.route('/prioritary_job', methods=['GET'])
def get_highest_priority_job():
    """Get and consume (delete) the job with highest priority"""
    try:
        highest_priority_job = queue_service.get_next_job()
        
        if not highest_priority_job:
            # Return 404 to match Job Handler's expectation
            return jsonify({'detail': 'No jobs available'}), 404
        
        # CONSUME the job - delete it from the queue
        queue_service.delete_job(highest_priority_job.id)
        
        # Convert to response DTO and return DIRECTLY (no wrapper)
        job_response = job_to_response_dto(highest_priority_job).to_dict()
        
        logger.info(f"Consumed highest priority job: {highest_priority_job.id}")
        return jsonify(job_response), 200  # Direct job object, no wrapper
        
    except Exception as e:
        return handle_error(e, "Failed to retrieve and consume highest priority job")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'error_type': 'ENDPOINT_NOT_FOUND'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint',
        'error_type': 'METHOD_NOT_ALLOWED'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'error_type': 'INTERNAL_ERROR'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Priority Queue Manager service...")
    app.run(host='0.0.0.0', port=8080, debug=True)