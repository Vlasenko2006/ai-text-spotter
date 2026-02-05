"""
Semantic Embedding Detector for AI-generated text.
Uses semantic embedding variability to detect AI vs Human text.

5-Zone Classification System:
- Zone 1 (High AI): STD > 0.036824, Accuracy: 86.75%
- Zone 2 (Likely AI): 0.035141 < STD ≤ 0.036824, Accuracy: 74.65%
- Zone 3 (Unclassified): 0.033005 ≤ STD ≤ 0.035141, No prediction
- Zone 4 (Likely Human): 0.030963 ≤ STD < 0.033005, Accuracy: 67.53%
- Zone 5 (High Human): STD < 0.030963, Accuracy: 94.86%

Overall accuracy: 81.35% (validation), 84.87% (training)
Joint AI accuracy (Zones 1+2): 83.18%
Joint Human accuracy (Zones 4+5): 80.00%

Trained on 300 Llama 3.1 8B + 300 Wikipedia articles.
"""
import logging
import re
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


# Hardcoded thresholds from training data (300 Llama 3.1 8B + 300 Wikipedia articles)
GLOBAL_MEAN_STD_AI = 0.036824      # Mean STD for AI texts
GLOBAL_MEAN_STD_HUMAN = 0.030963   # Mean STD for human texts
SIGMA_STD_AI = 0.003366             # Std deviation of AI STDs
SIGMA_STD_HUMAN = 0.004083          # Std deviation of human STDs

# 5-Zone Classification Boundaries
# Zone 3 (unclassified): mean ± 0.5*sigma
UNCLASSIFIED_LOWER = GLOBAL_MEAN_STD_HUMAN + (0.5 * SIGMA_STD_HUMAN)  # 0.033005
UNCLASSIFIED_UPPER = GLOBAL_MEAN_STD_AI - (0.5 * SIGMA_STD_AI)        # 0.035141

# Zone accuracies from validation (81.35% overall, 16% unclassified)
ZONE_1_ACCURACY = 0.8675  # High AI (> 0.036824)
ZONE_2_ACCURACY = 0.7465  # Likely AI (0.035141 - 0.036824)
ZONE_4_ACCURACY = 0.6753  # Likely Human (0.030963 - 0.033005)
ZONE_5_ACCURACY = 0.9486  # High Human (< 0.030963)


