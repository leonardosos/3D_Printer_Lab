FROM python:3.11-slim

# Install security updates
RUN apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y && apt-get autoremove -y && apt-get clean

# Install python3-full
#   RUN apt-get update && apt-get install -y python3-full && apt-get clean

# Copy Application Files & Requirements to /app
COPY ./app /app
COPY requirements.txt /app/requirements.txt

# Set the target container working directory to /app
WORKDIR /app

# Install Python Application Requirements
RUN pip3 install -r requirements.txt

# Ensure persistence files exist so Docker volume mounts them as files, not directories
RUN mkdir -p /app/persistence/save && \
    touch /app/persistence/save/temperature_history.csv && \
    touch /app/persistence/save/alert_history.csv

# Exposed Port of the API Server --> port_flowchart for more details
EXPOSE 8140

# Python Container Application Configurations
ENV PYTHONUNBUFFERED=1

# Since the python cmd is a module, we need to set the working directory to the root
# This is because the app.web_server module is located in the /app directory
WORKDIR / 

# Run the target application
CMD ["python3", "-m", "app.main"]
