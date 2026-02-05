#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 13:14:43 2026

@author: andreyvlasenko
"""

import matplotlib.pyplot as plt
import numpy as np
from os.path import join



def moving_average(data, window_size=10, compute_singe_mean = True):
    """Calculate moving average using convolution"""
    if compute_singe_mean:
        return np.zeros_like(data) + np.mean(data)
    else:
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid')



def plotting_2_mean(embeddings_0,embeddings_1, label0='AI', label1 = "Human", mean_ai = True,mean_human = True):
    plt.figure(figsize=(12, 6))
    # Use the same bins for both histograms to ensure proper overlap
    bins = np.linspace(-0.08, 0.10, 91)
    if mean_ai:
        plt.hist(np.mean(embeddings_0, axis=0), bins=bins, alpha=0.6, label=label0, color='red', edgecolor='darkred', linewidth=0.5)
    else:
        plt.hist(embeddings_0, bins=bins, alpha=0.6, label=label0, color='red', edgecolor='darkred', linewidth=0.5)
        
        
        
    if mean_human:
        plt.hist( np.mean(embeddings_1, axis=0), bins=bins, alpha=0.6, label=label1, color='blue', edgecolor='darkblue', linewidth=0.5)
    else:
        plt.hist(embeddings_1, bins=bins, alpha=0.6, label=label1, color='blue', edgecolor='darkred', linewidth=0.5)
    
    plt.xlabel('Mean Embedding Value', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of Mean Embeddings: AI vs Human', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', fontsize=11)
    plt.grid(alpha=0.3)
    # Add vertical line at zero
    plt.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5, label='Zero')
    plt.tight_layout()
    #plt.savefig('embeddings_mean_distribution.png', dpi=150)
    plt.show()




def std_plot(data_ai, data_h, num_chunks, sigma_ai, sigma_h, ma_ai, ma_h, window=10,
             xlabel='Articles',
             ylabel='STD',
             title='Distribution of STD Embeddings: AI vs Human (MA ± σ)', 
             filename='Distribution of STD Embeddings: AI vs Human'):
    """Plot standard deviation or mean values with moving average and confidence bands.
    
    Args:
        data_ai: Raw AI data values (300 articles)
        data_h: Raw human data values (300 articles)
        num_chunks: Number of chunks used in embedding generation
        sigma_ai: Standard deviation for AI (constant array for shading)
        sigma_h: Standard deviation for human (constant array for shading)
        ma_ai: Moving average of AI data
        ma_h: Moving average of human data
        window: Moving average window size
    """
    # Create x-axis
    print(f"data AI shape = {data_ai.shape}")
    x_original = np.arange(len(data_ai))
    x_ma = np.arange(window//2, window//2 + len(ma_ai))
    plt.figure(figsize=(12, 6))

    # Original data (very light)
    plt.plot(x_original, data_ai, alpha=0.92, linewidth=0.8, color='red')
    plt.plot(x_original, data_h, alpha=0.92, linewidth=0.8, color='blue')

    # Moving averages (bold)
    plt.plot(x_ma, ma_ai, linewidth=2.5, color='darkred', label=f'AI (MA-{window})')
    plt.plot(x_ma, ma_h, linewidth=2.5, color='darkblue', label=f'Human (MA-{window})')

    # Shaded confidence bands (±1σ)
    plt.fill_between(x_ma, ma_ai - sigma_ai, ma_ai + sigma_ai, 
                     color='red', alpha=0.15, label='AI (±1σ)')
    plt.fill_between(x_ma, ma_h - sigma_h, ma_h + sigma_h, 
                     color='blue', alpha=0.15, label='Human (±1σ)')

    # Dotted boundary lines
    plt.plot(x_ma, ma_ai + sigma_ai, linewidth=1, color='darkred', 
             linestyle=':', alpha=0.6)
    plt.plot(x_ma, ma_ai - sigma_ai, linewidth=1, color='darkred', 
             linestyle=':', alpha=0.6)
    plt.plot(x_ma, ma_h + sigma_h, linewidth=1, color='darkblue', 
             linestyle=':', alpha=0.6)
    plt.plot(x_ma, ma_h - sigma_h, linewidth=1, color='darkblue', 
             linestyle=':', alpha=0.6)

    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, 
              fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename + f'{num_chunks}.png', dpi=150, bbox_inches='tight')
    plt.show()




def compute_stats(embeddings_ai_sentence, embeddings_h_sentence, window_size=10):
    """Compute statistical metrics for embeddings.
    
    For each document, computes:
    - Standard deviation across all embedding dimensions
    - Mean across all embedding dimensions
    
    Then computes global statistics and moving averages.
    
    Args:
        embeddings_ai_sentence: AI embeddings (num_docs x embedding_dim)
        embeddings_h_sentence: Human embeddings (num_docs x embedding_dim)
        window_size: Window size for moving average
    
    Returns:
        Tuple of statistical arrays for plotting
    """
    num_docs = min(embeddings_ai_sentence.shape[0],embeddings_h_sentence.shape[0])
    
    # Compute per-document statistics
    std_ai = []
    std_h = []
    mean_ai = []
    mean_h = []

    for doc_id in range(num_docs):
        # Standard deviation across embedding dimensions for this document
        std_ai.append(np.std(embeddings_ai_sentence[doc_id, :]))
        std_h.append(np.std(embeddings_h_sentence[doc_id, :]))
        
        # Mean across embedding dimensions for this document
        mean_ai.append(np.mean(embeddings_ai_sentence[doc_id, :]))
        mean_h.append(np.mean(embeddings_h_sentence[doc_id, :]))
        
    std_ai = np.array(std_ai)
    std_h = np.array(std_h)
    mean_ai = np.array(mean_ai)
    mean_h = np.array(mean_h)

    # Calculate moving averages
    ma_std_ai = moving_average(std_ai, window_size)
    ma_std_h = moving_average(std_h, window_size)
    ma_mean_ai = moving_average(mean_ai, window_size)
    ma_mean_h = moving_average(mean_h, window_size)

    # Compute global statistics
    # Global mean of standard deviations across all documents
    global_mean_std_h = np.mean(std_h)
    global_mean_std_ai = np.mean(std_ai)

    # Global std of standard deviations (variability in STD across documents)
    global_std_of_std_h = np.std(std_h)
    global_std_of_std_ai = np.std(std_ai)

    # Global std of means (variability in means across documents)
    global_std_of_mean_h = np.std(mean_h)
    global_std_of_mean_ai = np.std(mean_ai)

    # Create constant arrays for shading (sigma bands)
    sigma_std_ai_array = np.zeros_like(ma_std_ai) + global_std_of_std_ai
    sigma_std_h_array = np.zeros_like(ma_std_h) + global_std_of_std_h
    sigma_mean_ai_array = np.zeros_like(ma_mean_ai) + global_std_of_mean_ai
    sigma_mean_h_array = np.zeros_like(ma_mean_h) + global_std_of_mean_h
    
    return (std_ai, std_h, sigma_std_ai_array, sigma_std_h_array, 
            ma_std_ai, ma_std_h, mean_ai, mean_h, 
            sigma_mean_ai_array, sigma_mean_h_array, 
            ma_mean_ai, ma_mean_h, 
            global_mean_std_h, global_mean_std_ai, window_size) 






print(f"{'='*10} Starting Analysis {'='*10}")

# Configuration
NUM_DOCS = 300
NUM_CHUNKS = 50
WINDOW_SIZE = 10
EMBEDDINGS_PATH = 'embeddings/'

# Load embeddings
embeddings_ai_sentence = np.load(join(EMBEDDINGS_PATH, f'embeddings_ai_sentence_{NUM_CHUNKS}.npy'))
embeddings_h_sentence = np.load(join(EMBEDDINGS_PATH, f'embeddings_h_sentence_{NUM_CHUNKS}.npy'))

# Load embeddings
embeddings_ai_sentence_val = np.load(join(EMBEDDINGS_PATH, f'embeddings_ai_sentence_{NUM_CHUNKS}_val.npy'))
embeddings_h_sentence_val = np.load(join(EMBEDDINGS_PATH, f'embeddings_h_sentence_{NUM_CHUNKS}_val.npy'))

embeddings_52_sentence_val = np.load(join(EMBEDDINGS_PATH, f'embeddings_ai_sentence_{NUM_CHUNKS}_gpt.npy'))





print(f"\nAI embeddings shape: {embeddings_ai_sentence.shape}")
print(f"Human embeddings shape: {embeddings_h_sentence.shape}")
    

# Compute statistics
(std_ai_52, std_h_52, sigma_std_ai_array_52, sigma_std_h_array_52,
 ma_std_ai_52, ma_std_h_52, mean_ai_52, mean_h_52,
 sigma_mean_ai_array_52, sigma_mean_h_array_52,
 ma_mean_ai_52, ma_mean_h_52,
 global_mean_std_h_52, global_mean_std_ai_52, window_size_52) = compute_stats(
    embeddings_52_sentence_val, embeddings_h_sentence[:40,:], window_size=WINDOW_SIZE)


# Compute statistics
(std_ai, std_h, sigma_std_ai_array, sigma_std_h_array,
 ma_std_ai, ma_std_h, mean_ai, mean_h,
 sigma_mean_ai_array, sigma_mean_h_array,
 ma_mean_ai, ma_mean_h,
 global_mean_std_h, global_mean_std_ai, window_size) = compute_stats(
    embeddings_ai_sentence, embeddings_h_sentence, window_size=WINDOW_SIZE)
     
     
     
     
# Compute statistics
(std_ai_val, std_h_val, sigma_std_ai_array_val, sigma_std_h_array_val,
 ma_std_ai_val, ma_std_h_val, mean_ai_val, mean_h_val,
 sigma_mean_ai_array_val, sigma_mean_h_array_val,
 ma_mean_ai_val, ma_mean_h_val,
 global_mean_std_h_val, global_mean_std_ai_val, window_size) = compute_stats(
    embeddings_ai_sentence_val, embeddings_h_sentence_val, window_size=WINDOW_SIZE)
     
     
     
     

print(f"\nGlobal Statistics:")
print(f"  AI - Mean STD: {global_mean_std_ai:.6f}, STD of STD: {sigma_std_ai_array[0]:.6f}")
print(f"  Human - Mean STD: {global_mean_std_h:.6f}, STD of STD: {sigma_std_h_array[0]:.6f}")

# Plot 1: Standard Deviation Distribution
std_plot(std_ai, std_h, NUM_CHUNKS, sigma_std_ai_array, sigma_std_h_array, 
         ma_std_ai, ma_std_h, window=window_size,
         xlabel='Articles',
         ylabel='STD',
         title='Distribution of STD Embeddings: AI vs Human (MA ± σ)', 
         filename='distribution_std_embeddings_ai_vs_human_chunks_')


# Plot 1: Standard Deviation Distribution
std_plot(std_ai_val, std_h_val, NUM_CHUNKS, sigma_std_ai_array_val, sigma_std_h_array_val, 
         ma_std_ai_val, ma_std_h_val, window=window_size,
         xlabel='Articles',
         ylabel='STD',
         title='Distribution of STD Embeddings: AI vs Human (MA ± σ)', 
         filename='distribution_std_embeddings_ai_vs_human_chunks_')

# # Plot 2: Mean Distribution
# std_plot(mean_ai_val, mean_h_val, NUM_CHUNKS, sigma_mean_ai_array_val, sigma_mean_h_array_val,
#          ma_mean_ai_val, ma_mean_h_val, window=window_size,
#          xlabel='Validation Articles',
#          ylabel='Mean',
#          title='Distribution of Mean Embeddings, Validation Set: AI vs Human (MA ± σ)', 
#          filename='distribution_mean_embeddings_ai_vs_human_chunks_val')




# Statistical Analysis
print(f"\nStatistical Analysis:")

# Count documents with unusual STD values
num_human_above_threshold = (std_h > (global_mean_std_h + sigma_std_h_array[0])).sum()
num_ai_below_threshold = (std_ai < (global_mean_std_h + sigma_std_h_array[0])).sum()

# Identify human articles with STD above AI mean
human_above_ai_mean = std_h > global_mean_std_ai
human_above_ai_mean_ids = np.where(human_above_ai_mean)[0]

# Print human articles with STD above global AI mean
print(f"\n{'='*60}")
print(f"Human articles with STD > global_mean_std_ai ({global_mean_std_ai:.6f}):")
print(f"{'='*60}")
if len(human_above_ai_mean_ids) > 0:
    # Load human articles to get character counts
    from os import listdir
    human_files = sorted([f for f in listdir('wiki_articles') if f.endswith('.txt')])
    
    print(f"Found {len(human_above_ai_mean_ids)} articles:")
    short_articles_count = 0
    for idx in human_above_ai_mean_ids:
        # Read the article to get character count
        article_path = join('wiki_articles', human_files[idx])
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
        char_count = len(content)
        if char_count < 3000:
            short_articles_count += 1
        print(f"  ID: {idx:3d} | STD: {std_h[idx]:.6f} | Characters: {char_count:5d} | File: {human_files[idx]}")
    
    # Count total articles with less than 3000 characters across all articles
    total_short_articles = 0
    for idx in range(len(human_files)):
        article_path = join('wiki_articles', human_files[idx])
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if len(content) < 3000:
            total_short_articles += 1
    
    print(f"\n  Articles with <3000 chars (among high-STD): {short_articles_count}/{len(human_above_ai_mean_ids)} ({100*short_articles_count/len(human_above_ai_mean_ids):.1f}%)")
    print(f"  Total articles with <3000 chars (all dataset): {total_short_articles}/{NUM_DOCS} ({100*total_short_articles/NUM_DOCS:.1f}%)")
else:
    print("  No human articles exceed the AI mean STD threshold")
print(f"{'='*60}\n")

# Probability metric: 1 - (outliers / total_docs)
prob_metric = 1 - (num_human_above_threshold + num_ai_below_threshold) / NUM_DOCS

# Probability human text has STD > AI mean STD
prob_human_above_ai_mean = 1 - (std_h_val > global_mean_std_ai).sum() / NUM_DOCS

# Probability AI text has STD < human mean STD  
prob_ai_below_human_mean = 1 - (std_ai_val < global_mean_std_h).sum() / NUM_DOCS

print(f"  Combined probability metric: {prob_metric:.4f}")
print(f"  P(Human STD > AI mean STD): {prob_human_above_ai_mean:.4f}")
print(f"  P(AI STD < Human mean STD): {prob_ai_below_human_mean:.4f}")
print(f"\nKey Finding: AI texts have {'lower' if global_mean_std_ai < global_mean_std_h else 'higher'} embedding variability")
print(f"  → AI is more {'consistent/repetitive' if global_mean_std_ai < global_mean_std_h else 'varied'}")

#def probability_score(embedding, std_ai, std_h)
