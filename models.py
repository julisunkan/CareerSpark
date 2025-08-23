import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

class ResumeHistory:
    """Simple JSON-based storage for resume history"""
    
    def __init__(self, data_file='data/resumes.json'):
        self.data_file = data_file
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure the data file exists"""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
    
    def _load_all(self) -> List[Dict[str, Any]]:
        """Load all resume entries (private method for internal use)"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_resume(self, resume_data: Dict[str, Any]) -> str:
        """Save a resume analysis and return the ID"""
        resumes = self._load_all()
        
        # Generate a simple ID based on timestamp
        resume_id = str(int(datetime.now().timestamp() * 1000))
        
        resume_entry = {
            'id': resume_id,
            'timestamp': datetime.now().isoformat(),
            'original_filename': resume_data.get('original_filename'),
            'original_text': resume_data.get('original_text'),
            'job_description': resume_data.get('job_description'),
            'analysis': resume_data.get('analysis'),
            'score': resume_data.get('score'),
            'suggestions': resume_data.get('suggestions'),
            'optimized_resumes': resume_data.get('optimized_resumes', {})
        }
        
        resumes.append(resume_entry)
        
        with open(self.data_file, 'w') as f:
            json.dump(resumes, f, indent=2)
        
        return resume_id
    
    
    def load_by_id(self, resume_id: str) -> Dict[str, Any]:
        """Load a specific resume by ID"""
        resumes = self._load_all()
        for resume in resumes:
            if resume['id'] == resume_id:
                return resume
        return {}
    
    def cleanup_old_entries(self, max_age_hours: int = 24) -> int:
        """Remove resume entries older than specified hours"""
        resumes = self._load_all()
        if not resumes:
            return 0
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        original_count = len(resumes)
        
        # Filter out old entries
        filtered_resumes = []
        for resume in resumes:
            try:
                resume_time = datetime.fromisoformat(resume.get('timestamp', ''))
                if resume_time > cutoff_time:
                    filtered_resumes.append(resume)
            except (ValueError, TypeError):
                # Keep entries with invalid timestamps
                filtered_resumes.append(resume)
        
        # Save if changes were made
        if len(filtered_resumes) != original_count:
            with open(self.data_file, 'w') as f:
                json.dump(filtered_resumes, f, indent=2)
            
            return original_count - len(filtered_resumes)
        
        return 0
    

# Global instance
resume_history = ResumeHistory()
