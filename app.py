import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'

# Ensure upload and download directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Initialize models and routes
with app.app_context():
    import models
    import routes
    
    # Start periodic cleanup on app startup
    try:
        from utils.cleanup import schedule_periodic_cleanup, run_full_cleanup
        
        # Run initial cleanup
        cleanup_results = run_full_cleanup()
        if cleanup_results['upload_files_deleted'] + cleanup_results['download_files_deleted'] + cleanup_results['data_entries_removed'] > 0:
            app.logger.info(f"Startup cleanup completed: {cleanup_results}")
        
        # Schedule periodic cleanup
        schedule_periodic_cleanup()
        
    except Exception as e:
        app.logger.warning(f"Failed to initialize cleanup system: {e}")
