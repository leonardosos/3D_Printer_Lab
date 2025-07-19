#!/usr/bin/env python3
"""
Script to run the robot microservice.
This file serves as the entry point for the Docker container.
"""
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the application
from app.robot_service import main

if __name__ == "__main__":
    main()