class SemanticEmbeddingDetector:
    """
    Semantic embedding-based AI text detector.
    
    Analyzes semantic embedding variability across document chunks.
    AI texts tend to have higher embedding standard deviation than human texts.
    """
    
    def __init__(self):
        """Initialize the semantic embedding detector."""
        self.model = None
        self._loaded = False
    
    def load(self):
        """Load the sentence transformer model."""
        if self._loaded:
            return
        
        try:
            logger.info("Loading semantic embedding model: all-MiniLM-L6-v2")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self._loaded = True
            logger.info("Semantic embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load semantic embedding model: {e}")
            raise
    
    def split_into_sentences(self, text):
        """Split text into sentences using regex."""
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
        sentences = re.split(sentence_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def sentence_aware_chunk_encode(self, text, num_chunks=50):
        """
        Split text into chunks that respect sentence boundaries.
        Returns embeddings for each chunk.
        """
        if not self._loaded:
            self.load()
        
        sentences = self.split_into_sentences(text)
        
        if len(sentences) < num_chunks:
            # Fewer sentences than chunks - encode each sentence separately
            chunk_embeddings = self.model.encode(sentences, show_progress_bar=False)
            # DO NOT PAD - return actual embeddings to avoid zero-dilution
            return chunk_embeddings
        
        # Calculate target sentences per chunk
        sentences_per_chunk = len(sentences) / num_chunks
        
        chunks = []
        current_chunk = []
        sentence_count = 0
        
        for i, sentence in enumerate(sentences):
            current_chunk.append(sentence)
            sentence_count += 1
            
            # Check if we should close this chunk
            expected_sentences = (len(chunks) + 1) * sentences_per_chunk
            
            if sentence_count >= expected_sentences or i == len(sentences) - 1:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                sentence_count = 0
        
        # Encode all chunks
        chunk_embeddings = self.model.encode(chunks, show_progress_bar=False)
        
        return chunk_embeddings
    
    def compute_embedding_std(self, text, num_chunks=50):
        """
        Compute standard deviation of embeddings across document chunks.
        
        Args:
            text: Input text string
            num_chunks: Number of chunks to split document into
            
        Returns:
            float: Standard deviation across embedding dimensions
        """
        if not self._loaded:
            self.load()
        
        # Get chunk embeddings
        chunk_embeddings = self.sentence_aware_chunk_encode(text, num_chunks=num_chunks)
        
        # Compute mean embedding across chunks
        mean_embedding = np.mean(chunk_embeddings, axis=0)
        
        # Compute standard deviation across 384 dimensions
        embedding_std = np.std(mean_embedding)
        
        return embedding_std
    
    def detect(self, text: str) -> dict:
        """
        Detect if text is AI-generated based on semantic embedding variability.
        Uses 5-zone classification system with validated accuracies.
        
        Args:
            text: The text to analyze (full document or sentence)
            
        Returns:
            dict with 'score' (0=AI, 1=Human), 'confidence', 'std', 'classification', 'zone'
        """
        if not text or len(text.strip()) == 0:
            return {
                'score': 0.5,
                'confidence': 0.0,
                'std': 0.0,
                'classification': 'unknown',
                'zone': 0
            }
        
        try:
            # Compute embedding standard deviation
            std = self.compute_embedding_std(text)
            
            # 5-Zone Classification
            if std > GLOBAL_MEAN_STD_AI:
                # Zone 1: High AI
                zone = 1
                classification = "ai"
                confidence = ZONE_1_ACCURACY
                score = 0.02  # Very low score = AI
                
            elif UNCLASSIFIED_UPPER < std <= GLOBAL_MEAN_STD_AI:
                # Zone 2: Likely AI
                zone = 2
                classification = "likely-ai"
                confidence = ZONE_2_ACCURACY
                score = 0.25  # Low score = AI
                
            elif UNCLASSIFIED_LOWER <= std <= UNCLASSIFIED_UPPER:
                # Zone 3: Unclassified (overlap zone)
                zone = 3
                classification = "mixed"
                confidence = 0.50
                score = 0.50  # Neutral
                
            elif GLOBAL_MEAN_STD_HUMAN <= std < UNCLASSIFIED_LOWER:
                # Zone 4: Likely Human
                zone = 4
                classification = "likely-human"
                confidence = ZONE_4_ACCURACY
                score = 0.75  # High score = Human
                
            else:  # std < GLOBAL_MEAN_STD_HUMAN
                # Zone 5: High Human
                zone = 5
                classification = "human"
                confidence = ZONE_5_ACCURACY
                score = 0.98  # Very high score = Human
            
            logger.info(f"Semantic detection - STD: {std:.6f}, Zone: {zone}, Classification: {classification}, Confidence: {confidence:.2%}")
            
            return {
                'score': round(score, 4),
                'confidence': round(confidence, 4),
                'std': round(std, 6),
                'classification': classification,
                'zone': zone,
                'thresholds': {
                    'human_mean': GLOBAL_MEAN_STD_HUMAN,
                    'ai_mean': GLOBAL_MEAN_STD_AI,
                    'unclassified_lower': UNCLASSIFIED_LOWER,
                    'unclassified_upper': UNCLASSIFIED_UPPER
                }
            }
            
        except Exception as e:
            logger.error(f"Error during semantic embedding detection: {e}")
            return {
                'score': 0.5,
                'confidence': 0.0,
                'std': 0.0,
                'classification': 'error',
                'zone': 0
            }
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._loaded
    
    def unload(self):
        """Unload the model to free memory."""
        if self._loaded:
            self.model = None
            self._loaded = False
            logger.info("Semantic embedding model unloaded")
