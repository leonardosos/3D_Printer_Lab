class Job:
    def __init__(self, id, modelId, priority, status, submittedAt, updatedAt, assignedPrinterId=None, **kwargs):
        self.id = id
        self.modelId = modelId
        self.priority = priority
        self.status = status
        self.submittedAt = submittedAt
        self.updatedAt = updatedAt
        self.assignedPrinterId = assignedPrinterId
        # Optionally store other fields from kwargs if needed