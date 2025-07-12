from flask import Flask
from app.routes.dashboard import dashboard_bp
from app.routes.temperature import temperature_bp
from app.routes.printers import printers_bp
from app.routes.queue import queue_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(temperature_bp)
    app.register_blueprint(printers_bp)
    app.register_blueprint(queue_bp)
    return app

if __name__ == '__main__':
    # LOCAL RUNNING
    app = create_app()
    app.run(host='0.0.0.0', port=5000)