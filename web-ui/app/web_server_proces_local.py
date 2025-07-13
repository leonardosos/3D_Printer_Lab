# This launch the web server locally
# The input() function is used to keep the server running until the user decides to stop it.

from app.web_server import WebServer

if __name__ == '__main__':
    print("Starting WebServer from __main__")
    server = WebServer()
    server.start()
    try:
        input("\n\n--> Press Enter to stop the server... <--\n\n")
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, exiting...")
    finally:
        server.stop()