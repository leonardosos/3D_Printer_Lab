import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.model.job_model import Job
from app.model.exceptions import PersistenceError, JobNotFoundError

class QueuePersistence:
    def __init__(self, file_path: str = "data/queue_data.json"):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
        self.jobs: List[Job] = []  # In-memory storage
        self._ensure_directory()
        self._load_jobs_from_file()
    
    def _ensure_directory(self):
        """Ensure the data directory exists"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _load_jobs_from_file(self):
        """Load jobs from file into memory on initialization"""
        try:
            if not os.path.exists(self.file_path):
                self.logger.info(f"No persistence file found at {self.file_path}, starting with empty queue")
                self.jobs = []
                return
            
            with open(self.file_path, 'r') as f:
                jobs_data = json.load(f)
            
            # Convert dictionaries to Job objects
            self.jobs = []
            for job_dict in jobs_data:
                # Convert string timestamps back to datetime objects
                if 'submittedAt' in job_dict and isinstance(job_dict['submittedAt'], str):
                    job_dict['submittedAt'] = datetime.fromisoformat(job_dict['submittedAt'])
                if 'updatedAt' in job_dict and isinstance(job_dict['updatedAt'], str):
                    job_dict['updatedAt'] = datetime.fromisoformat(job_dict['updatedAt'])
                
                job = Job(
                    id=job_dict['id'],
                    modelId=job_dict['modelId'],
                    assignedPrinterId=job_dict.get('assignedPrinterId'),
                    priority=job_dict.get('priority', 0),
                    status=job_dict.get('status', 'pending'),
                    submittedAt=job_dict.get('submittedAt'),
                    updatedAt=job_dict.get('updatedAt')
                )
                self.jobs.append(job)
            
            self.logger.info(f"Successfully loaded {len(self.jobs)} jobs from {self.file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load jobs: {e}")
            self.jobs = []
            raise PersistenceError(f"Failed to load jobs: {e}")
    
    def _save_jobs_to_file(self):
        """Save current jobs to file"""
        try:
            # Convert Job objects to dictionaries
            serializable_jobs = []
            for job in self.jobs:
                job_dict = {
                    'id': job.id,
                    'modelId': job.modelId,
                    'assignedPrinterId': job.assignedPrinterId,
                    'priority': job.priority,
                    'status': job.status,
                    'submittedAt': job.submittedAt.isoformat() if job.submittedAt else None,
                    'updatedAt': job.updatedAt.isoformat() if job.updatedAt else None
                }
                serializable_jobs.append(job_dict)
            
            with open(self.file_path, 'w') as f:
                json.dump(serializable_jobs, f, indent=2)
            
            self.logger.info(f"Successfully saved {len(self.jobs)} jobs to {self.file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save jobs: {e}")
            raise PersistenceError(f"Failed to save jobs: {e}")
    
    def add_job(self, job: Job) -> Job:
        """Add a job to the repository"""
        self.jobs.append(job)
        self._save_jobs_to_file()
        return job
    
    def get_job_by_id(self, job_id: str) -> Job:
        """Get a job by its ID"""
        job = next((job for job in self.jobs if job.id == job_id), None)
        if not job:
            raise JobNotFoundError(job_id)
        return job
    
    def update_job(self, job: Job) -> Job:
        """Update an existing job"""
        # Find and replace the job
        for i, existing_job in enumerate(self.jobs):
            if existing_job.id == job.id:
                self.jobs[i] = job
                self._save_jobs_to_file()
                return job
        raise JobNotFoundError(job.id)
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job by ID"""
        job = self.get_job_by_id(job_id)  # This will raise JobNotFoundError if not found
        self.jobs.remove(job)
        self._save_jobs_to_file()
        return True
    
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs"""
        return self.jobs.copy()
    
    def delete_multiple_jobs(self, job_ids: List[str]) -> int:
        """Delete multiple jobs by IDs"""
        deleted_count = 0
        jobs_to_remove = []
        
        for job_id in job_ids:
            job = next((job for job in self.jobs if job.id == job_id), None)
            if job:
                jobs_to_remove.append(job)
                deleted_count += 1
        
        # Remove found jobs
        for job in jobs_to_remove:
            self.jobs.remove(job)
        
        if deleted_count > 0:
            self._save_jobs_to_file()
        
        return deleted_count
    
    def clear_all_jobs(self):
        """Clear all jobs (for testing purposes)"""
        self.jobs = []
        self._save_jobs_to_file()

    # Legacy methods for backward compatibility (deprecated)
    def save_jobs(self, jobs: List[Dict[str, Any]]) -> bool:
        """Legacy method - deprecated, use repository methods instead"""
        self.logger.warning("save_jobs method is deprecated, use repository methods instead")
        return True
    
    def load_jobs(self) -> List[Dict[str, Any]]:
        """Legacy method - deprecated, use repository methods instead"""
        self.logger.warning("load_jobs method is deprecated, use repository methods instead")
        return []