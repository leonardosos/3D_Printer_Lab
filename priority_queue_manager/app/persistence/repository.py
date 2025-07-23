from random import randint
from typing import List, Optional
from app.dto.job_request_dto import JobRequestDTO
from app.dto.job_response_dto import JobResponseDTO
from datetime import datetime, timezone

import logging

class PriorityQueueRepository:
    def __init__(self):
        # In-memory storage for jobs
        self._jobs: List[JobResponseDTO] = []
        self._job_counter = 0  # Counter for job IDs starting from 0. Not implemented in this version.
        self._logger = logging.getLogger(__name__)
        self._logger.info("PriorityQueueRepository initialized")

    def add_job(self, job_request: JobRequestDTO) -> JobResponseDTO:
        """
        Add a new job to the repository
        """
        
        job_id = f"{job_request.modelId}-{randint(10,99)}{randint(10,99)}"
        now = datetime.now(timezone.utc)
        
        new_job = JobResponseDTO(
            id=job_id,
            modelId=job_request.modelId,
            assignedPrinterId=job_request.printerId,
            priority=job_request.priority,
            status="pending",
            submittedAt=now,
            updatedAt=now
        )
        
        self._jobs.append(new_job)
        self._logger.info(f"Added job {job_id} with priority {job_request.priority}")
        return new_job

    def get_all_jobs(self) -> List[JobResponseDTO]:
        """
        Get all jobs
        """
        return self._jobs.copy()

    def set_jobs(self, jobs: List[JobResponseDTO]):
        """
        Set the jobs list (used by service for reordering)
        """
        self._jobs = jobs

    def get_job_by_id(self, job_id: str) -> Optional[JobResponseDTO]:
        """
        Get a specific job by its ID
        """
        for job in self._jobs:
            if job.id == job_id:
                return job
        return None

    def update_job_priority(self, job_id: str, new_priority: int) -> Optional[JobResponseDTO]:
        """
        Update the priority of an existing job
        """
        job = self.get_job_by_id(job_id)
        if job:
            job.priority = new_priority
            job.updatedAt = datetime.now(timezone.utc)
            self._logger.info(f"Updated job {job_id} priority to {new_priority}")
            return job
        return None

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a single job by ID
        Returns True if job was found and deleted, False otherwise
        """
        for i, job in enumerate(self._jobs):
            if job.id == job_id:
                deleted_job = self._jobs.pop(i)
                self._logger.info(f"Deleted job {job_id}")
                return True
        return False

    def delete_multiple_jobs(self, job_ids: List[str]) -> int:
        """
        Delete multiple jobs by their IDs
        Returns the number of jobs actually deleted
        """
        deleted_count = 0
        job_ids_set = set(job_ids)
        
        # Filter out jobs that should be deleted
        original_count = len(self._jobs)
        self._jobs = [job for job in self._jobs if job.id not in job_ids_set]
        deleted_count = original_count - len(self._jobs)
        
        if deleted_count > 0:
            self._logger.info(f"Deleted {deleted_count} jobs")
        
        return deleted_count

    def get_highest_priority_job(self) -> Optional[JobResponseDTO]:
        """
        Get the job with highest priority (consumer approach - removes the job)
        Returns None if no jobs are available
        """
        if not self._jobs:
            return None
        
        # Get the first job (highest priority) and remove it
        highest_priority_job = self._jobs.pop(0)
        self._logger.info(f"Retrieved and removed highest priority job {highest_priority_job.id}")
        return highest_priority_job

    def get_job_count(self) -> int:
        """
        Get the total number of jobs in the queue
        """
        return len(self._jobs)

    def update_job_status(self, job_id: str, status: str) -> Optional[JobResponseDTO]:
        """
        Update the status of an existing job
        """
        job = self.get_job_by_id(job_id)
        if job:
            job.status = status
            job.updatedAt = datetime.now(timezone.utc)
            self._logger.info(f"Updated job {job_id} status to {status}")
            return job
        return None

    def clear_all_jobs(self):
        """
        Remove all jobs from the queue (useful for testing)
        """
        count = len(self._jobs)
        self._jobs.clear()
        self._logger.info(f"Cleared all {count} jobs from queue")