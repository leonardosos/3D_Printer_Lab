FROM python:3.9-slim

WORKDIR /app

COPY fake_api_response.py /app/fake_api_response.py

RUN pip install flask

EXPOSE 8080

CMD ["python3", "fake_api_response.py"]