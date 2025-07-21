import logging
from typing import List, Optional
from ..model.job_model import Job
from ..persistence.repository import QueuePersistence
from ..model.exceptions import JobNotFoundError, InvalidJobDataError, QueueOperationError

class PriorityQueueService:
    def __init__(self, persistence_file_path: str = "data/queue_data.json"):
        self.logger = logging.getLogger(__name__)
        self.repository = QueuePersistence(persistence_file_path)
    
    def add_job(self, model_id: str, printer_id: Optional[str] = None, priority: int = 0) -> Job:
        """Add a new job to the queue with optional printer and priority"""
        try:
            if not model_id or not model_id.strip():
                raise InvalidJobDataError("Model ID cannot be empty")
            
            if priority < 0:
                raise InvalidJobDataError("Priority cannot be negative")
            
            new_job = Job.create_new(
                model_id=model_id.strip(),
                printer_id=printer_id.strip() if printer_id else None,
                priority=priority
            )
            
            saved_job = self.repository.add_job(new_job)
            self.logger.info(f"Added new job: {saved_job.id} with priority {saved_job.priority}")
            return saved_job
            
        except Exception as e:
            if isinstance(e, InvalidJobDataError):
                raise
            self.logger.error(f"Unexpected error adding job: {e}")
            raise QueueOperationError(f"Failed to add job: {e}")
    
    def update_job_priority(self, job_id: str, new_priority: int) -> Job:
        """Update the priority of an existing job and reorder the queue"""
        try:
            if new_priority < 0:
                raise InvalidJobDataError("Priority cannot be negative")
            
            job = self.repository.get_job_by_id(job_id)
            old_priority = job.priority
            
            job.update_priority(new_priority)
            updated_job = self.repository.update_job(job)
            
            self.logger.info(f"Updated job {job_id} priority from {old_priority} to {new_priority}")
            return updated_job
            
        except JobNotFoundError:
            raise
        except Exception as e:
            if isinstance(e, InvalidJobDataError):
                raise
            self.logger.error(f"Unexpected error updating job priority: {e}")
            raise QueueOperationError(f"Failed to update job priority: {e}")
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a single job by ID"""
        try:
            result = self.repository.delete_job(job_id)
            self.logger.info(f"Deleted job: {job_id}")
            return result
            
        except JobNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error deleting job: {e}")
            raise QueueOperationError(f"Failed to delete job: {e}")
    
    def delete_multiple_jobs(self, job_ids: List[str]) -> int:
        """Bulk delete of multiple jobs"""
        try:
            if not job_ids:
                raise InvalidJobDataError("Job IDs list cannot be empty")
            
            deleted_count = self.repository.delete_multiple_jobs(job_ids)
            
            self.logger.info(f"Deleted {deleted_count} out of {len(job_ids)} requested jobs")
            
            if deleted_count == 0:
                raise JobNotFoundError(f"None of the jobs found: {job_ids}")
            
            return deleted_count
            
        except Exception as e:
            if isinstance(e, (InvalidJobDataError, JobNotFoundError)):
                raise
            self.logger.error(f"Unexpected error deleting multiple jobs: {e}")
            raise QueueOperationError(f"Failed to delete multiple jobs: {e}")
    
    def get_all_jobs(self) -> List[Job]:
        """Return all jobs sorted by priority (highest first)"""
        try:
            jobs = self.repository.get_all_jobs()
            # Sort by priority (highest first), then by submission time
            jobs.sort(key=lambda x: (-x.priority, x.submittedAt))
            return jobs
        except Exception as e:
            self.logger.error(f"Error getting all jobs: {e}")
            raise QueueOperationError(f"Failed to get all jobs: {e}")
    
    def get_job_by_id(self, job_id: str) -> Job:
        """Return a job by its ID"""
        try:
            if not job_id or not job_id.strip():
                raise InvalidJobDataError("Job ID cannot be empty")
            
            return self.repository.get_job_by_id(job_id.strip())
            
        except JobNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting job by ID: {e}")
            raise QueueOperationError(f"Failed to get job by ID: {e}")
    
    def get_next_job(self) -> Optional[Job]:
        """Return the highest priority job ready for processing"""
        try:
            jobs = self.get_all_jobs()  # Already sorted by priority
            
            # Get the first pending job (highest priority)
            next_job = next((job for job in jobs if job.status == 'pending'), None)
            
            if next_job:
                self.logger.info(f"Next job for processing: {next_job.id} (priority: {next_job.priority})")
            else:
                self.logger.info("No pending jobs available for processing")
            
            return next_job
            
        except Exception as e:
            self.logger.error(f"Error getting next job: {e}")
            raise QueueOperationError(f"Failed to get next job: {e}")