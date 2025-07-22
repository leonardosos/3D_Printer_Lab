FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/job_handler

# Create working directory
WORKDIR /job_handler

# Copy everything into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose port (if you're running an API or server)
EXPOSE 8115

# Optional: Create logs folder
RUN mkdir -p /logs

# Run the main app module (adjust this if your main file is elsewhere)
CMD ["python3", "-m", "app.main"]
