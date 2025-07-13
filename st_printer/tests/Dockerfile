FROM python:3.9-slim

WORKDIR /app

COPY st_printer_tester.py /app/st_printer_tester.py
COPY requirements.txt /app/requirements.txt

ENV MQTT_BROKER=broker

RUN pip install -r requirements.txt

# job handler port
EXPOSE 8115

# Python Container Application Configurations
ENV PYTHONPATH=/app/
ENV PYTHONUNBUFFERED=1

CMD ["python3", "st_printer_tester.py"]