class PersistenceError(Exception):
    """Exception raised for errors in persistence layer"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class JobNotFoundError(Exception):
    """Exception raised when a job is not found"""
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.message = f"Job with ID '{job_id}' not found"
        super().__init__(self.message)

class InvalidJobDataError(Exception):
    """Exception raised for invalid job data"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class QueueOperationError(Exception):
    """Exception raised for queue operation errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)