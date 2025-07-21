FROM python:3.11-slim

# Install security updates
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Copy Application Files & Requirements to /app
COPY ./app /app
COPY ./config /config
COPY requirements.txt /app/requirements.txt

# Set the target container working directory to /app
WORKDIR /app

# Install Python Application Requirements
RUN pip3 install -r requirements.txt

# Python Container Application Configurations
ENV PYTHONPATH=/app/
ENV PYTHONUNBUFFERED=1

# Since the python cmd is a module, we need to set the working directory to the root
WORKDIR /

# Run the target application using module syntax
CMD ["python3", "-m", "app.main"]