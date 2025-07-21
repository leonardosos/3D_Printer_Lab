FROM python:3.9-slim-bullseye

# Install security updates
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Copy Application Files & Requirements to /app
COPY ./app /app
COPY requirements.txt /app/requirements.txt

# Set the target container working directory to /app
WORKDIR /app

# Install Python Application Requirements
RUN pip3 install -r requirements.txt

# Exposed Port of the API Server
EXPOSE 8080

# Python Container Application Configurations
ENV PYTHONPATH=/app/
ENV PYTHONUNBUFFERED=1

# Since the python cmd is a module, we need to set the working directory to the root
WORKDIR / 

# Run the target application
CMD ["python3", "-m", "app.main"]