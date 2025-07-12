class PrinterStatus:
    def __init__(self, printerId, status, lastUpdated, progress=None, temperature=None, currentJobId=None, **kwargs):
        self.printerId = printerId
        self.status = status
        self.lastUpdated = lastUpdated
        self.progress = progress
        self.temperature = temperature
        self.currentJobId = currentJobId
        # Optionally store other fields from kwargs if needed