#!/usr/bin/python3

"""
WSGI configuration for PythonAnywhere deployment.

This module configures the Flask application for deployment on PythonAnywhere.
"""

import sys
import os

# Add your project directory to sys.path
project_home = '/home/yourusername/mysite'  # Update this path
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
# Generate a secure secret key: python3 -c "import secrets; print(secrets.token_hex(16))"
os.environ['SESSION_SECRET'] = 'your-secret-key-here'  # Change this to a random secret key

# Import your Flask application
from main import app as application

if __name__ == "__main__":
    application.run()