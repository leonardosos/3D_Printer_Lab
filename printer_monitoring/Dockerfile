FROM python:3.11-slim

# Update and clean apt packages
RUN apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y && apt-get autoremove -y && apt-get clean

# Copy Application Files & Requirements to /app
COPY ./app /app
COPY requirements.txt /app/requirements.txt

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Exposed Port of the API Server --> port_flowchart for more details
EXPOSE 8110

# Since the python cmd is a module, we need to set the working directory to the root
WORKDIR / 

# Run the target application
CMD ["python3", "-m", "app.main"]