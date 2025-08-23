import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List

def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """
    Delete files older than specified hours from a directory
    Returns number of files deleted
    """
    if not os.path.exists(directory):
        return 0
    
    deleted_count = 0
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Check file age
            file_age = current_time - os.path.getmtime(file_path)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    logging.info(f"Deleted old file: {filename}")
                except Exception as e:
                    logging.warning(f"Failed to delete {filename}: {e}")
    
    except Exception as e:
        logging.error(f"Error cleaning up directory {directory}: {e}")
    
    return deleted_count

def cleanup_old_resume_data(data_file: str, max_age_hours: int = 24) -> int:
    """
    Remove old resume entries from JSON data file
    Returns number of entries removed
    """
    if not os.path.exists(data_file):
        return 0
    
    try:
        with open(data_file, 'r') as f:
            resumes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0
    
    if not resumes:
        return 0
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    original_count = len(resumes)
    
    # Filter out old entries
    filtered_resumes = []
    for resume in resumes:
        try:
            # Parse timestamp
            resume_time = datetime.fromisoformat(resume.get('timestamp', ''))
            if resume_time > cutoff_time:
                filtered_resumes.append(resume)
        except (ValueError, TypeError):
            # Keep entries with invalid timestamps (safety)
            filtered_resumes.append(resume)
    
    # Save filtered data
    if len(filtered_resumes) != original_count:
        try:
            with open(data_file, 'w') as f:
                json.dump(filtered_resumes, f, indent=2)
            
            removed_count = original_count - len(filtered_resumes)
            logging.info(f"Removed {removed_count} old resume entries from data file")
            return removed_count
        except Exception as e:
            logging.error(f"Failed to update data file: {e}")
            return 0
    
    return 0

def run_full_cleanup(upload_dir: str = 'uploads', 
                    download_dir: str = 'downloads', 
                    data_file: str = 'data/resumes.json',
                    max_age_hours: int = 24) -> dict:
    """
    Run complete cleanup of all temporary files and data
    Returns summary of cleanup results
    """
    logging.info(f"Starting cleanup of files older than {max_age_hours} hours")
    
    results = {
        'upload_files_deleted': 0,
        'download_files_deleted': 0,
        'data_entries_removed': 0,
        'total_cleanup_time': 0
    }
    
    start_time = time.time()
    
    # Clean upload directory
    results['upload_files_deleted'] = cleanup_old_files(upload_dir, max_age_hours)
    
    # Clean download directory  
    results['download_files_deleted'] = cleanup_old_files(download_dir, max_age_hours)
    
    # Clean old data entries
    results['data_entries_removed'] = cleanup_old_resume_data(data_file, max_age_hours)
    
    results['total_cleanup_time'] = int((time.time() - start_time) * 100) / 100
    
    total_items = (results['upload_files_deleted'] + 
                  results['download_files_deleted'] + 
                  results['data_entries_removed'])
    
    logging.info(f"Cleanup completed: {total_items} items removed in {results['total_cleanup_time']:.2f}s")
    
    return results

def schedule_periodic_cleanup():
    """
    Schedule periodic cleanup to run in background
    This is a simple implementation - in production, use a proper task scheduler
    """
    import threading
    import time
    
    def cleanup_worker():
        while True:
            try:
                # Wait 1 hour between cleanups
                time.sleep(3600)  
                run_full_cleanup()
            except Exception as e:
                logging.error(f"Error in cleanup worker: {e}")
                # Continue running even if cleanup fails
                time.sleep(3600)
    
    # Start cleanup thread as daemon (won't prevent app shutdown)
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    logging.info("Periodic cleanup scheduler started")

def manual_cleanup_now():
    """
    Trigger immediate cleanup - useful for testing or manual maintenance
    """
    return run_full_cleanup()