"""
Resume generator from job description
Creates a professional resume based solely on job description analysis
"""

import re
from typing import Dict, List, Any

def generate_resume_from_job_description(job_description: str) -> str:
    """Generate a complete resume from job description analysis"""
    
    # Extract key information from job description
    job_analysis = analyze_job_description(job_description)
    
    # Generate resume sections
    resume_sections = {
        'personal_info': generate_personal_info_section(),
        'summary': generate_professional_summary(job_analysis),
        'experience': generate_experience_section(job_analysis),
        'education': generate_education_section(job_analysis),
        'skills': generate_skills_section(job_analysis),
        'certifications': generate_certifications_section(job_analysis)
    }
    
    # Combine into formatted resume text
    return format_generated_resume(resume_sections)

def analyze_job_description(job_description: str) -> Dict[str, Any]:
    """Analyze job description to extract key requirements"""
    
    # Extract keywords and skills using simple pattern matching
    keywords_skills = extract_simple_keywords_and_skills(job_description)
    
    # Extract job title and company info
    job_title = extract_job_title(job_description)
    industry = extract_industry_context(job_description)
    
    # Extract requirements and qualifications
    requirements = extract_requirements(job_description)
    preferred_skills = extract_preferred_skills(job_description)
    
    # Extract experience level
    experience_level = extract_experience_level(job_description)
    
    return {
        'job_title': job_title,
        'industry': industry,
        'required_skills': keywords_skills.get('technical_skills', []),
        'soft_skills': keywords_skills.get('soft_skills', []),
        'keywords': keywords_skills.get('keywords', []),
        'requirements': requirements,
        'preferred_skills': preferred_skills,
        'experience_level': experience_level,
        'education_requirements': extract_education_requirements(job_description)
    }

