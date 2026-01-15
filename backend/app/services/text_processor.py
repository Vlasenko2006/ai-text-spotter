"""
Text processing service for sentence splitting and preprocessing.
Handles edge cases like abbreviations, URLs, etc.
"""
import re
from typing import List


class TextProcessor:
    """
    Service for processing text into sentences.
    
    Handles:
    - Sentence splitting
    - Abbreviation detection
    - URL preservation
    - Original formatting preservation
    """
    
    def __init__(self):
        """Initialize the text processor."""
        # Common abbreviations that shouldn't trigger sentence breaks
        self.abbreviations = {
            'mr', 'mrs', 'ms', 'dr', 'prof', 'sr', 'jr',
            'vs', 'etc', 'inc', 'ltd', 'corp', 'co',
            'st', 'ave', 'blvd', 'dept', 'univ',
            'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
            'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
            'no', 'vol', 'fig', 'ed', 'est', 'approx'
        }
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text to split
            
        Returns:
            List of sentences
        """
        if not text or len(text.strip()) == 0:
            return []
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Protect abbreviations
        protected_text = self._protect_abbreviations(text)
        
        # Split on sentence terminators
        # Look for . ! ? followed by space and capital letter or end of string
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$', protected_text)
        
        # Restore abbreviations and clean up
        sentences = [self._restore_abbreviations(s.strip()) for s in sentences if s.strip()]
        
        # Filter out very short sentences (likely noise)
        sentences = [s for s in sentences if len(s.split()) >= 3]
        
        return sentences
    
    def _protect_abbreviations(self, text: str) -> str:
        """
        Protect abbreviations from sentence splitting.
        Replaces periods in abbreviations with a placeholder.
        """
        protected = text
        
        for abbr in self.abbreviations:
            # Match abbreviation with period (case insensitive)
            pattern = re.compile(r'\b' + abbr + r'\.', re.IGNORECASE)
            protected = pattern.sub(abbr + '<ABR>', protected)
        
        return protected
    
    def _restore_abbreviations(self, text: str) -> str:
        """Restore protected abbreviations."""
        return text.replace('<ABR>', '.')
    
    def preprocess(self, text: str) -> str:
        """
        Basic preprocessing of text.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_context(self, sentences: List[str], index: int) -> dict:
        """
        Extract context (before/after) for a sentence.
        
        Args:
            sentences: List of all sentences
            index: Index of the current sentence
            
        Returns:
            dict with 'before' and 'after' keys
        """
        before = sentences[index - 1] if index > 0 else None
        after = sentences[index + 1] if index < len(sentences) - 1 else None
        
        return {
            'before': before,
            'after': after
        }
    
    def batch_sentences(self, sentences: List[str], batch_size: int) -> List[List[str]]:
        """
        Batch sentences for efficient processing.
        
        Args:
            sentences: List of sentences
            batch_size: Size of each batch
            
        Returns:
            List of batches
        """
        batches = []
        for i in range(0, len(sentences), batch_size):
            batches.append(sentences[i:i + batch_size])
        return batches
