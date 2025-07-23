FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Ensure config directory exists with default configuration
COPY app/config/ /app/config/

# Copy application code
COPY app/ /app/app/

# Create data directory for persistence and ensure it's writable
RUN mkdir -p data && chmod -R 755 data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose the port used by the priority queue manager (as defined in docker-compose.yml)
EXPOSE 8090

# Command to run the application
CMD ["python", "app/main.py"]