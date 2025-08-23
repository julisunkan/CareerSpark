import os
import json
from datetime import datetime
from typing import Dict, List, Any
from jinja2 import Template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import logging

def generate_resume_formats(resume_text: str, job_description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate all four resume formats with optimized content"""
    
    # Parse resume into structured data
    resume_data = parse_resume_text(resume_text)
    
    # Optimize content based on job description and analysis
    optimized_data = optimize_resume_content(resume_data, job_description, analysis)
    
    # Generate each format
    formats = {}
    format_types = ['chronological', 'functional', 'combination', 'targeted']
    
    for format_type in format_types:
        formats[format_type] = generate_format_specific_content(optimized_data, format_type, analysis)
    
    return formats

def parse_resume_text(text: str) -> Dict[str, Any]:
    """Parse resume text into structured sections"""
    if not text:
        return {}
    
    # Initialize structure
    resume_data = {
        'personal_info': {},
        'summary': '',
        'experience': [],
        'skills': [],
        'education': [],
        'achievements': [],
        'other_sections': []
    }
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    current_section = 'other'
    current_item = {}
    
    # Common section headers
    section_keywords = {
        'personal': ['contact', 'personal', 'name', 'email', 'phone'],
        'summary': ['summary', 'profile', 'objective', 'about'],
        'experience': ['experience', 'employment', 'work', 'career', 'jobs'],
        'skills': ['skills', 'competencies', 'technologies', 'tools', 'expertise'],
        'education': ['education', 'qualifications', 'academic', 'degree', 'school'],
        'achievements': ['achievements', 'awards', 'honors', 'accomplishments']
    }
    
    for line in lines:
        line_lower = line.lower()
        
        # Detect section headers
        section_detected = False
        for section, keywords in section_keywords.items():
            if any(keyword in line_lower for keyword in keywords) and len(line) < 100:
                if is_likely_header(line):
                    current_section = section
                    section_detected = True
                    break
        
        if section_detected:
            continue
        
        # Process content based on current section
        if current_section == 'personal':
            parse_personal_info(line, resume_data['personal_info'])
        elif current_section == 'summary':
            resume_data['summary'] += line + ' '
        elif current_section == 'experience':
            parse_experience_item(line, resume_data['experience'])
        elif current_section == 'skills':
            parse_skills(line, resume_data['skills'])
        elif current_section == 'education':
            parse_education_item(line, resume_data['education'])
        elif current_section == 'achievements':
            resume_data['achievements'].append(line)
        else:
            resume_data['other_sections'].append(line)
    
    # Clean up data
    resume_data['summary'] = resume_data['summary'].strip()
    
    return resume_data

def is_likely_header(line: str) -> bool:
    """Determine if a line is likely a section header"""
    return (len(line) < 50 and 
            line.isupper() or 
            line.count(' ') <= 3 and 
            not any(char.isdigit() for char in line))

def parse_personal_info(line: str, personal_info: Dict[str, str]):
    """Extract personal information from line"""
    import re
    
    # Email detection
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
    if email_match:
        personal_info['email'] = email_match.group()
    
    # Phone detection
    phone_match = re.search(r'[\+]?[1-9]?[\s.-]?\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}', line)
    if phone_match:
        personal_info['phone'] = phone_match.group()
    
    # If no specific patterns, might be name or address
    if not email_match and not phone_match:
        if 'name' not in personal_info and len(line.split()) <= 4:
            personal_info['name'] = line
        else:
            personal_info['address'] = personal_info.get('address', '') + line + ' '

def parse_experience_item(line: str, experience_list: List[Dict[str, Any]]):
    """Parse experience items"""
    # Simple heuristic: if line looks like a job title/company, start new item
    if (len(line.split()) <= 6 and 
        ('at' in line.lower() or '|' in line or '-' in line) and
        not line.startswith('•') and not line.startswith('-')):
        
        # New job entry
        job_parts = line.split(' at ') if ' at ' in line else line.split(' - ')
        experience_item = {
            'title': job_parts[0].strip() if job_parts else line,
            'company': job_parts[1].strip() if len(job_parts) > 1 else '',
            'duration': '',
            'responsibilities': []
        }
        experience_list.append(experience_item)
    
    elif experience_list and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
        # Responsibility/achievement
        experience_list[-1]['responsibilities'].append(line.lstrip('•-* '))
    
    elif experience_list:
        # Could be duration or additional info
        import re
        if re.search(r'(20\d{2}|19\d{2})', line):  # Contains year
            experience_list[-1]['duration'] = line
        else:
            experience_list[-1]['responsibilities'].append(line)

def parse_skills(line: str, skills_list: List[str]):
    """Parse skills from line"""
    # Split by common delimiters
    separators = [',', '•', '|', '·', ';']
    skills = [line]
    
    for sep in separators:
        if sep in line:
            skills = [skill.strip() for skill in line.split(sep) if skill.strip()]
            break
    
    for skill in skills:
        if skill and skill not in skills_list:
            skills_list.append(skill)

def parse_education_item(line: str, education_list: List[Dict[str, Any]]):
    """Parse education items"""
    # Simple heuristic for education entries
    if any(keyword in line.lower() for keyword in ['university', 'college', 'degree', 'bachelor', 'master', 'phd']):
        education_item = {
            'institution': '',
            'degree': '',
            'year': '',
            'details': line
        }
        education_list.append(education_item)

def optimize_resume_content(resume_data: Dict[str, Any], job_description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize resume content based on job analysis"""
    optimized = resume_data.copy()
    
    # Get missing keywords and suggestions from analysis
    missing_keywords = analysis.get('missing_keywords', [])
    job_skills = analysis.get('job_skills', [])
    suggestions = analysis.get('suggestions', [])
    matched_skills = analysis.get('skills_match', {}).get('matched_skills', [])
    
    # Optimize summary with missing keywords and suggestions
    optimized['summary'] = optimize_summary_comprehensive(
        optimized.get('summary', ''), missing_keywords, suggestions, job_description
    )
    
    # Optimize skills section with job requirements
    optimized['skills'] = optimize_skills_comprehensive(
        optimized['skills'], job_skills, missing_keywords, matched_skills
    )
    
    # Optimize experience descriptions with keywords and action words
    optimized['experience'] = optimize_experience_comprehensive(
        optimized['experience'], missing_keywords, suggestions, job_description
    )
    
    # Add achievements that incorporate missing keywords
    optimized['achievements'] = enhance_achievements(
        optimized.get('achievements', []), missing_keywords, suggestions
    )
    
    # Apply grammar corrections to all text content
    optimized = apply_grammar_corrections(optimized)
    
    return optimized

def apply_grammar_corrections(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply automatic grammar corrections to resume content"""
    from .grammar_checker import check_grammar
    corrected_data = resume_data.copy()
    
    # Correct summary
    if corrected_data.get('summary'):
        corrected_data['summary'] = correct_text_grammar(corrected_data['summary'])
    
    # Correct experience descriptions
    if corrected_data.get('experience'):
        for exp in corrected_data['experience']:
            if exp.get('responsibilities'):
                exp['responsibilities'] = [correct_text_grammar(resp) for resp in exp['responsibilities']]
            if exp.get('title'):
                exp['title'] = correct_text_grammar(exp['title'])
            if exp.get('company'):
                exp['company'] = correct_text_grammar(exp['company'])
    
    # Correct achievements
    if corrected_data.get('achievements'):
        corrected_data['achievements'] = [correct_text_grammar(achievement) for achievement in corrected_data['achievements']]
    
    # Correct skills (minimal correction for skills as they're usually keywords)
    if corrected_data.get('skills'):
        corrected_data['skills'] = [correct_skill_text(skill) for skill in corrected_data['skills']]
    
    return corrected_data

def correct_text_grammar(text: str) -> str:
    """Apply automatic grammar corrections to text"""
    if not text or len(text.strip()) < 3:
        return text
    
    from .grammar_checker import check_grammar
    
    try:
        grammar_result = check_grammar(text)
        
        if grammar_result['issues']:
            corrected_text = text
            
            # Apply simple corrections for common issues
            for issue in grammar_result['issues']:
                if issue['replacements'] and len(issue['replacements']) > 0:
                    # Apply the first suggested replacement
                    replacement = issue['replacements'][0]
                    offset = issue['offset']
                    length = issue['length']
                    
                    if offset + length <= len(corrected_text):
                        corrected_text = (corrected_text[:offset] + 
                                        replacement + 
                                        corrected_text[offset + length:])
            
            return corrected_text
        
        return text
    except Exception:
        # If grammar checking fails, return original text
        return text

def correct_skill_text(skill: str) -> str:
    """Apply minimal corrections to skill text"""
    if not skill:
        return skill
    
    # Basic capitalization and punctuation fixes for skills
    corrected = skill.strip()
    
    # Ensure proper capitalization for common technologies
    tech_corrections = {
        'javascript': 'JavaScript',
        'html': 'HTML',
        'css': 'CSS',
        'sql': 'SQL',
        'aws': 'AWS',
        'api': 'API',
        'ui': 'UI',
        'ux': 'UX',
        'powerbi': 'PowerBI',
        'github': 'GitHub'
    }
    
    corrected_lower = corrected.lower()
    for tech, proper_case in tech_corrections.items():
        if tech in corrected_lower:
            corrected = corrected.replace(tech, proper_case)
            corrected = corrected.replace(tech.upper(), proper_case)
    
    # Remove trailing punctuation from skills
    corrected = corrected.rstrip('.,;:')
    
    return corrected



def optimize_summary_comprehensive(summary: str, missing_keywords: List[str], suggestions: List[str], job_description: str) -> str:
    """Comprehensively optimize summary with missing keywords and suggestions"""
    if not summary:
        # Create a basic summary if none exists
        summary = "Experienced professional with strong background in delivering results and exceeding expectations."
    
    # Enhance summary with missing keywords
    enhanced_summary = summary.strip()
    keywords_to_add = missing_keywords[:3]  # Add top 3 missing keywords
    
    for keyword in keywords_to_add:
        if keyword.lower() not in enhanced_summary.lower():
            # Add keyword naturally to summary
            if 'experience' in enhanced_summary.lower():
                enhanced_summary = enhanced_summary.replace(
                    'experience',
                    f'experience in {keyword.lower()}'
                )
            else:
                enhanced_summary = f"{enhanced_summary.rstrip('.')}. Skilled in {keyword.lower()}."
    
    # Ensure summary ends with period
    if not enhanced_summary.endswith('.'):
        enhanced_summary += '.'
    
    return enhanced_summary

def optimize_skills_comprehensive(skills: List[str], job_skills: List[str], missing_keywords: List[str], matched_skills: List[str]) -> List[str]:
    """Comprehensively optimize skills with job requirements"""
    optimized_skills = skills.copy()
    
    # Add missing job skills that aren't already present
    for skill in job_skills[:5]:  # Add top 5 job skills
        skill_lower = skill.lower()
        if not any(skill_lower in existing_skill.lower() for existing_skill in optimized_skills):
            optimized_skills.append(skill)
    
    # Add missing keywords that are skill-related
    skill_keywords = [k for k in missing_keywords if len(k.split()) <= 2]  # Likely to be skills
    for keyword in skill_keywords[:3]:
        keyword_lower = keyword.lower()
        if not any(keyword_lower in existing_skill.lower() for existing_skill in optimized_skills):
            optimized_skills.append(keyword)
    
    # Ensure matched skills are properly formatted
    for i, skill in enumerate(optimized_skills):
        optimized_skills[i] = correct_skill_text(skill)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in optimized_skills:
        skill_lower = skill.lower()
        if skill_lower not in seen:
            seen.add(skill_lower)
            unique_skills.append(skill)
    
    return unique_skills

def optimize_experience_comprehensive(experience: List[Dict[str, Any]], missing_keywords: List[str], suggestions: List[str], job_description: str) -> List[Dict[str, Any]]:
    """Comprehensively optimize experience with keywords and impact statements"""
    optimized_exp = []
    action_verbs = ['Led', 'Managed', 'Developed', 'Implemented', 'Designed', 'Created', 'Improved', 'Optimized', 'Achieved', 'Delivered']
    
    for i, exp in enumerate(experience):
        optimized_item = exp.copy()
        
        # Enhance responsibilities with missing keywords and action words
        enhanced_responsibilities = []
        keywords_used = set()
        
        for j, resp in enumerate(exp.get('responsibilities', [])):
            enhanced_resp = resp.strip()
            
            # Ensure responsibility starts with action verb
            if not any(enhanced_resp.startswith(verb) for verb in action_verbs):
                # Find appropriate action verb
                if 'manage' in enhanced_resp.lower() or 'lead' in enhanced_resp.lower():
                    enhanced_resp = f"Led {enhanced_resp.lower()}"
                elif 'develop' in enhanced_resp.lower() or 'create' in enhanced_resp.lower():
                    enhanced_resp = f"Developed {enhanced_resp.lower()}"
                elif 'improve' in enhanced_resp.lower() or 'optimize' in enhanced_resp.lower():
                    enhanced_resp = f"Improved {enhanced_resp.lower()}"
                else:
                    enhanced_resp = f"Achieved {enhanced_resp.lower()}"
                
                enhanced_resp = enhanced_resp[0].upper() + enhanced_resp[1:]
            
            # Integrate relevant missing keywords naturally
            available_keywords = [k for k in missing_keywords if k.lower() not in enhanced_resp.lower() and k not in keywords_used]
            
            if available_keywords and j < 3:  # Only enhance first 3 responsibilities per job
                keyword = available_keywords[0]
                keywords_used.add(keyword)
                
                # Add keyword contextually
                if len(keyword.split()) == 1:
                    enhanced_resp = enhance_responsibility_with_keyword(enhanced_resp, keyword)
            
            # Add quantifiable impact if missing
            if not any(char.isdigit() for char in enhanced_resp) and j == 0:  # Add to first responsibility
                enhanced_resp = add_quantifiable_impact(enhanced_resp)
            
            enhanced_responsibilities.append(enhanced_resp)
        
        # Add new responsibility if we have remaining important keywords
        remaining_keywords = [k for k in missing_keywords[:3] if k not in keywords_used]
        if remaining_keywords and len(enhanced_responsibilities) < 5:
            new_responsibility = create_keyword_responsibility(remaining_keywords[0], job_description)
            if new_responsibility:
                enhanced_responsibilities.append(new_responsibility)
        
        optimized_item['responsibilities'] = enhanced_responsibilities
        optimized_exp.append(optimized_item)
    
    return optimized_exp

def generate_format_specific_content(resume_data: Dict[str, Any], format_type: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate content optimized for specific resume format"""
    
    content = {
        'format_type': format_type,
        'personal_info': resume_data.get('personal_info', {}),
        'summary': resume_data.get('summary', ''),
        'sections': []
    }
    
    if format_type == 'chronological':
        # Traditional chronological format
        content['sections'] = [
            {'title': 'Professional Experience', 'content': resume_data.get('experience', [])},
            {'title': 'Skills', 'content': resume_data.get('skills', [])},
            {'title': 'Education', 'content': resume_data.get('education', [])},
            {'title': 'Achievements', 'content': resume_data.get('achievements', [])}
        ]
    
    elif format_type == 'functional':
        # Skills-based format
        grouped_skills = group_skills_by_category(resume_data.get('skills', []))
        content['sections'] = [
            {'title': 'Core Competencies', 'content': grouped_skills},
            {'title': 'Professional Experience', 'content': resume_data.get('experience', [])},
            {'title': 'Education', 'content': resume_data.get('education', [])}
        ]
    
    elif format_type == 'combination':
        # Hybrid format
        content['sections'] = [
            {'title': 'Skills Summary', 'content': resume_data.get('skills', [])},
            {'title': 'Professional Experience', 'content': resume_data.get('experience', [])},
            {'title': 'Education', 'content': resume_data.get('education', [])},
            {'title': 'Additional Achievements', 'content': resume_data.get('achievements', [])}
        ]
    
    elif format_type == 'targeted':
        # Job-specific targeted format
        missing_keywords = analysis.get('missing_keywords', [])
        job_skills = analysis.get('job_skills', [])
        
        # Customize summary for job
        targeted_summary = create_targeted_summary(resume_data.get('summary', ''), missing_keywords)
        content['summary'] = targeted_summary
        
        # Prioritize relevant skills
        relevant_skills = prioritize_relevant_skills(resume_data.get('skills', []), job_skills)
        
        content['sections'] = [
            {'title': 'Relevant Skills', 'content': relevant_skills},
            {'title': 'Relevant Experience', 'content': resume_data.get('experience', [])},
            {'title': 'Education', 'content': resume_data.get('education', [])},
            {'title': 'Key Achievements', 'content': resume_data.get('achievements', [])}
        ]
    
    return content

def group_skills_by_category(skills: List[str]) -> Dict[str, List[str]]:
    """Group skills into categories for functional format"""
    categories = {
        'Technical Skills': [],
        'Programming Languages': [],
        'Tools & Technologies': [],
        'Soft Skills': [],
        'Other Skills': []
    }
    
    # Simple categorization based on keywords
    for skill in skills:
        skill_lower = skill.lower()
        
        if any(tech in skill_lower for tech in ['python', 'java', 'javascript', 'html', 'css', 'sql']):
            categories['Programming Languages'].append(skill)
        elif any(tool in skill_lower for tool in ['excel', 'powerbi', 'tableau', 'jira', 'git']):
            categories['Tools & Technologies'].append(skill)
        elif any(soft in skill_lower for soft in ['leadership', 'communication', 'teamwork', 'management']):
            categories['Soft Skills'].append(skill)
        elif any(tech in skill_lower for tech in ['aws', 'azure', 'docker', 'kubernetes', 'api']):
            categories['Technical Skills'].append(skill)
        else:
            categories['Other Skills'].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}

def create_targeted_summary(original_summary: str, missing_keywords: List[str]) -> str:
    """Create job-targeted summary"""
    if not original_summary:
        return f"Professional with expertise in {', '.join(missing_keywords[:3])}."
    
    # Enhance original summary with missing keywords
    targeted = original_summary
    
    if missing_keywords:
        targeted += f" Experienced in {', '.join(missing_keywords[:3])} with proven track record of success."
    
    return targeted

def prioritize_relevant_skills(skills: List[str], job_skills: List[str]) -> List[str]:
    """Prioritize skills based on job requirements"""
    if not job_skills:
        return skills
    
    relevant_skills = []
    other_skills = []
    
    for skill in skills:
        if any(job_skill.lower() in skill.lower() for job_skill in job_skills):
            relevant_skills.append(skill)
        else:
            other_skills.append(skill)
    
    # Return relevant skills first
    return relevant_skills + other_skills

# Helper functions for comprehensive optimization

def extract_key_requirements(job_description: str) -> List[str]:
    """Extract key requirements from job description"""
    requirements = []
    key_phrases = ['must have', 'required', 'essential', 'responsible for', 'you will', 'seeking']
    
    lines = job_description.lower().split('\n')
    for line in lines:
        if any(phrase in line for phrase in key_phrases):
            # Extract meaningful requirement
            cleaned_line = line.strip('• - * ').strip()
            if 3 < len(cleaned_line.split()) < 20:  # Reasonable length
                requirements.append(cleaned_line)
    
    return requirements[:5]  # Top 5 requirements

def create_value_proposition(requirements: List[str], keywords: List[str]) -> str:
    """Create value proposition based on job requirements"""
    if not requirements:
        return ""
    
    # Create general value proposition
    value_statements = [
        "Proven ability to deliver high-quality results in fast-paced environments.",
        "Strong track record of improving operational efficiency and driving growth.",
        "Demonstrated expertise in cross-functional collaboration and project leadership.",
        "Experience in implementing innovative solutions that exceed expectations."
    ]
    
    # Select most relevant value statement
    for statement in value_statements:
        if keywords and any(keyword.lower() in statement.lower() for keyword in keywords):
            return statement
    
    return value_statements[0]

def is_skill_like_keyword(keyword: str) -> bool:
    """Determine if a keyword is skill-like"""
    skill_indicators = [
        'software', 'tool', 'language', 'framework', 'technology', 'platform',
        'system', 'database', 'programming', 'development', 'analysis', 'management'
    ]
    
    return (len(keyword.split()) <= 2 and 
            (any(indicator in keyword.lower() for indicator in skill_indicators) or
             keyword.lower() in ['python', 'java', 'sql', 'excel', 'powerbi', 'tableau', 'git', 'aws', 'azure']))

def enhance_responsibility_with_keyword(responsibility: str, keyword: str) -> str:
    """Enhance responsibility statement with keyword naturally"""
    keyword_integrations = {
        'python': f"{responsibility} using Python programming",
        'sql': f"{responsibility} with SQL database queries",
        'excel': f"{responsibility} utilizing Excel analysis",
        'leadership': f"{responsibility} demonstrating strong leadership",
        'analytics': f"{responsibility} through data analytics",
        'automation': f"{responsibility} via process automation",
        'collaboration': f"{responsibility} through cross-team collaboration"
    }
    
    keyword_lower = keyword.lower()
    if keyword_lower in keyword_integrations:
        return keyword_integrations[keyword_lower]
    else:
        return f"{responsibility} leveraging {keyword} expertise"

def add_quantifiable_impact(responsibility: str) -> str:
    """Add quantifiable impact to responsibility if missing"""
    impact_additions = [
        "resulting in 20% efficiency improvement",
        "achieving 95% accuracy rate", 
        "reducing processing time by 30%",
        "supporting team of 10+ members",
        "managing budget of $50K+",
        "serving 100+ stakeholders"
    ]
    
    # Select appropriate impact based on responsibility content
    if 'team' in responsibility.lower() or 'manage' in responsibility.lower():
        return f"{responsibility}, supporting team of 10+ members"
    elif 'process' in responsibility.lower() or 'improve' in responsibility.lower():
        return f"{responsibility}, resulting in 20% efficiency improvement"
    elif 'develop' in responsibility.lower() or 'create' in responsibility.lower():
        return f"{responsibility}, achieving 95% accuracy rate"
    else:
        return f"{responsibility}, delivering measurable results"

def create_keyword_responsibility(keyword: str, job_description: str) -> str:
    """Create new responsibility that incorporates keyword"""
    responsibility_templates = [
        f"Implemented {keyword} solutions to streamline operations and improve efficiency",
        f"Utilized {keyword} expertise to drive project success and exceed targets", 
        f"Applied {keyword} skills to solve complex challenges and deliver results",
        f"Leveraged {keyword} knowledge to optimize processes and enhance performance"
    ]
    
    # Select template based on keyword type
    if keyword.lower() in ['leadership', 'management', 'collaboration']:
        return f"Demonstrated {keyword} skills to guide teams and achieve organizational goals"
    elif keyword.lower() in ['analytics', 'analysis', 'data']:
        return f"Conducted {keyword} to inform decision-making and drive strategic initiatives"
    else:
        return responsibility_templates[0]

def enhance_achievements(achievements: List[str], missing_keywords: List[str], suggestions: List[str]) -> List[str]:
    """Enhance achievements with missing keywords"""
    enhanced_achievements = achievements.copy()
    
    # Add achievement statements that incorporate missing keywords
    for keyword in missing_keywords[:3]:
        if keyword not in ' '.join(enhanced_achievements).lower():
            new_achievement = f"Successfully applied {keyword} expertise to deliver exceptional results"
            enhanced_achievements.append(new_achievement)
    
    # Add achievements based on suggestions
    if suggestions and len(enhanced_achievements) < 5:
        suggestion_achievements = [
            "Recognized for outstanding performance and commitment to excellence",
            "Consistently exceeded performance targets and quality standards",
            "Received positive feedback for innovative problem-solving approach"
        ]
        enhanced_achievements.extend(suggestion_achievements[:2])
    
    return enhanced_achievements

def generate_downloadable_resume(resume_data: Dict[str, Any], format_type: str, file_format: str, output_dir: str) -> str:
    """Generate downloadable resume file"""
    
    optimized_resume = resume_data['optimized_resumes'].get(format_type, {})
    
    if file_format == 'txt':
        return generate_txt_resume(resume_data, optimized_resume, format_type, output_dir)
    elif file_format == 'pdf':
        return generate_pdf_resume(resume_data, optimized_resume, format_type, output_dir)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")

def generate_txt_resume(resume_data: Dict[str, Any], optimized_resume: Dict[str, Any], format_type: str, output_dir: str) -> str:
    """Generate plain text resume"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"resume_{format_type}_{timestamp}.txt")
    
    content = []
    
    # Personal info
    personal_info = optimized_resume.get('personal_info', {})
    if personal_info.get('name'):
        content.append(personal_info['name'].upper())
        content.append('=' * len(personal_info['name']))
    
    if personal_info.get('email'):
        content.append(f"Email: {personal_info['email']}")
    if personal_info.get('phone'):
        content.append(f"Phone: {personal_info['phone']}")
    
    content.append('')
    
    # Summary
    if optimized_resume.get('summary'):
        content.append('SUMMARY')
        content.append('-' * 7)
        content.append(optimized_resume['summary'])
        content.append('')
    
    # Sections
    for section in optimized_resume.get('sections', []):
        content.append(section['title'].upper())
        content.append('-' * len(section['title']))
        
        if isinstance(section['content'], list):
            if section['title'] == 'Professional Experience':
                for exp in section['content']:
                    if isinstance(exp, dict):
                        content.append(f"{exp.get('title', '')} - {exp.get('company', '')}")
                        if exp.get('duration'):
                            content.append(f"Duration: {exp['duration']}")
                        for resp in exp.get('responsibilities', []):
                            content.append(f"• {resp}")
                        content.append('')
            else:
                for item in section['content']:
                    if isinstance(item, str):
                        content.append(f"• {item}")
                    elif isinstance(item, dict):
                        content.append(f"• {item.get('details', str(item))}")
        
        content.append('')
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return filename

def generate_pdf_resume(resume_data: Dict[str, Any], optimized_resume: Dict[str, Any], format_type: str, output_dir: str) -> str:
    """Generate PDF resume using WeasyPrint"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"resume_{format_type}_{timestamp}.pdf")
    
    # Create HTML content
    html_content = create_html_resume(optimized_resume, format_type)
    
    # Generate PDF
    try:
        font_config = FontConfiguration()
        html_doc = HTML(string=html_content)
        css_styles = CSS(string=get_pdf_css_styles())
        html_doc.write_pdf(filename, stylesheets=[css_styles], font_config=font_config)
    except Exception as e:
        # Fallback: create a simple PDF using FPDF if WeasyPrint fails
        logging.warning(f"WeasyPrint failed, using FPDF fallback: {e}")
        return generate_simple_pdf_resume(optimized_resume, format_type, output_dir)
    
    return filename

def create_html_resume(optimized_resume: Dict[str, Any], format_type: str) -> str:
    """Create HTML content for PDF generation"""
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Resume - {{ format_type }}</title>
    </head>
    <body>
        <div class="resume">
            <!-- Personal Info -->
            {% if personal_info.name %}
            <header class="header">
                <h1>{{ personal_info.name }}</h1>
                <div class="contact-info">
                    {% if personal_info.email %}<span>{{ personal_info.email }}</span>{% endif %}
                    {% if personal_info.phone %}<span>{{ personal_info.phone }}</span>{% endif %}
                </div>
            </header>
            {% endif %}
            
            <!-- Summary -->
            {% if summary %}
            <section class="summary">
                <h2>Summary</h2>
                <p>{{ summary }}</p>
            </section>
            {% endif %}
            
            <!-- Sections -->
            {% for section in sections %}
            <section class="section">
                <h2>{{ section.title }}</h2>
                
                {% if section.title == 'Professional Experience' %}
                    {% for exp in section.content %}
                        {% if exp.title %}
                        <div class="experience-item">
                            <h3>{{ exp.title }}{% if exp.company %} - {{ exp.company }}{% endif %}</h3>
                            {% if exp.duration %}<p class="duration">{{ exp.duration }}</p>{% endif %}
                            {% if exp.responsibilities %}
                            <ul>
                                {% for resp in exp.responsibilities %}
                                <li>{{ resp }}</li>
                                {% endfor %}
                            </ul>
                            {% endif %}
                        </div>
                        {% endif %}
                    {% endfor %}
                
                {% elif section.content is mapping %}
                    <!-- Grouped skills -->
                    {% for category, skills in section.content.items() %}
                    <div class="skill-category">
                        <h3>{{ category }}</h3>
                        <ul class="skills-list">
                            {% for skill in skills %}
                            <li>{{ skill }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endfor %}
                
                {% else %}
                    <!-- Regular list -->
                    <ul>
                        {% for item in section.content %}
                        <li>{{ item.details if item is mapping else item }}</li>
                        {% endfor %}
                    </ul>
                {% endif %}
            </section>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    
    template = Template(html_template)
    return template.render(
        personal_info=optimized_resume.get('personal_info', {}),
        summary=optimized_resume.get('summary', ''),
        sections=optimized_resume.get('sections', []),
        format_type=format_type.title()
    )

def get_pdf_css_styles() -> str:
    """Get CSS styles for PDF generation"""
    return """
    @page {
        size: A4;
        margin: 1in;
    }
    
    body {
        font-family: Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.4;
        color: #333;
    }
    
    .resume {
        max-width: 100%;
    }
    
    .header {
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
    }
    
    .header h1 {
        margin: 0;
        font-size: 24pt;
        font-weight: bold;
    }
    
    .contact-info {
        margin-top: 5px;
    }
    
    .contact-info span {
        margin: 0 15px;
    }
    
    h2 {
        color: #2c3e50;
        border-bottom: 1px solid #bdc3c7;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 10px;
        font-size: 14pt;
    }
    
    h3 {
        margin-top: 15px;
        margin-bottom: 5px;
        font-size: 12pt;
        font-weight: bold;
    }
    
    .summary p {
        text-align: justify;
        margin-bottom: 15px;
    }
    
    .experience-item {
        margin-bottom: 15px;
    }
    
    .duration {
        font-style: italic;
        color: #666;
        margin: 5px 0;
    }
    
    ul {
        margin: 5px 0 15px 20px;
        padding: 0;
    }
    
    li {
        margin-bottom: 3px;
    }
    
    .skills-list {
        display: flex;
        flex-wrap: wrap;
        list-style: none;
        margin: 0;
        padding: 0;
    }
    
    .skills-list li {
        background-color: #ecf0f1;
        padding: 5px 10px;
        margin: 3px;
        border-radius: 3px;
        font-size: 10pt;
    }
    
    .skill-category {
        margin-bottom: 15px;
    }
    """

def generate_simple_pdf_resume(optimized_resume: Dict[str, Any], format_type: str, output_dir: str) -> str:
    """Generate simple PDF using FPDF as fallback"""
    try:
        from fpdf import FPDF
    except ImportError:
        # If FPDF is not available, create a simple text file instead
        logging.warning("FPDF not available, creating text file instead")
        # Fallback to text format if FPDF fails
        return generate_txt_resume({}, optimized_resume, format_type, output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"resume_{format_type}_{timestamp}.pdf")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Personal info
    personal_info = optimized_resume.get('personal_info', {})
    if personal_info.get('name'):
        pdf.cell(0, 10, personal_info['name'], ln=True, align='C')
        pdf.ln(5)
    
    pdf.set_font('Arial', '', 12)
    if personal_info.get('email'):
        pdf.cell(0, 10, f"Email: {personal_info['email']}", ln=True, align='C')
    if personal_info.get('phone'):
        pdf.cell(0, 10, f"Phone: {personal_info['phone']}", ln=True, align='C')
    
    pdf.ln(10)
    
    # Summary
    if optimized_resume.get('summary'):
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'SUMMARY', ln=True)
        pdf.set_font('Arial', '', 10)
        
        # Handle long text
        summary_text = optimized_resume['summary']
        lines = []
        words = summary_text.split()
        current_line = ""
        
        for word in words:
            if pdf.get_string_width(current_line + word + " ") < 180:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        for line in lines:
            pdf.cell(0, 6, line, ln=True)
        
        pdf.ln(5)
    
    # Sections
    for section in optimized_resume.get('sections', []):
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, section['title'].upper(), ln=True)
        pdf.set_font('Arial', '', 10)
        
        if isinstance(section['content'], list):
            for item in section['content'][:5]:  # Limit items to fit on page
                if isinstance(item, str):
                    pdf.cell(0, 6, f"• {item[:80]}", ln=True)
                elif isinstance(item, dict):
                    if 'title' in item:
                        pdf.cell(0, 6, f"• {item.get('title', '')[:60]}", ln=True)
        
        pdf.ln(3)
    
    try:
        pdf.output(filename)
        return filename
    except Exception as e:
        raise Exception(f"Failed to generate PDF: {str(e)}")
