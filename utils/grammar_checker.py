import language_tool_python
from typing import List, Dict, Any
import logging

# Initialize LanguageTool
tool = None

def get_language_tool():
    """Get or initialize LanguageTool instance"""
    global tool
    if tool is None:
        try:
            tool = language_tool_python.LanguageTool('en-US')
        except Exception as e:
            logging.error(f"Failed to initialize LanguageTool: {e}")
            tool = None
    return tool

def check_grammar(text: str) -> Dict[str, Any]:
    """Check grammar and style issues in text"""
    if not text or not text.strip():
        return {
            'issues': [],
            'issue_count': 0,
            'suggestions': [],
            'score': 100.0
        }
    
    tool = get_language_tool()
    if tool is None:
        return {
            'issues': [],
            'issue_count': 0,
            'suggestions': ['Grammar checking service is currently unavailable'],
            'score': 95.0  # Default good score when service unavailable
        }
    
    try:
        # Check for grammar issues
        matches = tool.check(text)
        
        # Process matches into structured format
        issues = []
        suggestions = []
        
        for match in matches:
            issue = {
                'message': match.message,
                'context': match.context,
                'offset': match.offset,
                'length': match.errorLength,
                'replacements': match.replacements[:3] if match.replacements else [],
                'rule_id': match.ruleId,
                'category': match.category
            }
            issues.append(issue)
            
            # Generate suggestions for common issues
            if match.replacements:
                # Use correct attributes for LanguageTool match object
                try:
                    context_offset = getattr(match, 'contextOffset', getattr(match, 'context_offset', 0))
                    error_length = getattr(match, 'errorLength', getattr(match, 'error_length', len(match.replacements[0]) if match.replacements else 1))
                    
                    if hasattr(match, 'context') and match.context:
                        original_text = match.context[context_offset:context_offset + error_length] if context_offset + error_length <= len(match.context) else match.context[context_offset:]
                        suggestion = f"Consider changing '{original_text}' to '{match.replacements[0]}'"
                    else:
                        suggestion = f"Consider using '{match.replacements[0]}' instead"
                    suggestions.append(suggestion)
                except Exception:
                    # Fallback suggestion
                    suggestion = f"Consider using '{match.replacements[0]}' for better grammar"
                    suggestions.append(suggestion)
        
        # Calculate grammar score
        word_count = len(text.split())
        if word_count == 0:
            score = 100.0
        else:
            # Penalize based on error density
            error_density = len(issues) / word_count
            score = max(0, 100 - (error_density * 1000))  # Rough scoring formula
        
        # Add general grammar suggestions
        if len(issues) > 5:
            suggestions.append("Consider reviewing your text for grammar and style improvements")
        elif len(issues) > 0:
            suggestions.append("Minor grammar improvements detected")
        else:
            suggestions.append("Good grammar and writing style!")
        
        return {
            'issues': issues,
            'issue_count': len(issues),
            'suggestions': suggestions,
            'score': score
        }
    
    except Exception as e:
        logging.error(f"Grammar check failed: {e}")
        return {
            'issues': [],
            'issue_count': 0,
            'suggestions': ['Grammar checking encountered an error'],
            'score': 90.0  # Default decent score on error
        }

def get_style_suggestions(text: str) -> List[str]:
    """Get style and clarity suggestions"""
    suggestions = []
    
    if not text:
        return suggestions
    
    # Basic style checks
    sentences = text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    
    if avg_sentence_length > 25:
        suggestions.append("Consider breaking down long sentences for better readability")
    
    # Check for passive voice (simple heuristic)
    passive_indicators = ['was', 'were', 'been', 'being']
    passive_count = sum(1 for word in text.lower().split() if word in passive_indicators)
    
    if passive_count > len(text.split()) * 0.1:  # More than 10% passive indicators
        suggestions.append("Consider using more active voice to make your resume more impactful")
    
    # Check for buzzwords overuse
    buzzwords = ['responsible for', 'duties included', 'worked on', 'helped with']
    buzzword_count = sum(1 for phrase in buzzwords if phrase in text.lower())
    
    if buzzword_count > 3:
        suggestions.append("Replace generic phrases with specific achievements and metrics")
    
    return suggestions

def highlight_grammar_issues(text: str, issues: List[Dict[str, Any]]) -> str:
    """Add HTML highlighting to grammar issues in text"""
    if not issues:
        return text
    
    # Sort issues by offset in reverse order to avoid offset shifts
    sorted_issues = sorted(issues, key=lambda x: x['offset'], reverse=True)
    
    highlighted_text = text
    
    for issue in sorted_issues:
        start = issue['offset']
        end = start + issue['length']
        
        original = highlighted_text[start:end]
        replacement = f'<span class="grammar-issue" title="{issue["message"]}">{original}</span>'
        
        highlighted_text = highlighted_text[:start] + replacement + highlighted_text[end:]
    
    return highlighted_text

def check_resume_specific_issues(text: str) -> List[str]:
    """Check for resume-specific writing issues"""
    issues = []
    
    if not text:
        return issues
    
    text_lower = text.lower()
    
    # Check for first person pronouns
    first_person = ['i ', 'me ', 'my ', 'myself']
    if any(pronoun in text_lower for pronoun in first_person):
        issues.append("Avoid using first-person pronouns (I, me, my) in your resume")
    
    # Check for incomplete sentences
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines:
        if len(line.split()) > 3 and not line.endswith(('.', '!', '?', ':')):
            if not any(char.isdigit() for char in line):  # Skip lines that might be dates/numbers
                issues.append("Ensure all bullet points and sentences are complete")
                break
    
    # Check for consistent tense
    past_tense_indicators = ['ed ', 'managed', 'developed', 'created', 'led']
    present_tense_indicators = ['manage', 'develop', 'create', 'lead']
    
    past_count = sum(1 for indicator in past_tense_indicators if indicator in text_lower)
    present_count = sum(1 for indicator in present_tense_indicators if indicator in text_lower)
    
    if past_count > 0 and present_count > 0:
        issues.append("Maintain consistent verb tense (use past tense for previous roles, present for current)")
    
    return issues
