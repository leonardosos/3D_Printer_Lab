from typing import List, Optional
from app.persistence.repository import PriorityQueueRepository
from app.dto.job_request_dto import JobRequestDTO
from app.dto.job_response_dto import JobResponseDTO
import logging
from flask import jsonify

class PriorityQueueManager:
    def __init__(self):
        self.repository = PriorityQueueRepository()
        self.logger = logging.getLogger(__name__)
    
    def add_job(self, job_request: JobRequestDTO) -> JobResponseDTO:
        """Add job and reorder queue"""
        new_job = self.repository.add_job(job_request)
        self._reorder_queue()
        return new_job
    
    def update_job_priority(self, job_id: str, new_priority: int) -> Optional[JobResponseDTO]:
        """Update priority and reorder queue"""
        updated_job = self.repository.update_job_priority(job_id, new_priority)
        if updated_job:
            self._reorder_queue()   # <---------------------------------
        return updated_job
    
    def get_all_jobs(self) -> List[JobResponseDTO]:
        """Get all jobs (already sorted)"""
        self._reorder_queue()
        return self.repository.get_all_jobs()
    
    def delete_job(self, job_id: str) -> bool:
        """Delete single job"""
        return self.repository.delete_job(job_id)
    
    def delete_multiple_jobs(self, job_ids: List[str]) -> int:
        """Delete multiple jobs"""
        return self.repository.delete_multiple_jobs(job_ids)
    
    def get_highest_priority_job(self) -> Optional[JobResponseDTO]:
        """Get and remove highest priority job"""
        self._reorder_queue()   # <---------------------------------
        return self.repository.get_highest_priority_job()
    
    def get_job_count(self) -> int:
        """Get total job count"""
        return self.repository.get_job_count()
    
    def _reorder_queue(self):
        """Sort jobs by priority (highest first), then by submission time"""
        jobs = self.repository.get_all_jobs()
        jobs.sort(key=lambda job: (-int(job.priority), job.submittedAt))
        self.repository.set_jobs(jobs)
        self.logger.debug("Queue reordered by priority")

    @staticmethod
    def validate_model_id(data):
        # Validate required fields
        if 'modelId' not in data:
            return jsonify({"error": "modelId is required"}), 400