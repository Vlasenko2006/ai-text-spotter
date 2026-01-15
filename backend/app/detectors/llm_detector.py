"""
LLM-based detector using DistilBERT model for AI text detection.
Uses HuggingFace transformers library with a pre-trained model.
"""
import logging
from typing import Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.config import settings

logger = logging.getLogger(__name__)


class LLMDetector:
    """
    DistilBERT-based AI text detector.
    
    Uses a pre-trained model from HuggingFace for detecting AI-generated text.
    Optimized for low memory usage (suitable for AWS t3.micro).
    """
    
    def __init__(self):
        """Initialize the LLM detector."""
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._loaded = False
    
    def load(self):
        """
        Load the model and tokenizer.
        This is done lazily to save memory until first use.
        """
        if self._loaded:
            return
        
        try:
            logger.info(f"Loading LLM detector model: {settings.llm_detector_model}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.llm_detector_model,
                cache_dir=settings.model_cache_dir
            )
            
            # Load model
            self.model = AutoModelForSequenceClassification.from_pretrained(
                settings.llm_detector_model,
                cache_dir=settings.model_cache_dir
            )
            
            # Move to device
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            self._loaded = True
            logger.info("LLM detector model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load LLM detector model: {e}")
            raise
    
    def detect(self, sentence: str) -> dict:
        """
        Detect if a sentence is AI-generated using the LLM model.
        
        Args:
            sentence: The sentence to analyze
            
        Returns:
            dict with 'score' (0=AI, 1=Human) and 'confidence'
        """
        # Ensure model is loaded
        if not self._loaded:
            self.load()
        
        if not sentence or len(sentence.strip()) == 0:
            return {
                'score': 0.5,
                'confidence': 0.0
            }
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                sentence,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # Get probabilities
            probs = torch.softmax(logits, dim=-1)
            
            # Model outputs: [AI probability, Human probability]
            # We want score where 0=AI, 1=Human
            ai_prob = probs[0][0].item()
            human_prob = probs[0][1].item()
            
            # Score: human probability (0=AI, 1=Human)
            score = human_prob
            
            # Confidence: max probability
            confidence = max(ai_prob, human_prob)
            
            return {
                'score': round(score, 4),
                'confidence': round(confidence, 4)
            }
            
        except Exception as e:
            logger.error(f"Error during LLM detection: {e}")
            # Return neutral score on error
            return {
                'score': 0.5,
                'confidence': 0.0
            }
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._loaded
    
    def unload(self):
        """Unload the model to free memory."""
        if self._loaded:
            self.model = None
            self.tokenizer = None
            self._loaded = False
            
            # Clear CUDA cache if using GPU
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            logger.info("LLM detector model unloaded")
