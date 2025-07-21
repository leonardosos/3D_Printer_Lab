FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Ensure config directory exists with default configuration
COPY config/ /app/config/

# Copy remaining application code
COPY app/ /app/app/
COPY run.py /app/

# Create directories for logs and ensure they're writable
RUN mkdir -p logs && chmod -R 755 logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8080

# Run the application
CMD ["python", "run.py"]