def extract_job_title(job_description: str) -> str:
    """Extract likely job title from description"""
    
    # Common patterns for job titles
    title_patterns = [
        r'(?:position|role|title|job):\s*([^\n]+)',
        r'(?:seeking|hiring|looking for).*?([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'([A-Z][a-z]+\s+(?:Engineer|Developer|Manager|Analyst|Specialist|Coordinator|Assistant))'
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, job_description, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Professional"

def extract_industry_context(job_description: str) -> str:
    """Extract industry context from job description"""
    
    industry_keywords = {
        'technology': ['software', 'tech', 'IT', 'development', 'programming', 'digital'],
        'healthcare': ['medical', 'healthcare', 'hospital', 'clinical', 'patient'],
        'finance': ['financial', 'banking', 'investment', 'accounting', 'finance'],
        'education': ['education', 'teaching', 'academic', 'university', 'school'],
        'marketing': ['marketing', 'advertising', 'branding', 'social media', 'campaigns'],
        'sales': ['sales', 'business development', 'revenue', 'client acquisition'],
        'operations': ['operations', 'logistics', 'supply chain', 'manufacturing']
    }
    
    text_lower = job_description.lower()
    industry_scores = {}
    
    for industry, keywords in industry_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            industry_scores[industry] = score
    
    if industry_scores:
        return max(industry_scores.keys(), key=lambda k: industry_scores[k])
    
    return "business"

def extract_requirements(job_description: str) -> List[str]:
    """Extract key requirements from job description"""
    
    # Look for requirement sections
    requirement_patterns = [
        r'(?:requirements?|qualifications?|must have)[:)]?\s*[\n\r]*((?:[-*•]\s*[^\n\r]+[\n\r]*)+)',
        r'(?:you will|responsibilities?)[:)]?\s*[\n\r]*((?:[-*•]\s*[^\n\r]+[\n\r]*)+)',
        r'(?:looking for|seeking)[:)]?\s*[\n\r]*((?:[-*•]\s*[^\n\r]+[\n\r]*)+)'
    ]
    
    requirements = []
    
    for pattern in requirement_patterns:
        matches = re.finditer(pattern, job_description, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            bullet_points = re.findall(r'[-*•]\s*([^\n\r]+)', match.group(1))
            requirements.extend([point.strip() for point in bullet_points if len(point.strip()) > 10])
    
    return requirements[:8]  # Limit to most relevant

def extract_preferred_skills(job_description: str) -> List[str]:
    """Extract preferred skills and technologies"""
    
    # Common technical skills and tools
    skill_patterns = [
        r'\b(?:Python|Java|JavaScript|React|Node\.js|SQL|AWS|Docker|Kubernetes)\b',
        r'\b(?:Excel|PowerPoint|Salesforce|HubSpot|Google Analytics)\b',
        r'\b(?:project management|team leadership|communication|problem solving)\b'
    ]
    
    skills = set()
    
    for pattern in skill_patterns:
        matches = re.finditer(pattern, job_description, re.IGNORECASE)
        for match in matches:
            skills.add(match.group().title())
    
    return list(skills)[:10]  # Limit results

def extract_simple_keywords_and_skills(job_description: str) -> Dict[str, List[str]]:
    """Extract keywords and skills using simple pattern matching"""
    
    text_lower = job_description.lower()
    
    # Common technical skills
    technical_skills = []
    tech_patterns = [
        r'\b(?:python|java|javascript|react|node\.?js|sql|aws|docker|kubernetes|git)\b',
        r'\b(?:excel|powerpoint|word|outlook|salesforce|hubspot|tableau)\b',
        r'\b(?:html|css|php|ruby|go|swift|kotlin|scala|rust)\b',
        r'\b(?:machine learning|ai|data science|analytics|cloud computing)\b'
    ]
    
    for pattern in tech_patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            skill = match.group().replace('.', '').title()
            if skill not in technical_skills:
                technical_skills.append(skill)
    
    # Common soft skills
    soft_skills = []
    soft_patterns = [
        r'\b(?:communication|leadership|teamwork|problem solving|critical thinking)\b',
        r'\b(?:project management|time management|organization|attention to detail)\b',
        r'\b(?:collaboration|adaptability|creativity|innovation|analytical)\b'
    ]
    
    for pattern in soft_patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            skill = match.group().title()
            if skill not in soft_skills:
                soft_skills.append(skill)
    
    # Extract general keywords (nouns and important terms)
    keywords = []
    keyword_patterns = [
        r'\b(?:[A-Z][a-z]+ [A-Z][a-z]+)\b',  # Two-word capitalized phrases
        r'\b(?:development|design|management|analysis|strategy|optimization)\b'
    ]
    
    for pattern in keyword_patterns:
        matches = re.finditer(pattern, job_description)
        for match in matches:
            keyword = match.group().strip()
            if len(keyword) > 3 and keyword not in keywords:
                keywords.append(keyword)
    
    return {
        'technical_skills': technical_skills[:6],
        'soft_skills': soft_skills[:5],
        'keywords': keywords[:10]
    }

def extract_experience_level(job_description: str) -> str:
    """Extract required experience level"""
    
    # Look for experience indicators
    if re.search(r'\b(?:0-2|entry.level|junior|recent.graduate)\b', job_description, re.IGNORECASE):
        return "entry"
    elif re.search(r'\b(?:3-5|mid.level|intermediate)\b', job_description, re.IGNORECASE):
        return "mid"
    elif re.search(r'\b(?:5\+|senior|lead|principal)\b', job_description, re.IGNORECASE):
        return "senior"
    else:
        return "mid"  # Default to mid-level

def extract_education_requirements(job_description: str) -> str:
    """Extract education requirements"""
    
    if re.search(r'\b(?:PhD|doctorate|doctoral)\b', job_description, re.IGNORECASE):
        return "PhD"
    elif re.search(r'\b(?:master|MS|MBA|graduate)\b', job_description, re.IGNORECASE):
        return "Master's"
    elif re.search(r'\b(?:bachelor|BS|BA|undergraduate)\b', job_description, re.IGNORECASE):
        return "Bachelor's"
    else:
        return "Bachelor's"  # Default

def generate_personal_info_section() -> Dict[str, str]:
    """Generate placeholder personal information"""
    return {
        'name': '[Your Name]',
        'email': '[your.email@example.com]',
        'phone': '[Your Phone Number]',
        'location': '[Your City, State]',
        'linkedin': '[LinkedIn Profile URL]'
    }

def generate_professional_summary(job_analysis: Dict[str, Any]) -> str:
    """Generate professional summary based on job analysis"""
    
    experience_level = job_analysis.get('experience_level', 'mid')
    industry = job_analysis.get('industry', 'business').title()
    job_title = job_analysis.get('job_title', 'Professional')
    key_skills = job_analysis.get('required_skills', [])[:3]
    
    # Experience level descriptions
    experience_desc = {
        'entry': 'Motivated recent graduate',
        'mid': 'Experienced professional',
        'senior': 'Senior-level expert'
    }
    
    # Years of experience
    years = {
        'entry': '1-2',
        'mid': '3-5',
        'senior': '7+'
    }
    
    summary_base = f"{experience_desc.get(experience_level, 'Experienced professional')} with {years.get(experience_level, '3-5')} years of experience in {industry.lower()}."
    
    if key_skills:
        skills_text = ', '.join(key_skills[:3])
        summary_base += f" Proven expertise in {skills_text}."
    
    summary_base += f" Seeking to leverage strong analytical and problem-solving skills in a {job_title.lower()} role."
    
    return summary_base

def generate_experience_section(job_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate relevant work experience based on job requirements"""
    
    experience_level = job_analysis.get('experience_level', 'mid')
    industry = job_analysis.get('industry', 'business')
    requirements = job_analysis.get('requirements', [])
    
    # Number of jobs based on experience level
    num_jobs = {'entry': 1, 'mid': 2, 'senior': 3}.get(experience_level, 2)
    
    experiences = []
    
    for i in range(num_jobs):
        # Create experience entry
        exp = {
            'title': f'[Previous Job Title {i+1}]',
            'company': f'[Company Name {i+1}]',
            'duration': f'[Start Date - End Date]',
            'location': '[City, State]',
            'responsibilities': generate_responsibilities(requirements[:4], industry)
        }
        experiences.append(exp)
    
    return experiences

def generate_responsibilities(requirements: List[str], industry: str) -> List[str]:
    """Generate relevant responsibilities based on requirements"""
    
    if not requirements:
        # Default responsibilities by industry
        default_responsibilities = {
            'technology': [
                'Developed and maintained software applications',
                'Collaborated with cross-functional teams to deliver projects',
                'Implemented best practices for code quality and testing',
                'Participated in agile development processes'
            ],
            'business': [
                'Managed key client relationships and accounts',
                'Analyzed business processes and identified improvement opportunities',
                'Collaborated with stakeholders to achieve project objectives',
                'Prepared detailed reports and presentations for management'
            ]
        }
        return default_responsibilities.get(industry, default_responsibilities['business'])
    
    # Convert requirements to past-tense accomplishments
    responsibilities = []
    action_verbs = ['Developed', 'Implemented', 'Managed', 'Led', 'Created', 'Improved', 'Streamlined']
    
    for i, req in enumerate(requirements):
        # Clean up requirement text and convert to accomplishment
        clean_req = re.sub(r'^[-*•]\s*', '', req).strip()
        if clean_req and len(clean_req) > 15:
            # Add action verb if not present
            if not any(clean_req.lower().startswith(verb.lower()) for verb in action_verbs):
                verb = action_verbs[i % len(action_verbs)]
                clean_req = f"{verb} {clean_req.lower()}"
            
            responsibilities.append(clean_req.capitalize())
    
    return responsibilities[:4]  # Limit to 4 bullets

def generate_education_section(job_analysis: Dict[str, Any]) -> Dict[str, str]:
    """Generate education section based on requirements"""
    
    education_level = job_analysis.get('education_requirements', "Bachelor's")
    industry = job_analysis.get('industry', 'business')
    
    # Common degree fields by industry
    degree_fields = {
        'technology': 'Computer Science',
        'business': 'Business Administration',
        'finance': 'Finance',
        'healthcare': 'Health Sciences',
        'marketing': 'Marketing',
        'education': 'Education'
    }
    
    field = degree_fields.get(industry, 'Business Administration')
    
    return {
        'degree': f"{education_level} Degree in {field}",
        'school': '[University Name]',
        'graduation': '[Graduation Year]',
        'location': '[City, State]'
    }

def generate_skills_section(job_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
    """Generate skills section based on job requirements"""
    
    technical_skills = job_analysis.get('required_skills', [])
    soft_skills = job_analysis.get('soft_skills', [])
    industry = job_analysis.get('industry', 'business')
    
    # Default skills by industry if none found
    default_technical = {
        'technology': ['Python', 'SQL', 'Git', 'Agile Methodologies'],
        'business': ['Excel', 'PowerPoint', 'Data Analysis', 'Project Management'],
        'finance': ['Financial Modeling', 'Excel', 'Bloomberg', 'Risk Analysis'],
        'marketing': ['Google Analytics', 'Social Media', 'Content Creation', 'SEO']
    }
    
    default_soft = ['Communication', 'Leadership', 'Problem Solving', 'Team Collaboration', 'Time Management']
    
    return {
        'technical': technical_skills[:6] or default_technical.get(industry, default_technical['business']),
        'soft': soft_skills[:5] or default_soft
    }

def generate_certifications_section(job_analysis: Dict[str, Any]) -> List[str]:
    """Generate relevant certifications based on industry"""
    
    industry = job_analysis.get('industry', 'business')
    
    industry_certs = {
        'technology': ['AWS Certified Solutions Architect', 'Certified Scrum Master'],
        'business': ['Project Management Professional (PMP)', 'Six Sigma Green Belt'],
        'finance': ['CFA Level I', 'Financial Risk Manager (FRM)'],
        'marketing': ['Google Analytics Certified', 'HubSpot Inbound Marketing']
    }
    
    return industry_certs.get(industry, ['[Relevant Professional Certification]'])

def format_generated_resume(sections: Dict[str, Any]) -> str:
    """Format all sections into a complete resume"""
    
    personal = sections['personal_info']
    
    resume_text = f"""
{personal['name']}
{personal['email']} | {personal['phone']} | {personal['location']}
{personal['linkedin']}

PROFESSIONAL SUMMARY
{sections['summary']}

WORK EXPERIENCE
"""
    
    # Add experience entries
    for exp in sections['experience']:
        resume_text += f"""
{exp['title']}
{exp['company']} | {exp['location']} | {exp['duration']}
"""
        for resp in exp['responsibilities']:
            resume_text += f"• {resp}\n"
    
    # Add education
    education = sections['education']
    resume_text += f"""
EDUCATION
{education['degree']}
{education['school']} | {education['location']} | {education['graduation']}

TECHNICAL SKILLS
"""
    
    # Add skills
    skills = sections['skills']
    resume_text += f"• Technical: {', '.join(skills['technical'])}\n"
    resume_text += f"• Soft Skills: {', '.join(skills['soft'])}\n"
    
    # Add certifications if any
    if sections['certifications']:
        resume_text += f"\nCERTIFICATIONS\n"
        for cert in sections['certifications']:
            resume_text += f"• {cert}\n"
    
    return resume_text.strip()