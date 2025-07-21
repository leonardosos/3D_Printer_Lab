#!/usr/bin/env python3
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the application
from app.main import app

if __name__ == '__main__':
    app.run(host=app.config.get('HOST', '0.0.0.0'), 
            port=app.config.get('PORT', 8080))
