"""
Production configuration for PythonAnywhere deployment.
This file contains production-specific settings.
"""

import os
import logging

# Production logging configuration
def configure_production_logging():
    """Configure logging for production environment."""
    logging.basicConfig(
        level=logging.INFO,  # Reduce log verbosity in production
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('/home/yourusername/mysite/logs/app.log'),  # Update path
            logging.StreamHandler()
        ]
    )

# Production environment variables
PRODUCTION_ENV = {
    'FLASK_ENV': 'production',
    'DEBUG': False,
    'TESTING': False,
    'LOG_LEVEL': 'INFO'
}

# Security settings for production
SECURITY_CONFIG = {
    'SECRET_KEY_MIN_LENGTH': 32,
    'SESSION_COOKIE_SECURE': True,  # Requires HTTPS
    'SESSION_COOKIE_HTTPONLY': True,
    'PERMANENT_SESSION_LIFETIME': 3600  # 1 hour
}

# File size and timeout limits for production
PRODUCTION_LIMITS = {
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    'GRAMMAR_CHECK_TIMEOUT': 30,  # 30 seconds
    'NLP_PROCESSING_TIMEOUT': 60,  # 1 minute
    'PDF_GENERATION_TIMEOUT': 120  # 2 minutes
}