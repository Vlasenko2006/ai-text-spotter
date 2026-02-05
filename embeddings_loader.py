#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 13:14:43 2026

@author: andreyvlasenko
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm
import re
from load_dataset import DatasetLoader
from os.path import join




def split_into_sentences(text):
    """
    Split text into sentences using regex.
    Handles common punctuation: . ! ?
    """
    # Pattern: sentence ends with .!? followed by space and capital letter or end of string
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
    sentences = re.split(sentence_pattern, text)
    
    # Clean up empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences

def sentence_aware_chunk_encode(text, model, num_chunks=10):
    """
    Split text into chunks that respect sentence boundaries.
    Each chunk ends at a complete sentence.
    """
    # Split into sentences
    sentences = split_into_sentences(text)
    
    if len(sentences) < num_chunks:
        # Fewer sentences than chunks - encode each sentence separately
        chunk_embeddings = model.encode(sentences, show_progress_bar=False)
        return np.mean(chunk_embeddings, axis=0)
    
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
            # Combine sentences into chunk
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            sentence_count = 0
    
    # Encode all chunks
    chunk_embeddings = model.encode(chunks, show_progress_bar=False)
    
    return np.mean(chunk_embeddings, axis=0)





# Load the dataset
loader = DatasetLoader(wiki_folder="validation_wiki_articles", ai_folder="validation_gpt_52")
wiki_list, ai_list = loader.load_all()
#wiki_list = [text[:3000] for text in wiki_list]
n_articles = 40
num_chunks = 50
num_of_plots = 2

print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')    

print("Generating embeddings for AI texts...")
embeddings_ai = model.encode(ai_list)

print("Generating embeddings for Wikipedia texts...")
embeddings_h = model.encode(wiki_list)



# Main processing
embeddings_ai_sentence = []
embeddings_h_sentence = []

print("Processing documents with sentence-aware chunking...")
for ai_text, wiki_text in tqdm(zip(ai_list, wiki_list), total=len(ai_list)):
    embeddings_ai_sentence.append(sentence_aware_chunk_encode(ai_text, model, num_chunks=num_chunks))
    embeddings_h_sentence.append(sentence_aware_chunk_encode(wiki_text, model, num_chunks=num_chunks))

# Convert to arrays
embeddings_ai_sentence = np.array(embeddings_ai_sentence)
embeddings_h_sentence = np.array(embeddings_h_sentence)


np.save(join('embeddings/',f'embeddings_ai_sentence_{num_chunks}_gpt'),embeddings_ai_sentence)
#np.save(join('embeddings/',f'embeddings_h_sentence_{num_chunks}_val'),embeddings_h_sentence)

print(f"\nAI embeddings shape: {embeddings_ai_sentence.shape}")
print(f"Human embeddings shape: {embeddings_h_sentence.shape}")
    
