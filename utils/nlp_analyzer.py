import spacy
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List, Any
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

# Load spaCy model (use small model for efficiency)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model not found, try to install it
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def analyze_resume_vs_job(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Comprehensive analysis of resume against job description"""
    
    # Clean and preprocess texts
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_description)
    
    # Extract keywords and skills
    resume_keywords = extract_keywords(resume_clean)
    job_keywords = extract_keywords(job_clean)
    
    # Calculate keyword overlap
    keyword_overlap = calculate_keyword_overlap(resume_keywords, job_keywords)
    
    # Extract technical skills
    resume_skills = extract_technical_skills(resume_clean)
    job_skills = extract_technical_skills(job_clean)
    
    # Calculate skills match
    skills_match = calculate_skills_match(resume_skills, job_skills)
    
    # Calculate semantic similarity
    semantic_similarity = calculate_semantic_similarity(resume_clean, job_clean)
    
    # Find missing keywords
    missing_keywords = find_missing_keywords(resume_keywords, job_keywords)
    
    # Generate suggestions
    suggestions = generate_improvement_suggestions(
        missing_keywords, skills_match, semantic_similarity
    )
    
    return {
        'keyword_overlap': keyword_overlap,
        'skills_match': skills_match,
        'semantic_similarity': semantic_similarity,
        'missing_keywords': missing_keywords,
        'resume_keywords': list(resume_keywords),
        'job_keywords': list(job_keywords),
        'resume_skills': list(resume_skills),
        'job_skills': list(job_skills),
        'suggestions': suggestions
    }

def clean_text(text: str) -> str:
    """Clean and normalize text for NLP processing"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def extract_keywords(text: str) -> set:
    """Extract important keywords using spaCy NLP"""
    if not text:
        return set()
    
    doc = nlp(text)
    keywords = set()
    
    # Extract entities, noun phrases, and important words
    for token in doc:
        # Skip stop words, punctuation, and spaces
        if (not token.is_stop and 
            not token.is_punct and 
            not token.is_space and 
            len(token.text) > 2 and
            token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']):
            keywords.add(token.lemma_.lower())
    
    # Extract named entities
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PRODUCT', 'WORK_OF_ART', 'LANGUAGE']:
            keywords.add(ent.text.lower())
    
    # Extract noun phrases
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3:  # Limit to reasonable phrase length
            keywords.add(chunk.text.lower())
    
    return keywords

def extract_technical_skills(text: str) -> set:
    """Extract technical skills and technologies"""
    if not text:
        return set()
    
    # Common technical skills patterns
    skill_patterns = [
        r'\b(?:python|java|javascript|html|css|sql|react|angular|vue|node\.?js)\b',
        r'\b(?:aws|azure|gcp|docker|kubernetes|git|github|gitlab)\b',
        r'\b(?:machine learning|data science|ai|artificial intelligence)\b',
        r'\b(?:agile|scrum|devops|ci/cd|jenkins|terraform)\b',
        r'\b(?:excel|powerbi|tableau|salesforce|jira|confluence)\b',
        r'\b(?:linux|windows|macos|ubuntu|centos)\b',
        r'\b(?:mysql|postgresql|mongodb|oracle|redis|elasticsearch)\b',
        r'\b(?:rest|api|microservices|soap|graphql)\b'
    ]
    
    skills = set()
    text_lower = text.lower()
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        skills.update(matches)
    
    # Use spaCy to find additional technical terms
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG'] and len(ent.text) > 2:
            # Check if it looks like a technology
            if any(tech in ent.text.lower() for tech in ['js', 'sql', 'db', 'os', 'ai', 'ml']):
                skills.add(ent.text.lower())
    
    return skills

def calculate_keyword_overlap(resume_keywords: set, job_keywords: set) -> float:
    """Calculate percentage overlap between resume and job keywords"""
    if not job_keywords:
        return 0.0
    
    intersection = resume_keywords.intersection(job_keywords)
    return len(intersection) / len(job_keywords) * 100

def calculate_skills_match(resume_skills: set, job_skills: set) -> Dict[str, Any]:
    """Calculate skills matching analysis"""
    if not job_skills:
        return {
            'percentage': 0.0,
            'matched_skills': [],
            'missing_skills': []
        }
    
    matched_skills = list(resume_skills.intersection(job_skills))
    missing_skills = list(job_skills - resume_skills)
    percentage = len(matched_skills) / len(job_skills) * 100
    
    return {
        'percentage': percentage,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills
    }

def calculate_semantic_similarity(resume_text: str, job_text: str) -> float:
    """Calculate semantic similarity using TF-IDF and cosine similarity"""
    if not resume_text or not job_text:
        return 0.0
    
    try:
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )
        
        texts = [resume_text, job_text]
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return similarity * 100
    
    except Exception:
        return 0.0

def find_missing_keywords(resume_keywords: set, job_keywords: set) -> List[str]:
    """Find important keywords missing from resume"""
    missing = job_keywords - resume_keywords
    
    # Sort by potential importance (longer keywords first, then alphabetically)
    missing_list = sorted(missing, key=lambda x: (-len(x), x))
    
    # Return top 20 missing keywords
    return missing_list[:20]

def generate_improvement_suggestions(missing_keywords: List[str], 
                                   skills_match: Dict[str, Any], 
                                   semantic_similarity: float) -> List[str]:
    """Generate actionable improvement suggestions"""
    suggestions = []
    
    # Keyword suggestions
    if missing_keywords:
        suggestions.append(
            f"Add these important keywords: {', '.join(missing_keywords[:5])}"
        )
    
    # Skills suggestions
    if skills_match['missing_skills']:
        suggestions.append(
            f"Highlight these missing skills: {', '.join(skills_match['missing_skills'][:3])}"
        )
    
    # Semantic similarity suggestions
    if semantic_similarity < 30:
        suggestions.append(
            "Consider rephrasing your experience to better match the job description language"
        )
    elif semantic_similarity < 50:
        suggestions.append(
            "Your resume partially matches the job requirements. Add more relevant keywords."
        )
    
    # General suggestions
    if len(missing_keywords) > 10:
        suggestions.append(
            "Your resume appears to be generic. Tailor it more specifically to this job."
        )
    
    if not suggestions:
        suggestions.append("Your resume is well-matched to the job description!")
    
    return suggestions

def extract_resume_sections(resume_text: str) -> Dict[str, str]:
    """Extract common resume sections for better analysis"""
    sections = {
        'summary': '',
        'experience': '',
        'skills': '',
        'education': '',
        'other': resume_text
    }
    
    # Simple section detection based on common headers
    section_patterns = {
        'summary': r'(?i)(summary|profile|objective|about)',
        'experience': r'(?i)(experience|employment|work|career)',
        'skills': r'(?i)(skills|competencies|technologies|tools)',
        'education': r'(?i)(education|qualifications|academic|degree)'
    }
    
    lines = resume_text.split('\n')
    current_section = 'other'
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Check if this line is a section header
        for section, pattern in section_patterns.items():
            if re.search(pattern, line_stripped) and len(line_stripped) < 50:
                current_section = section
                break
        else:
            # Add content to current section
            if sections[current_section]:
                sections[current_section] += '\n' + line_stripped
            else:
                sections[current_section] = line_stripped
    
    return sections
