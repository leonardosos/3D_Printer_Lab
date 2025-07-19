
from app.web_server import WebServer
import os

if __name__ == '__main__':
    
    debug_service = os.getenv("DEBUG", default="True")

    server = WebServer(debug=debug_service)
    server.start()

    import time
    try:
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Exception received: {e}")
        server.stop()