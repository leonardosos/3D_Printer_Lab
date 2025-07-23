FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY app/ app/
COPY config/ config/

# Make sure config directory exists
RUN mkdir -p config

# Run as non-root user for better security
RUN useradd -m appuser
USER appuser

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Command to run the application
CMD ["python", "-m", "app.main"]

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('localhost', 1883)) or exit(1)"
