FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories for logs and ensure they're writable
RUN mkdir -p logs && chmod -R 755 logs

EXPOSE 5000

CMD ["python", "app.py"]
