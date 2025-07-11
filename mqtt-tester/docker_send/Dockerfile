FROM python:3.11-slim

WORKDIR /app

COPY json_producer_device_1.py .

COPY model/ /app/model/
RUN touch /app/model/__init__.py

RUN pip install paho-mqtt

CMD ["python", "json_producer_device_1.py"]