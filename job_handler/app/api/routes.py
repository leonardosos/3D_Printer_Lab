from fastapi import APIRouter, HTTPException
from app.dto.job_dto import Job
from typing import Optional
from datetime import datetime
import logging

router = APIRouter()

# Dummy in-memory job queue for demonstration - not used in the real implementation
job_queue = [
    Job(
        id="job-123",
        modelId="model-456",
        assignedPrinterId=None,
        priority=10,
        status="pending",
        submittedAt=datetime(2025, 6, 15, 8, 30, 0),
        updatedAt=datetime(2025, 6, 15, 8, 30, 0)
    )
]

@router.get("/prioritary_job", response_model=Job)
def get_prioritary_job():
    if not job_queue:
        logging.info("No jobs available in the queue.")
        raise HTTPException(status_code=404, detail="No jobs available")
    job = job_queue.pop(0)
    logging.info(f"Returning job: {job}")
    return job

