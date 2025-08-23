from typing import Dict, List, Any

def calculate_resume_score(analysis: Dict[str, Any], grammar_results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate comprehensive resume score (0-100)"""
    
    # Weight factors for different aspects
    weights = {
        'keyword_match': 0.35,      # 35% - Keyword matching with job
        'skills_match': 0.25,       # 25% - Skills alignment
        'semantic_similarity': 0.20, # 20% - Overall content similarity
        'grammar': 0.15,            # 15% - Grammar and writing quality
        'completeness': 0.05        # 5% - Resume completeness
    }
    
    # Calculate individual scores
    keyword_score = calculate_keyword_score(analysis)
    skills_score = calculate_skills_score(analysis)
    semantic_score = analysis.get('semantic_similarity', 0)
    grammar_score = grammar_results.get('score', 95.0)
    completeness_score = calculate_completeness_score(analysis)
    
    # Calculate weighted overall score
    overall_score = (
        keyword_score * weights['keyword_match'] +
        skills_score * weights['skills_match'] +
        semantic_score * weights['semantic_similarity'] +
        grammar_score * weights['grammar'] +
        completeness_score * weights['completeness']
    )
    
    # Ensure score is between 0 and 100
    overall_score = max(0, min(100, overall_score))
    
    # Determine score category and recommendations
    category, recommendations = get_score_category_and_recommendations(overall_score)
    
    return {
        'overall_score': round(overall_score, 1),
        'category': category,
        'breakdown': {
            'keyword_match': round(keyword_score, 1),
            'skills_match': round(skills_score, 1),
            'semantic_similarity': round(semantic_score, 1),
            'grammar': round(grammar_score, 1),
            'completeness': round(completeness_score, 1)
        },
        'weights': weights,
        'recommendations': recommendations,
        'improvement_potential': calculate_improvement_potential(overall_score, {
            'keyword_match': keyword_score,
            'skills_match': skills_score,
            'semantic_similarity': semantic_score,
            'grammar': grammar_score,
            'completeness': completeness_score
        })
    }

def calculate_keyword_score(analysis: Dict[str, Any]) -> float:
    """Calculate keyword matching score"""
    keyword_overlap = analysis.get('keyword_overlap', 0)
    
    # Score based on keyword overlap percentage
    if keyword_overlap >= 80:
        return 100
    elif keyword_overlap >= 60:
        return 85
    elif keyword_overlap >= 40:
        return 70
    elif keyword_overlap >= 25:
        return 55
    elif keyword_overlap >= 10:
        return 40
    else:
        return 20

def calculate_skills_score(analysis: Dict[str, Any]) -> float:
    """Calculate skills matching score"""
    skills_match = analysis.get('skills_match', {})
    
    if not skills_match:
        return 50  # Default neutral score if no skills analysis
    
    skills_percentage = skills_match.get('percentage', 0)
    
    # Score based on skills match percentage
    if skills_percentage >= 90:
        return 100
    elif skills_percentage >= 75:
        return 90
    elif skills_percentage >= 60:
        return 80
    elif skills_percentage >= 45:
        return 70
    elif skills_percentage >= 30:
        return 60
    elif skills_percentage >= 15:
        return 45
    else:
        return 30

def calculate_completeness_score(analysis: Dict[str, Any]) -> float:
    """Calculate resume completeness score based on content analysis"""
    
    # Check for key resume components
    resume_keywords = analysis.get('resume_keywords', [])
    resume_skills = analysis.get('resume_skills', [])
    
    completeness_factors = {
        'has_keywords': len(resume_keywords) >= 10,  # At least 10 keywords
        'has_skills': len(resume_skills) >= 3,       # At least 3 skills
        'keyword_diversity': len(set(resume_keywords)) >= 8,  # Diverse keywords
        'sufficient_content': len(resume_keywords) >= 15      # Substantial content
    }
    
    # Calculate score based on factors
    met_factors = sum(1 for factor in completeness_factors.values() if factor)
    completeness_score = (met_factors / len(completeness_factors)) * 100
    
    return completeness_score

def get_score_category_and_recommendations(score: float) -> tuple:
    """Get score category and recommendations based on overall score"""
    
    if score >= 85:
        category = "Excellent"
        recommendations = [
            "Your resume is very well-matched to this position!",
            "Consider minor formatting improvements for perfection",
            "You're ready to apply with confidence"
        ]
    elif score >= 70:
        category = "Good"
        recommendations = [
            "Your resume is well-suited for this position",
            "Add a few more relevant keywords to improve matching",
            "Consider reviewing and enhancing key achievements"
        ]
    elif score >= 55:
        category = "Fair"
        recommendations = [
            "Your resume shows potential but needs improvement",
            "Focus on adding missing keywords and skills",
            "Enhance your experience descriptions with specific achievements"
        ]
    elif score >= 40:
        category = "Needs Improvement"
        recommendations = [
            "Significant improvements needed to match this position",
            "Add relevant keywords and skills from the job description",
            "Consider restructuring content to better align with requirements"
        ]
    else:
        category = "Poor Match"
        recommendations = [
            "Major revisions needed to match this job",
            "Consider if this position aligns with your experience",
            "Focus on highlighting transferable skills and relevant experience"
        ]
    
    return category, recommendations

def calculate_improvement_potential(overall_score: float, breakdown: Dict[str, float]) -> List[Dict[str, Any]]:
    """Calculate specific improvement opportunities"""
    
    improvements = []
    
    # Find areas with lowest scores
    sorted_areas = sorted(breakdown.items(), key=lambda x: x[1])
    
    for area, score in sorted_areas:
        if score < 70:  # Focus on areas scoring below 70
            potential_gain = min(25, 90 - score)  # Realistic improvement potential
            
            if area == 'keyword_match':
                improvements.append({
                    'area': 'Keyword Optimization',
                    'current_score': score,
                    'potential_gain': potential_gain,
                    'priority': 'High' if score < 50 else 'Medium',
                    'actions': [
                        'Add missing keywords from job description',
                        'Use industry-specific terminology',
                        'Include relevant technical terms'
                    ]
                })
            
            elif area == 'skills_match':
                improvements.append({
                    'area': 'Skills Alignment',
                    'current_score': score,
                    'potential_gain': potential_gain,
                    'priority': 'High' if score < 60 else 'Medium',
                    'actions': [
                        'Highlight relevant technical skills',
                        'Add missing required skills',
                        'Organize skills by relevance'
                    ]
                })
            
            elif area == 'semantic_similarity':
                improvements.append({
                    'area': 'Content Relevance',
                    'current_score': score,
                    'potential_gain': potential_gain,
                    'priority': 'Medium',
                    'actions': [
                        'Rewrite experience using job description language',
                        'Focus on relevant achievements',
                        'Align content with job requirements'
                    ]
                })
            
            elif area == 'grammar':
                improvements.append({
                    'area': 'Writing Quality',
                    'current_score': score,
                    'potential_gain': potential_gain,
                    'priority': 'Medium' if score > 60 else 'High',
                    'actions': [
                        'Fix grammar and spelling errors',
                        'Improve sentence structure',
                        'Use professional language'
                    ]
                })
            
            elif area == 'completeness':
                improvements.append({
                    'area': 'Resume Completeness',
                    'current_score': score,
                    'potential_gain': potential_gain,
                    'priority': 'Low',
                    'actions': [
                        'Add more relevant experience details',
                        'Include additional skills',
                        'Expand achievement descriptions'
                    ]
                })
    
    # Sort by potential impact (priority and potential gain)
    priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
    improvements.sort(key=lambda x: (priority_order[x['priority']], x['potential_gain']), reverse=True)
    
    return improvements[:3]  # Return top 3 improvement opportunities

def generate_score_insights(score_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
    """Generate detailed insights about the resume score"""
    
    insights = []
    breakdown = score_data['breakdown']
    overall_score = score_data['overall_score']
    
    # Overall performance insight
    if overall_score >= 80:
        insights.append(f"🎉 Excellent match! Your resume scores {overall_score}% for this position.")
    elif overall_score >= 65:
        insights.append(f"👍 Good match! Your resume scores {overall_score}% with room for improvement.")
    else:
        insights.append(f"⚠️ Your resume scores {overall_score}% and needs significant improvements.")
    
    # Keyword insights
    keyword_score = breakdown['keyword_match']
    missing_keywords = len(analysis.get('missing_keywords', []))
    
    if keyword_score >= 80:
        insights.append("✅ Excellent keyword matching with the job description")
    elif keyword_score >= 60:
        insights.append(f"📝 Good keyword coverage, but consider adding {missing_keywords} missing terms")
    else:
        insights.append(f"🔍 Low keyword match - add {min(missing_keywords, 10)} key terms from job description")
    
    # Skills insights
    skills_score = breakdown['skills_match']
    skills_data = analysis.get('skills_match', {})
    missing_skills = len(skills_data.get('missing_skills', []))
    
    if skills_score >= 75:
        insights.append("🛠️ Strong skills alignment with job requirements")
    elif missing_skills > 0:
        insights.append(f"🎯 Consider highlighting {min(missing_skills, 5)} additional relevant skills")
    
    # Grammar insights
    grammar_score = breakdown['grammar']
    if grammar_score < 85:
        insights.append("📖 Consider proofreading to improve writing quality")
    elif grammar_score >= 95:
        insights.append("✏️ Excellent writing quality and grammar")
    
    # Semantic similarity insights
    semantic_score = breakdown['semantic_similarity']
    if semantic_score < 40:
        insights.append("🔄 Consider rewriting sections to better match job language")
    elif semantic_score >= 70:
        insights.append("🎯 Great content alignment with job requirements")
    
    return insights

def get_competitive_score_context(score: float) -> Dict[str, Any]:
    """Provide context about how competitive the score is"""
    
    # Based on typical resume screening benchmarks
    percentiles = {
        90: "Top 10% - Highly competitive",
        80: "Top 25% - Very competitive", 
        70: "Top 50% - Competitive",
        60: "Top 75% - Moderately competitive",
        50: "Average - Needs improvement",
        0: "Below average - Significant work needed"
    }
    
    for threshold, description in percentiles.items():
        if score >= threshold:
            return {
                'percentile': threshold,
                'description': description,
                'competitive_level': 'High' if threshold >= 80 else 'Medium' if threshold >= 60 else 'Low'
            }
    
    return {
        'percentile': 0,
        'description': "Below average - Significant work needed",
        'competitive_level': 'Low'
    }
