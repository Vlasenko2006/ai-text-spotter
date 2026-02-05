#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Text Classifier
Classifies text as AI-generated or human-written based on semantic embedding variability.

@author: andreyvlasenko
Created: Feb 3, 2026
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import re


# Hardcoded thresholds from training data (300 Llama 3.1 8B + 300 Wikipedia articles)
GLOBAL_MEAN_STD_AI = 0.036824      # Mean STD for AI texts
GLOBAL_MEAN_STD_HUMAN = 0.030963   # Mean STD for human texts
SIGMA_STD_AI = 0.003366             # Std deviation of AI STDs
SIGMA_STD_HUMAN = 0.004083          # Std deviation of human STDs

# Load model once at module level
_model = None


def get_model():
    """Lazy load the sentence transformer model"""
    global _model
    if _model is None:
        print("Loading sentence transformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def split_into_sentences(text):
    """
    Split text into sentences using regex.
    Handles common punctuation: . ! ?
    """
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
    sentences = re.split(sentence_pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def sentence_aware_chunk_encode(text, model, num_chunks=50):
    """
    Split text into chunks that respect sentence boundaries.
    Returns embeddings for each chunk (not averaged).
    
    Args:
        text: Input text string
        model: SentenceTransformer model
        num_chunks: Target number of chunks
        
    Returns:
        numpy array of shape (num_chunks, 384) with chunk embeddings
    """
    sentences = split_into_sentences(text)
    
    if len(sentences) < num_chunks:
        # Fewer sentences than chunks - encode each sentence separately
        chunk_embeddings = model.encode(sentences, show_progress_bar=False)
        # Pad with zeros if needed
        if len(sentences) < num_chunks:
            padding = np.zeros((num_chunks - len(sentences), chunk_embeddings.shape[1]))
            chunk_embeddings = np.vstack([chunk_embeddings, padding])
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
    chunk_embeddings = model.encode(chunks, show_progress_bar=False)
    
    return chunk_embeddings


def compute_embedding_std(text, model=None, num_chunks=50):
    """
    Compute standard deviation of embeddings across document chunks.
    
    Args:
        text: Input text string
        model: SentenceTransformer model (optional, will load if None)
        num_chunks: Number of chunks to split document into
        
    Returns:
        float: Standard deviation across embedding dimensions
    """
    if model is None:
        model = get_model()
    
    # Get chunk embeddings
    chunk_embeddings = sentence_aware_chunk_encode(text, model, num_chunks=num_chunks)
    
    # Compute mean embedding across chunks
    mean_embedding = np.mean(chunk_embeddings, axis=0)
    
    # Compute standard deviation across 384 dimensions
    embedding_std = np.std(mean_embedding)
    
    return embedding_std


def classify_text(text, model=None, num_chunks=50, return_details=False):
    """
    Classify text as AI-generated or human-written based on embedding variability.
    
    Classification rules:
    - std > global_mean_std_ai: 98% AI
    - std < global_mean_std_h: 96% Human
    - std in [global_mean_std_h, global_mean_std_ai - sigma_std_ai]: 60% Human
    - std in [global_mean_std_h + sigma_std_h, global_mean_std_ai]: 60% AI
    - Otherwise: Uncertain (50/50)
    
    Args:
        text: Input text string to classify
        model: SentenceTransformer model (optional)
        num_chunks: Number of chunks for processing
        return_details: If True, return dict with full details
        
    Returns:
        If return_details=False: tuple (classification, confidence)
            - classification: "AI" or "Human"
            - confidence: float between 0 and 1
        If return_details=True: dict with classification, confidence, std, and thresholds
    """
    if model is None:
        model = get_model()
    
    # Compute embedding standard deviation
    std = compute_embedding_std(text, model, num_chunks)
    
    # Define decision boundaries
    lower_uncertain = GLOBAL_MEAN_STD_HUMAN
    upper_uncertain = GLOBAL_MEAN_STD_AI
    human_boundary_upper = GLOBAL_MEAN_STD_AI - SIGMA_STD_AI
    ai_boundary_lower = GLOBAL_MEAN_STD_HUMAN + SIGMA_STD_HUMAN
    
    # Classification logic
    if std > upper_uncertain:
        classification = "AI"
        confidence = 0.98
    elif std < lower_uncertain:
        classification = "Human"
        confidence = 0.96
    elif lower_uncertain <= std < human_boundary_upper:
        classification = "Human"
        confidence = 0.60
    elif ai_boundary_lower <= std <= upper_uncertain:
        classification = "AI"
        confidence = 0.60
    else:
        # In the overlap zone [global_mean_std_ai - sigma_std_ai, global_mean_std_h + sigma_std_h]
        # Equal probability of being AI or Human
        classification = "Uncertain (50% AI / 50% Human)"
        confidence = 0.50
    
    if return_details:
        return {
            'classification': classification,
            'confidence': confidence,
            'std': std,
            'thresholds': {
                'human_mean': GLOBAL_MEAN_STD_HUMAN,
                'ai_mean': GLOBAL_MEAN_STD_AI,
                'human_boundary_upper': human_boundary_upper,
                'ai_boundary_lower': ai_boundary_lower
            },
            'char_count': len(text)
        }
    else:
        return classification, confidence


def classify_file(filepath, model=None, num_chunks=50, return_details=False):
    """
    Classify text from a file.
    
    Args:
        filepath: Path to text file
        model: SentenceTransformer model (optional)
        num_chunks: Number of chunks for processing
        return_details: If True, return dict with full details
        
    Returns:
        Same as classify_text()
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    return classify_text(text, model, num_chunks, return_details)


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ai_text_classifier.py <text_file>")
        print("\nExample:")
        print("  python ai_text_classifier.py wiki_articles/wiki_001.txt")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    print(f"Classifying: {filepath}")
    print("=" * 60)
    
    result = classify_file(filepath, return_details=True)
    
    print(f"\nClassification: {result['classification']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Embedding STD: {result['std']:.6f}")
    print(f"Character count: {result['char_count']}")
    print(f"\nThresholds:")
    print(f"  Human mean: {result['thresholds']['human_mean']:.6f}")
    print(f"  AI mean: {result['thresholds']['ai_mean']:.6f}")
    print(f"  Human boundary (upper): {result['thresholds']['human_boundary_upper']:.6f}")
    print(f"  AI boundary (lower): {result['thresholds']['ai_boundary_lower']:.6f}")


if __name__ == "__main__":
    main()
