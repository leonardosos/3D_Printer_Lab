from flask import Blueprint, jsonify, request
from app.services.queue_service import (
    get_all_jobs, 
    create_job, 
    update_job, 
    delete_job
)
from app.dto.job_dto import JobDTO, JobsResponseDTO
from app.dto.create_job_dto import CreateJobRequestDTO, CreateJobResponseDTO
from app.dto.update_job_dto import UpdateJobRequestDTO, UpdateJobResponseDTO
from app.utils.error_handler import handle_service_error, validate_json_request

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs', methods=['GET'])
@handle_service_error
def get_jobs():
    """Get all jobs in the queue"""
    # Call the service to get all jobs
    jobs_data = get_all_jobs()
    
    # Convert raw data to DTOs for validation
    job_dtos = [
        JobDTO(
            id=job['id'],
            modelId=job['modelId'],
            assignedPrinterId=job.get('assignedPrinterId'),
            priority=job.get('priority', 0),
            status=job.get('status', 'pending'),
            submittedAt=job.get('submittedAt'),
            updatedAt=job.get('updatedAt')
        ) for job in jobs_data.get('jobs', [])
    ]
    
    # Create the response DTO
    response_dto = JobsResponseDTO(jobs=job_dtos)
    
    # Return the validated data
    return jsonify({
        'jobs': [vars(job) for job in response_dto.jobs]
    })

@jobs_bp.route('/jobs', methods=['POST'])
@handle_service_error
@validate_json_request
def post_job():
    """Create a new job"""
    # Get request data
    request_data = request.json
    
    # Create and validate the request DTO
    request_dto = CreateJobRequestDTO(
        modelId=request_data.get('modelId'),
        printerId=request_data.get('printerId'),
        priority=request_data.get('priority', 0)
    )
    request_dto.validate()
    
    # Call the service to create a job
    created_job = create_job(vars(request_dto))
    
    # Create the response DTO
    response_dto = CreateJobResponseDTO(
        modelId=created_job.get('modelId'),
        priority=created_job.get('priority', 0)
    )
    
    # Return the validated data
    return jsonify(vars(response_dto)), 201

@jobs_bp.route('/jobs/<job_id>', methods=['PUT'])
@handle_service_error
@validate_json_request
def put_job(job_id):
    """Update an existing job"""
    # Get request data
    request_data = request.json
    
    # Create and validate the request DTO
    request_dto = UpdateJobRequestDTO(
        priority=request_data.get('priority')
    )
    request_dto.validate()
    
    # Call the service to update the job
    updated_job = update_job(job_id, vars(request_dto))
    
    # Create the job DTO
    job_dto = JobDTO(
        id=updated_job.get('id'),
        modelId=updated_job.get('modelId'),
        assignedPrinterId=updated_job.get('assignedPrinterId'),
        priority=updated_job.get('priority', 0),
        status=updated_job.get('status', 'pending'),
        submittedAt=updated_job.get('submittedAt'),
        updatedAt=updated_job.get('updatedAt')
    )
    
    # Create the response DTO
    response_dto = UpdateJobResponseDTO(job=job_dto)
    
    # Return the validated data
    return jsonify({
        'job': vars(response_dto.job)
    })

@jobs_bp.route('/jobs/<job_id>', methods=['DELETE'])
@handle_service_error
def remove_job(job_id):
    """Delete a job"""
    # Call the service to delete the job
    delete_job(job_id)
    
    # Return a 204 No Content response
    return '', 204
