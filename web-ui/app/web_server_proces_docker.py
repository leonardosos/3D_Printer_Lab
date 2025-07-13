# This launch the web server in a Docker container
# The input() function is not suitable for Docker; it should be removed or commented out.
# Instead, the server should run indefinitely until the container is stopped externally.

from app.web_server import WebServer

if __name__ == '__main__':
    print("Starting WebServer from __main__")
    server = WebServer()
    server.start()
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, exiting...")
        server.stop()