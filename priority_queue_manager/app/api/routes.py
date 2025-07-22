from flask import Blueprint, request, jsonify
from app.model.priority_queue_service import PriorityQueueManager
from app.dto.job_request_dto import JobRequestDTO
import logging

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize service (singleton pattern)
service = PriorityQueueManager()

# Configure logging
logger = logging.getLogger(__name__)

@api_bp.route('/jobs', methods=['POST'])
def create_job():
    """
    POST /jobs - Creates a new job and inserts it into the priority queue
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        if 'modelId' not in data:
            return jsonify({"error": "modelId is required"}), 400
        
        # Create JobRequestDTO
        job_request = JobRequestDTO(
            modelId=data['modelId'],
            printerId=data.get('printerId'),
            priority=data.get('priority', 0)
        )
        
        # Add job via service
        new_job = service.add_job(job_request)
        
        # Return response
        response = {
            "job": new_job.to_dict()
        }
        
        logger.info(f"Created job {new_job.id} with priority {new_job.priority}")
        return jsonify(response), 201
        
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/jobs', methods=['GET'])
def get_all_jobs():
    """
    GET /jobs - Retrieves all jobs sorted from highest to lowest priority
    """
    try:
        jobs = service.get_all_jobs()
        
        response = {
            "jobs": [job.to_dict() for job in jobs]
        }
        
        logger.info(f"Retrieved {len(jobs)} jobs")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/jobs/<string:job_id>', methods=['PUT'])
def update_job_priority(job_id):
    """
    PUT /jobs/{jobId} - Modifies the priority of an existing job
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        if 'priority' not in data:
            return jsonify({"error": "priority is required"}), 400
        
        # Update job priority via service
        updated_job = service.update_job_priority(job_id, data['priority'])
        
        if not updated_job:
            return jsonify({"error": "Job not found"}), 404
        
        response = {
            "job": updated_job.to_dict()
        }
        
        logger.info(f"Updated job {job_id} priority to {data['priority']}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error updating job priority: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/jobs/<string:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """
    DELETE /jobs/{jobId} - Deletes a single job by ID
    """
    try:
        success = service.delete_job(job_id)
        
        if not success:
            return jsonify({"error": "Job not found"}), 404
        
        logger.info(f"Deleted job {job_id}")
        return '', 204
        
    except Exception as e:
        logger.error(f"Error deleting job: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/jobs', methods=['DELETE'])
def delete_multiple_jobs():
    """
    DELETE /jobs?ids=job-1,job-2,... - Deletes multiple jobs by ID in a single request
    """
    try:
        ids_param = request.args.get('ids')
        if not ids_param:
            return jsonify({"error": "ids parameter is required"}), 400
        
        # Parse job IDs from comma-separated string
        job_ids = [job_id.strip() for job_id in ids_param.split(',')]
        
        if not job_ids:
            return jsonify({"error": "At least one job ID is required"}), 400
        
        deleted_count = service.delete_multiple_jobs(job_ids)
        
        logger.info(f"Deleted {deleted_count} jobs")
        return '', 204
        
    except Exception as e:
        logger.error(f"Error deleting multiple jobs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/prioritary_job', methods=['GET'])
def get_prioritary_job():
    """
    GET /prioritary_job - Retrieves the job with highest priority (consumer approach - removes the job)
    """
    try:
        highest_priority_job = service.get_highest_priority_job()
        
        if not highest_priority_job:
            return jsonify({"error": "No jobs available"}), 404
        
        # Note: The spec shows response wrapped in "jobs" array, but it's a single job
        # Following the spec format from the howtodo.md
        response = {
            "jobs": [highest_priority_job.to_dict()]
        }
        
        logger.info(f"Retrieved and removed highest priority job {highest_priority_job.id}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting prioritary job: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Health check endpoint 
@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    GET /health - Simple health check endpoint
    """
    try:
        job_count = len(service.get_all_jobs())
        return jsonify({
            "status": "healthy",
            "service": "priority-queue-manager",
            "jobs_count": job_count
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "service": "priority-queue-manager",
            "error": str(e)
        }), 500

# Error handlers
@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500