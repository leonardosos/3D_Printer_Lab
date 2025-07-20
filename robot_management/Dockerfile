# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CONFIG_PATH=/app/app/config.yaml

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port (optional, for documentation)
EXPOSE 8120

# Set entry point
CMD ["python", "-m", "app.main"]

# Metadata
LABEL maintainer="IoT Project Team" \
      version="1.0" \
      description="Robot Management Microservice"
