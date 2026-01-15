"""
Jury detector using Groq Llama 3.1 8B as final arbitrator.
Makes final classification decisions based on other detector outputs.
"""
import json
import logging
from typing import Dict, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class JuryDetector:
    """
    Jury detector that uses Groq Llama 3.1 8B to make final classification decisions.
    
    Receives input from mathematical and LLM detectors and makes a final judgment.
    """
    
    def __init__(self):
        """Initialize the jury detector."""
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self._available = bool(self.api_key)
    
    def decide(
        self,
        sentence: str,
        context: Dict[str, Optional[str]],
        math_result: dict,
        llm_result: dict
    ) -> dict:
        """
        Make final classification decision using Groq Llama.
        
        Args:
            sentence: The sentence to classify
            context: Dict with 'before' and 'after' context sentences
            math_result: Results from mathematical detector
            llm_result: Results from LLM detector
            
        Returns:
            dict with 'classification' (human/suspicious/ai), 'confidence', 'reasoning'
        """
        if not self._available:
            # Fallback to simple voting if API key not available
            return self._fallback_decision(math_result, llm_result)
        
        try:
            # Build the prompt
            prompt = self._build_prompt(sentence, context, math_result, llm_result)
            
            # Call Groq API
            response = self._call_groq_api(prompt)
            
            # Parse response
            result = self._parse_response(response)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in jury decision: {e}")
            # Fallback to simple voting
            return self._fallback_decision(math_result, llm_result)
    
    def _build_prompt(
        self,
        sentence: str,
        context: Dict[str, Optional[str]],
        math_result: dict,
        llm_result: dict
    ) -> str:
        """Build the prompt for Groq API."""
        before = context.get('before', '')
        after = context.get('after', '')
        
        math_score = math_result.get('score', 0.5)
        math_features = math_result.get('features', {})
        llm_score = llm_result.get('score', 0.5)
        llm_confidence = llm_result.get('confidence', 0.0)
        
        prompt = f"""You are an AI text detection arbitrator. Analyze this sentence from a cover letter.

Sentence: "{sentence}"
Context Before: "{before}"
Context After: "{after}"

Detector Results:
- Statistical Analysis: {math_score:.3f} (0=AI, 1=Human)
  Features: burstiness={math_features.get('burstiness', 0):.3f}, vocabulary_richness={math_features.get('vocabulary_richness', 0):.3f}, word_frequency={math_features.get('word_frequency', 0):.3f}, punctuation={math_features.get('punctuation', 0):.3f}, complexity={math_features.get('complexity', 0):.3f}, entropy={math_features.get('entropy', 0):.3f}
- Language Model Analysis: {llm_score:.3f} (0=AI, 1=Human, confidence: {llm_confidence:.3f})

Classify this sentence as: human, suspicious, or ai

Guidelines:
- "human": Both detectors lean towards human (scores > 0.6)
- "suspicious": Mixed signals or borderline scores (0.4-0.6)
- "ai": Both detectors lean towards AI (scores < 0.4)
- Consider context and feature details in your reasoning

Respond ONLY with JSON in this exact format:
{{"classification": "human|suspicious|ai", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""
        
        return prompt
    
    def _call_groq_api(self, prompt: str) -> str:
        """Call Groq API with the prompt."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Low temperature for consistent results
            "max_tokens": 200
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return content
    
    def _parse_response(self, response: str) -> dict:
        """Parse the JSON response from Groq API."""
        try:
            # Extract JSON from response (might have markdown code blocks)
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            data = json.loads(response)
            
            classification = data.get('classification', 'suspicious').lower()
            confidence = float(data.get('confidence', 0.5))
            reasoning = data.get('reasoning', 'No reasoning provided')
            
            # Validate classification
            if classification not in ['human', 'suspicious', 'ai']:
                classification = 'suspicious'
            
            # Validate confidence
            confidence = max(0.0, min(1.0, confidence))
            
            return {
                'classification': classification,
                'confidence': round(confidence, 4),
                'reasoning': reasoning
            }
            
        except Exception as e:
            logger.error(f"Error parsing Groq response: {e}")
            logger.debug(f"Response was: {response}")
            return {
                'classification': 'suspicious',
                'confidence': 0.5,
                'reasoning': 'Failed to parse response'
            }
    
    def _fallback_decision(self, math_result: dict, llm_result: dict) -> dict:
        """
        Fallback decision logic when Groq API is not available.
        Uses simple voting based on detector scores.
        """
        math_score = math_result.get('score', 0.5)
        llm_score = llm_result.get('score', 0.5)
        
        # Average the scores
        avg_score = (math_score + llm_score) / 2
        
        # Classify based on thresholds
        if avg_score > 0.6:
            classification = 'human'
            confidence = avg_score
            reasoning = 'Both detectors indicate human writing'
        elif avg_score < 0.4:
            classification = 'ai'
            confidence = 1.0 - avg_score
            reasoning = 'Both detectors indicate AI-generated text'
        else:
            classification = 'suspicious'
            confidence = 0.5
            reasoning = 'Mixed signals from detectors'
        
        return {
            'classification': classification,
            'confidence': round(confidence, 4),
            'reasoning': reasoning
        }
    
    def is_available(self) -> bool:
        """Check if the jury detector is available (API key configured)."""
        return self._available
