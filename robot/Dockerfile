FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create directories for volumes
RUN mkdir -p /app/config /app/logs

# Set Python path to include app directory
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Entry point
CMD ["python", "-m", "app.main"]
