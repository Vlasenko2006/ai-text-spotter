"""
AI Pattern Detection - Targets specific characteristics of AI-generated text
Focuses on: wordiness, generic phrases, lack of specificity, predictable patterns
"""

import re
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Common AI buzzwords and generic phrases
AI_BUZZWORDS = {
    'comprehensive', 'exceptional', 'proficiency', 'leverage', 'utilize',
    'facilitate', 'implement', 'demonstrate', 'proven track record',
    'strong interest', 'excellent addition', 'esteemed', 'seamlessly',
    'consistently', 'diverse', 'enabling', 'encompasses', 'objectives',
    'capabilities', 'methodologies', 'proficiency', 'adept', 'exemplary'
}

AI_GENERIC_PHRASES = [
    r'I am writing to express my (?:strong )?interest',
    r'proven track record',
    r'comprehensive background',
    r'high-quality solutions',
    r'excellent addition to (?:your|the) (?:esteemed )?team',
    r'demonstrated exceptional',
    r'wide range of',
    r'enabling me to',
    r'adapt seamlessly',
    r'throughout my (?:professional )?career',
    r'I am confident that',
    r'I would be (?:an )?excellent',
    r'possess (?:a )?strong',
    r'my experience encompasses'
]

# Common repeated AI phrases (AI tends to reuse same patterns)
AI_REPEATED_PATTERNS = [
    r'I am \w+',  # "I am excited", "I am confident", "I am committed"
    r'I have \w+',  # "I have developed", "I have demonstrated"
    r'Furthermore[,]?',
    r'Moreover[,]?',
    r'Additionally[,]?',
    r'In addition[,]?',
    r'(?:my|the) (?:comprehensive|robust|extensive|strong)',
    r'will enable me to',
    r'I would be',
    r'looking forward to'
]

def calculate_ai_specific_features(text: str) -> Dict[str, float]:
    """
    Calculate features that specifically target AI-generated text patterns
    
    Returns scores where HIGHER = more AI-like (0.0 = human, 1.0 = AI)
    """
    text_lower = text.lower()
    words = text_lower.split()
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    if not words or not sentences:
        return {
            'ai_buzzword_density': 0.0,
            'repeated_pattern_score': 0.0,
            'generic_phrase_count': 0.0,
            'contraction_ratio': 0.0,  # Inverted: low = AI
            'specificity_score': 0.0,  # Inverted: low = AI
            'sentence_length_variance': 0.0,  # Inverted: low = AI
            'formal_language_score': 0.0
        }
    
    # 1. Buzzword density (AI uses more corporate jargon)
    buzzword_count = sum(1 for word in words if word in AI_BUZZWORDS)
    buzzword_density = min(buzzword_count / len(words) * 20, 1.0)  # Scale up
    
    # 2. Generic phrase count (AI uses template phrases)
    generic_count = sum(1 for pattern in AI_GENERIC_PHRASES if re.search(pattern, text_lower))
    generic_score = min(generic_count / len(sentences) * 2, 1.0)  # Normalize
    
    # 3. Contraction ratio (AI avoids contractions - formal style)
    contractions = len(re.findall(r"\w+[''](?:m|re|s|t|ve|d|ll)\b", text))
    contraction_ratio = contractions / len(sentences) if sentences else 0
    # INVERT: High contractions = human (score 0), Low contractions = AI (score 1)
    contraction_score = max(0, 1.0 - (contraction_ratio * 2))  # 0.5 contractions/sentence = human
    
    # 4. Specificity (AI is vague, humans give specifics)
    # Look for: numbers, proper nouns (capitals), dates, percentages
    numbers = len(re.findall(r'\b\d+[%]?\b', text))
    capitals = len(re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', text))  # Proper nouns
    specifics = numbers + capitals
    specificity_ratio = specifics / len(words) if words else 0
    # INVERT: High specificity = human (score 0), Low = AI (score 1)
    specificity_score = max(0, 1.0 - (specificity_ratio * 20))
    
    # 5. Sentence length variance (AI has uniform length, humans vary)
    sent_lengths = [len(s.split()) for s in sentences]
    if len(sent_lengths) > 1:
        import statistics
        variance = statistics.variance(sent_lengths)
        # INVERT: High variance = human (score 0), Low = AI (score 1)
        # Typical human variance: 50-200, AI variance: 10-30
        variance_score = max(0, 1.0 - (variance / 100))
    else:
        variance_score = 1.0  # Single sentence = uncertain, lean AI
    
    # 6. Formal language markers (AI is overly formal)
    formal_markers = len(re.findall(
        r'\b(?:thus|hence|moreover|furthermore|additionally|consequently|therefore|whereby)\b',
        text_lower
    ))
    formal_score = min(formal_markers / len(sentences), 1.0)
    
    # 7. Repeated pattern detection (NEW - Approach #3)
    # AI tends to reuse same sentence structures and phrases
    repeated_matches = {}
    for pattern in AI_REPEATED_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if len(matches) > 1:  # Only count if repeated
            repeated_matches[pattern] = len(matches)
    
    # Score based on how many patterns are repeated
    total_repetitions = sum(count - 1 for count in repeated_matches.values())  # -1 because first use is ok
    repeated_pattern_score = min(total_repetitions / max(len(sentences), 1), 1.0)
    
    if repeated_matches:
        logger.debug(f"Repeated patterns found: {repeated_matches}")
    
    features = {
        'ai_buzzword_density': round(buzzword_density, 4),
        'generic_phrase_count': round(generic_score, 4),
        'contraction_ratio': round(contraction_score, 4),  # Inverted
        'specificity_score': round(specificity_score, 4),  # Inverted
        'sentence_length_variance': round(variance_score, 4),  # Inverted
        'formal_language_score': round(formal_score, 4),
        'repeated_pattern_score': round(repeated_pattern_score, 4)  # NEW
    }
    
    logger.debug(f"AI-specific features: {features}")
    return features


def calculate_ai_pattern_score(text: str) -> float:
    """
    Calculate overall AI pattern score (0.0 = human, 1.0 = AI)
    Combines multiple AI-specific features
    """
    features = calculate_ai_specific_features(text)
    
    # Weighted combination (features already scaled 0-1 where 1=AI)
    weights = {
        'ai_buzzword_density': 0.18,        # Strong indicator
        'generic_phrase_count': 0.22,       # Very strong indicator
        'contraction_ratio': 0.12,          # Moderate (inverted)
        'specificity_score': 0.18,          # Strong (inverted)
        'sentence_length_variance': 0.08,   # Moderate (inverted)
        'formal_language_score': 0.08,      # Moderate
        'repeated_pattern_score': 0.14      # NEW - Strong (catches AI repetition)
    }
    
    score = sum(features[key] * weight for key, weight in weights.items())
    
    # Convert to human score (higher = more human)
    human_score = 1.0 - score
    
    logger.info(f"AI pattern analysis: AI_score={score:.3f}, Human_score={human_score:.3f}")
    return round(human_score, 4)  # Return as human score (consistent with other detectors)
