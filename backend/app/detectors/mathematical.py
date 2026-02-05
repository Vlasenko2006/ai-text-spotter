"""
Pure mathematical/statistical detector for AI-generated text.
NO neural networks - only statistical analysis.
"""
import re
import math
from collections import Counter
from typing import Dict, List


class MathematicalDetector:
    """
    Statistical detector that analyzes text features without using neural networks.
    
    Implements:
    - Burstiness: Variance in sentence/word length
    - Vocabulary richness: Type-token ratio
    - Word frequency: Average word commonness
    - Punctuation patterns: Punctuation usage analysis
    - Sentence complexity: Syntactic complexity measures
    - Entropy: Word length distribution entropy
    """
    
    def __init__(self):
        """Initialize the mathematical detector."""
        # Load common English words (top 10000 most frequent)
        # Using a simplified frequency list for common words
        self.common_words = self._load_common_words()
    
    def _load_common_words(self) -> Dict[str, int]:
        """
        Load a basic frequency dictionary of common English words.
        Returns dict mapping word to frequency rank (lower = more common).
        """
        # Top 100 most common English words with frequency ranks
        common = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
            "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"
        ]
        return {word: i + 1 for i, word in enumerate(common)}
    
    def detect(self, sentence: str) -> dict:
        """
        Analyze a sentence and return AI detection score.
        
        Args:
            sentence: The sentence to analyze
            
        Returns:
            dict with 'score' (0=AI, 1=Human) and 'features' breakdown
        """
        if not sentence or len(sentence.strip()) == 0:
            return {
                'score': 0.5,
                'features': {
                    'burstiness': 0.5,
                    'vocabulary_richness': 0.5,
                    'word_frequency': 0.5,
                    'punctuation': 0.5,
                    'complexity': 0.5,
                    'entropy': 0.5
                }
            }
        
        # Calculate individual features
        burstiness = self._calculate_burstiness(sentence)
        vocab_richness = self._calculate_vocabulary_richness(sentence)
        word_freq = self._calculate_word_frequency(sentence)
        punctuation = self._calculate_punctuation_score(sentence)
        complexity = self._calculate_complexity(sentence)
        entropy = self._calculate_entropy(sentence)
        
        # Aggregate score (weighted average)
        # Human writing tends to have:
        # - Higher burstiness (more variation) - but formal writing may be consistent
        # - Higher vocabulary richness (more unique words)
        # - Mix of common and uncommon words
        # - Natural punctuation patterns
        # - Varied complexity - but formal writing may be structured
        # - Higher entropy
        # 
        # NOTE: Professional/formal writing scores lower on burstiness and complexity
        # but is still human - adjust weights accordingly
        raw_score = (
            burstiness * 0.10 +          # Reduced - formal writing is consistent
            vocab_richness * 0.25 +      # Increased - unique words matter more
            word_freq * 0.20 +           # Increased - word choice is important
            punctuation * 0.20 +         # Increased - punctuation patterns matter
            complexity * 0.10 +          # Reduced - formal writing is structured
            entropy * 0.15               # Keep same
        )
        
        # Gentle NEGATIVE bias (-0.03) to increase AI sensitivity while preserving human accuracy
        # -0.10 was too aggressive, -0.03 is more balanced
        score = max(raw_score - 0.03, 0.0)
        
        return {
            'score': round(score, 4),
            'features': {
                'burstiness': round(burstiness, 4),
                'vocabulary_richness': round(vocab_richness, 4),
                'word_frequency': round(word_freq, 4),
                'punctuation': round(punctuation, 4),
                'complexity': round(complexity, 4),
                'entropy': round(entropy, 4)
            }
        }
    
    def _calculate_burstiness(self, sentence: str) -> float:
        """
        Calculate burstiness score based on word length variance.
        Higher variance = more bursty = more human-like.
        
        Returns: Score from 0 to 1 (higher = more human)
        """
        words = self._tokenize_words(sentence)
        if len(words) < 2:
            return 0.5
        
        word_lengths = [len(word) for word in words]
        mean_length = sum(word_lengths) / len(word_lengths)
        
        # Calculate variance
        variance = sum((l - mean_length) ** 2 for l in word_lengths) / len(word_lengths)
        
        # Normalize: typical variance ranges from 0 to 20
        # Higher variance suggests more human-like burstiness
        normalized = min(variance / 20.0, 1.0)
        
        return normalized
    
    def _calculate_vocabulary_richness(self, sentence: str) -> float:
        """
        Calculate type-token ratio (unique words / total words).
        Higher ratio = richer vocabulary = more human-like.
        
        Returns: Score from 0 to 1 (higher = more human)
        """
        words = self._tokenize_words(sentence)
        if len(words) == 0:
            return 0.5
        
        unique_words = len(set(words))
        total_words = len(words)
        
        # Type-token ratio
        ttr = unique_words / total_words
        
        return ttr
    
    def _calculate_word_frequency(self, sentence: str) -> float:
        """
        Calculate average word frequency score.
        AI tends to use more common words. Balance is human-like.
        
        Returns: Score from 0 to 1 (higher = more human)
        """
        words = self._tokenize_words(sentence)
        if len(words) == 0:
            return 0.5
        
        scores = []
        for word in words:
            word_lower = word.lower()
            if word_lower in self.common_words:
                # Common word: rank closer to 1 means very common
                rank = self.common_words[word_lower]
                # Inverse score: very common = lower score
                scores.append(1.0 - (rank / 100.0))
            else:
                # Uncommon word: higher score
                scores.append(1.0)
        
        avg_score = sum(scores) / len(scores) if scores else 0.5
        
        # Balance: mid-range (0.4-0.6) is most human-like
        # Too many common words (low score) or too many rare words (high score) suggests AI
        balance_score = 1.0 - abs(avg_score - 0.5) * 2
        
        return balance_score
    
    def _calculate_punctuation_score(self, sentence: str) -> float:
        """
        Analyze punctuation patterns.
        Natural punctuation usage is more human-like.
        
        Returns: Score from 0 to 1 (higher = more human)
        """
        # Count different punctuation types
        punctuation_marks = re.findall(r'[.,!?;:\-—…]', sentence)
        total_chars = len(sentence)
        
        if total_chars == 0:
            return 0.5
        
        # Calculate punctuation density
        punct_density = len(punctuation_marks) / total_chars
        
        # Count punctuation variety
        unique_puncts = len(set(punctuation_marks))
        
        # Natural punctuation density is around 0.05-0.15
        # Too much or too little suggests AI
        optimal_density = 0.10
        density_score = 1.0 - min(abs(punct_density - optimal_density) / 0.10, 1.0)
        
        # Variety bonus: humans use diverse punctuation
        variety_score = min(unique_puncts / 3.0, 1.0)  # 3+ types is good
        
        # Combine scores
        score = (density_score * 0.7 + variety_score * 0.3)
        
        return score
    
    def _calculate_complexity(self, sentence: str) -> float:
        """
        Measure sentence complexity.
        Moderate complexity with variation is human-like.
        
        Returns: Score from 0 to 1 (higher = more human)
        """
        words = self._tokenize_words(sentence)
        if len(words) == 0:
            return 0.5
        
        # Average words per sentence (for this single sentence)
        words_per_sentence = len(words)
        
        # Count clauses (approximated by commas, conjunctions, and semicolons)
        clause_indicators = len(re.findall(r'[,;]|\band\b|\bbut\b|\bor\b|\bif\b|\bwhen\b', sentence.lower()))
        
        # Calculate complexity score
        # Optimal sentence length: 15-25 words
        length_score = 1.0 - min(abs(words_per_sentence - 20) / 20.0, 1.0)
        
        # Clause density
        clause_density = clause_indicators / max(words_per_sentence, 1)
        # Optimal clause density: 0.1-0.2
        clause_score = 1.0 - min(abs(clause_density - 0.15) / 0.15, 1.0)
        
        # Combine
        score = (length_score * 0.6 + clause_score * 0.4)
        
        return score
    
    def _calculate_entropy(self, sentence: str) -> float:
        """
        Calculate Shannon entropy of word length distribution.
        Higher entropy = more variation = more human-like.
        
        Returns: Score from 0 to 1 (higher = more human)
        """
        words = self._tokenize_words(sentence)
        if len(words) < 2:
            return 0.5
        
        # Get word length distribution
        word_lengths = [len(word) for word in words]
        length_counts = Counter(word_lengths)
        total = len(words)
        
        # Calculate Shannon entropy
        entropy = 0.0
        for count in length_counts.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Normalize: maximum entropy for reasonable distribution is ~3.5
        normalized_entropy = min(entropy / 3.5, 1.0)
        
        return normalized_entropy
    
    def _tokenize_words(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of words
        """
        # Remove punctuation and split
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) > 0]
