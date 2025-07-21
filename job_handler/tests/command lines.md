 
 # run test-mosquitto broker:

docker run -it --rm -p 1883:1883 eclipse-mosquitto

# run the main program from the IoT_project folder:

python -m job_handler.app.main

# publish a printer progress input json:

"C:\Program Files\mosquitto\mosquitto_pub.exe" -h localhost -p 1883 -t "device/printer/printer-1/progress" -m "{\"printerId\": \"printer-1\", \"jobId\": \"job-123\", \"status\": \"idle\", \"progress\": 100, \"timestamp\": \"2025-07-20T12:00:00Z\"}"

# listen for the robot manager output json:

& "C:\Program Files\mosquitto\mosquitto_sub.exe" -h localhost -p 1883 -t "device/printers" -v

# listen for the printer manager output json:

& "C:\Program Files\mosquitto\mosquitto_sub.exe" -h localhost -p 1883 -t "device/printer/+/assignement" -v
