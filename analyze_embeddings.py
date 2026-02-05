#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 13:14:43 2026

@author: andreyvlasenko
"""

import pandas as pd
from os.path import join
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from load_dataset import DatasetLoader

# Load the dataset
loader = DatasetLoader()
wiki_list, ai_list = loader.load_all()
n_articles = 300

print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')    

print("Generating embeddings for AI texts...")
embeddings_0 = model.encode(ai_list)

print("Generating embeddings for Wikipedia texts...")
embeddings_1 = model.encode(wiki_list)

print(f"AI embeddings shape: {embeddings_0.shape}")
print(f"Wikipedia embeddings shape: {embeddings_1.shape}")

#%% Plot 1: Distribution of mean embeddings

plt.figure(figsize=(12, 6))
# Use the same bins for both histograms to ensure proper overlap
bins = np.linspace(-0.08, 0.10, 91)
plt.hist(np.mean(embeddings_0, axis=0), bins=bins, alpha=0.6, label='AI', color='red', edgecolor='darkred', linewidth=0.5)
plt.hist(np.mean(embeddings_1, axis=0), bins=bins, alpha=0.6, label='Human', color='blue', edgecolor='darkblue', linewidth=0.5)
plt.xlabel('Mean Embedding Value', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title('Distribution of Mean Embeddings: AI vs Human', fontsize=14, fontweight='bold')
plt.legend(loc='upper right', fontsize=11)
plt.grid(alpha=0.3)
# Add vertical line at zero
plt.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5, label='Zero')
plt.tight_layout()
plt.savefig('embeddings_mean_distribution.png', dpi=150)
plt.show()

print("\n✓ Plot 1 saved: embeddings_mean_distribution.png")

#%% Calculate statistics for each text

stats_0 = []
stats_1 = []

for i in range(0, n_articles):
    stats_0.append([np.mean(embeddings_0[i, :]), np.std(embeddings_0[i, :])])
    stats_1.append([np.mean(embeddings_1[i, :]), np.std(embeddings_1[i, :])])

stats_0 = np.array(stats_0)
stats_1 = np.array(stats_1)

print(f"\nAI texts - Mean: {np.mean(stats_0[:, 0]):.4f}, Std: {np.mean(stats_0[:, 1]):.4f}")
print(f"Human texts - Mean: {np.mean(stats_1[:, 0]):.4f}, Std: {np.mean(stats_1[:, 1]):.4f}")

#%% Plot 2: Scatter plot of mean vs std

plt.figure(figsize=(12, 8))
plt.scatter(stats_0[:, 0], stats_0[:, 1], alpha=0.6, label='AI', color='red', s=50)
plt.scatter(stats_1[:, 0], stats_1[:, 1], alpha=0.6, label='Human', color='blue', s=50)
plt.xlabel('Mean Embedding Value')
plt.ylabel('Standard Deviation')
plt.title('Mean vs Std of Embeddings: AI vs Human Texts')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('embeddings_mean_vs_std.png', dpi=150)
plt.show()

print("✓ Plot 2 saved: embeddings_mean_vs_std.png")

#%% Plot 3: PCA visualization

print("\nPerforming PCA dimensionality reduction...")
all_embeddings = np.vstack([embeddings_0, embeddings_1])
labels = np.array([0] * len(embeddings_0) + [1] * len(embeddings_1))

pca = PCA(n_components=2)
embeddings_pca = pca.fit_transform(all_embeddings)

plt.figure(figsize=(12, 8))
plt.scatter(embeddings_pca[labels == 0, 0], embeddings_pca[labels == 0, 1], 
           alpha=0.6, label='AI', color='red', s=50)
plt.scatter(embeddings_pca[labels == 1, 0], embeddings_pca[labels == 1, 1], 
           alpha=0.6, label='Human', color='blue', s=50)
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
plt.title('PCA: AI vs Human Text Embeddings')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('embeddings_pca.png', dpi=150)
plt.show()

print(f"✓ Plot 3 saved: embeddings_pca.png")
print(f"  PCA explained variance: PC1={pca.explained_variance_ratio_[0]:.1%}, PC2={pca.explained_variance_ratio_[1]:.1%}")

#%% Plot 4: t-SNE visualization

print("\nPerforming t-SNE dimensionality reduction (this may take a while)...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=1000)
embeddings_tsne = tsne.fit_transform(all_embeddings)

plt.figure(figsize=(12, 8))
plt.scatter(embeddings_tsne[labels == 0, 0], embeddings_tsne[labels == 0, 1], 
           alpha=0.6, label='AI', color='red', s=50)
plt.scatter(embeddings_tsne[labels == 1, 0], embeddings_tsne[labels == 1, 1], 
           alpha=0.6, label='Human', color='blue', s=50)
plt.xlabel('t-SNE Dimension 1')
plt.ylabel('t-SNE Dimension 2')
plt.title('t-SNE: AI vs Human Text Embeddings')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('embeddings_tsne.png', dpi=150)
plt.show()

print("✓ Plot 4 saved: embeddings_tsne.png")

#%% K-Means Clustering Analysis

from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix, accuracy_score, silhouette_score

print("\n=== K-Means Clustering Analysis ===")

# Get article titles for analysis
paired_data = loader.get_paired_data()
# Create title list for all 600 samples: first 300 are AI, next 300 are Human (Wikipedia)
article_titles = []
for item in paired_data:
    article_titles.append(f"AI: {item['title']}")  # AI version
for item in paired_data:
    article_titles.append(f"Wiki: {item['title']}")  # Human Wikipedia version

# Try k=2 (since we have 2 classes: AI and Human)
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(all_embeddings)

# Calculate silhouette score
silhouette = silhouette_score(all_embeddings, cluster_labels)
print(f"\nSilhouette Score (k=2): {silhouette:.4f}")

# Map clusters to actual labels (find which cluster corresponds to which class)
# Cluster 0 or 1 might be AI or Human, so we need to check
cluster_0_ai = np.sum((cluster_labels == 0) & (labels == 0))
cluster_0_human = np.sum((cluster_labels == 0) & (labels == 1))
cluster_1_ai = np.sum((cluster_labels == 1) & (labels == 0))
cluster_1_human = np.sum((cluster_labels == 1) & (labels == 1))

print(f"\nCluster 0: {cluster_0_ai} AI, {cluster_0_human} Human")
print(f"Cluster 1: {cluster_1_ai} AI, {cluster_1_human} Human")

# Determine mapping (which cluster is predominantly AI/Human)
if cluster_0_ai > cluster_0_human:
    predicted_labels = cluster_labels  # Cluster 0 = AI (label 0)
else:
    predicted_labels = 1 - cluster_labels  # Flip: Cluster 1 = AI (label 0)

# Calculate clustering accuracy
accuracy = accuracy_score(labels, predicted_labels)
print(f"\nClustering Accuracy: {accuracy:.2%}")

# Confusion matrix
cm = confusion_matrix(labels, predicted_labels)
print(f"\nConfusion Matrix:")
print(f"                Predicted")
print(f"              AI    Human")
print(f"Actual AI   {cm[0,0]:4d}   {cm[0,1]:4d}")
print(f"       Human {cm[1,0]:4d}   {cm[1,1]:4d}")

# Calculate precision, recall, f1
from sklearn.metrics import classification_report
print(f"\nClassification Report:")
print(classification_report(labels, predicted_labels, target_names=['AI', 'Human']))

# Find 5 most representative articles from each cluster
print("\n=== Most Representative Articles (Closest to Centroids) ===")

# Calculate distances to centroids
from scipy.spatial.distance import cdist
distances_to_centroids = cdist(all_embeddings, kmeans.cluster_centers_)

# Find which cluster is AI and which is Human
ai_cluster = 0 if cluster_0_ai > cluster_0_human else 1
human_cluster = 1 - ai_cluster

# Get 5 closest AI texts to AI centroid
ai_indices = np.where(labels == 0)[0]
ai_distances = distances_to_centroids[ai_indices, ai_cluster]
top_5_ai_idx = ai_indices[np.argsort(ai_distances)[:5]]

print(f"\n📌 Top 5 Most Representative AI Texts (Cluster {ai_cluster}):")
for i, idx in enumerate(top_5_ai_idx, 1):
    title = article_titles[idx]
    distance = distances_to_centroids[idx, ai_cluster]
    print(f"  {i}. [{idx+1:3d}] {title[:60]:60s} (dist: {distance:.4f})")

# Get 5 closest Human texts to Human centroid
human_indices = np.where(labels == 1)[0]
human_distances = distances_to_centroids[human_indices, human_cluster]
top_5_human_idx = human_indices[np.argsort(human_distances)[:5]]

print(f"\n📌 Top 5 Most Representative Human Texts (Cluster {human_cluster}):")
for i, idx in enumerate(top_5_human_idx, 1):
    title = article_titles[idx]
    distance = distances_to_centroids[idx, human_cluster]
    print(f"  {i}. [{idx+1:3d}] {title[:60]:60s} (dist: {distance:.4f})")

# Find outliers - farthest from their cluster centroid
print(f"\n⚠️  Top 5 AI Outliers (Farthest from AI Centroid):")
outlier_ai_idx = ai_indices[np.argsort(ai_distances)[-5:][::-1]]
for i, idx in enumerate(outlier_ai_idx, 1):
    title = article_titles[idx]
    distance = distances_to_centroids[idx, ai_cluster]
    cluster_assigned = cluster_labels[idx]
    print(f"  {i}. [{idx+1:3d}] {title[:60]:60s} (dist: {distance:.4f}, cluster: {cluster_assigned})")

print(f"\n⚠️  Top 5 Human Outliers (Farthest from Human Centroid):")
outlier_human_idx = human_indices[np.argsort(human_distances)[-5:][::-1]]
for i, idx in enumerate(outlier_human_idx, 1):
    title = article_titles[idx]
    distance = distances_to_centroids[idx, human_cluster]
    cluster_assigned = cluster_labels[idx]
    print(f"  {i}. [{idx+1:3d}] {title[:60]:60s} (dist: {distance:.4f}, cluster: {cluster_assigned})")

#%% Plot 5: K-means clustering on PCA

plt.figure(figsize=(12, 8))
scatter = plt.scatter(embeddings_pca[:, 0], embeddings_pca[:, 1], 
                     c=cluster_labels, cmap='viridis', alpha=0.6, s=50)
plt.scatter(kmeans.cluster_centers_[:, 0] if embeddings_pca.shape == kmeans.cluster_centers_.shape 
           else pca.transform(kmeans.cluster_centers_)[:, 0],
           kmeans.cluster_centers_[:, 1] if embeddings_pca.shape == kmeans.cluster_centers_.shape 
           else pca.transform(kmeans.cluster_centers_)[:, 1],
           c='red', marker='X', s=200, edgecolors='black', linewidths=2, label='Centroids')

# Add actual labels as shapes
ai_mask = labels == 0
human_mask = labels == 1
plt.scatter(embeddings_pca[ai_mask, 0], embeddings_pca[ai_mask, 1], 
           marker='o', facecolors='none', edgecolors='red', s=100, linewidths=1.5, alpha=0.3)
plt.scatter(embeddings_pca[human_mask, 0], embeddings_pca[human_mask, 1], 
           marker='s', facecolors='none', edgecolors='blue', s=100, linewidths=1.5, alpha=0.3)

plt.colorbar(scatter, label='Cluster')
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
plt.title(f'K-Means Clustering (k=2) on PCA - Accuracy: {accuracy:.1%}')
# Create custom legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='X', color='w', markerfacecolor='red', markersize=12, 
           markeredgecolor='black', linewidth=2, label='Centroids'),
    Line2D([0], [0], marker='o', color='w', markeredgecolor='red', markersize=10, 
           markeredgewidth=2, label='AI (red circles)'),
    Line2D([0], [0], marker='s', color='w', markeredgecolor='blue', markersize=10, 
           markeredgewidth=2, label='Human (blue squares)')
]
plt.legend(handles=legend_elements, loc='best', fontsize=11)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('embeddings_kmeans_pca.png', dpi=150)
plt.show()

print("✓ Plot 5 saved: embeddings_kmeans_pca.png")

#%% Plot 6: K-means clustering on t-SNE

plt.figure(figsize=(12, 8))
scatter = plt.scatter(embeddings_tsne[:, 0], embeddings_tsne[:, 1], 
                     c=cluster_labels, cmap='viridis', alpha=0.6, s=50)

# Add actual labels as shapes
plt.scatter(embeddings_tsne[ai_mask, 0], embeddings_tsne[ai_mask, 1], 
           marker='o', facecolors='none', edgecolors='red', s=100, linewidths=1.5, alpha=0.3)
plt.scatter(embeddings_tsne[human_mask, 0], embeddings_tsne[human_mask, 1], 
           marker='s', facecolors='none', edgecolors='blue', s=100, linewidths=1.5, alpha=0.3)

plt.colorbar(scatter, label='Cluster')
plt.xlabel('t-SNE Dimension 1')
plt.ylabel('t-SNE Dimension 2')
plt.title(f'K-Means Clustering (k=2) on t-SNE - Accuracy: {accuracy:.1%}')
# Create custom legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markeredgecolor='red', markersize=10, 
           markeredgewidth=2, label='AI (red circles)'),
    Line2D([0], [0], marker='s', color='w', markeredgecolor='blue', markersize=10, 
           markeredgewidth=2, label='Human (blue squares)')
]
plt.legend(handles=legend_elements, loc='best', fontsize=11)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('embeddings_kmeans_tsne.png', dpi=150)
plt.show()

print("✓ Plot 6 saved: embeddings_kmeans_tsne.png")

#%% Elbow method - optimal k

print("\nTesting different k values (Elbow method)...")
inertias = []
silhouettes = []
k_range = range(2, 11)
cluster_purities = []

for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(all_embeddings)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(all_embeddings, km.labels_))
    
    # For k=2, track which cluster is AI/Human
    if k == 2:
        cluster_breakdown = []
        for cluster_id in range(k):
            mask = km.labels_ == cluster_id
            n_ai_in_cluster = np.sum(labels[mask] == 0)
            n_human_in_cluster = np.sum(labels[mask] == 1)
            cluster_breakdown.append((n_ai_in_cluster, n_human_in_cluster))
        cluster_purities.append(cluster_breakdown)

#%% Plot 7: Elbow curve with AI/Human distinction

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Inertia plot - normalize to show variation better
inertia_min = min(inertias)
inertia_max = max(inertias)
ax1.plot(k_range, inertias, 'bo-', linewidth=2, markersize=8)
ax1.set_xlabel('Number of Clusters (k)', fontsize=12)
ax1.set_ylabel('Inertia (Within-cluster sum of squares)', fontsize=12)
ax1.set_title('Elbow Method: Inertia vs k', fontsize=14, fontweight='bold')
ax1.grid(alpha=0.3)
# Set y-axis limits to zoom in on the curve
ax1.set_ylim([inertia_min * 0.95, inertia_max * 1.02])
ax1.axvline(x=2, color='red', linestyle='--', alpha=0.7, linewidth=2, label='k=2 (AI vs Human)')

# Add annotation showing AI/Human split at k=2
if cluster_purities:
    n_ai_c0, n_human_c0 = cluster_purities[0][0]
    n_ai_c1, n_human_c1 = cluster_purities[0][1]
    annotation_text = (f'k=2 clusters:\n'
                      f'🤖 Cluster 0: {n_ai_c0} AI, {n_human_c0} Human\n'
                      f'👤 Cluster 1: {n_ai_c1} AI, {n_human_c1} Human\n'
                      f'Accuracy: {((n_ai_c0 + n_human_c1) / (n_ai_c0 + n_human_c0 + n_ai_c1 + n_human_c1) * 100):.2f}%')
    ax1.text(0.98, 0.98, annotation_text, transform=ax1.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9, edgecolor='navy', linewidth=2))
ax1.legend(fontsize=11)
ax1.legend(fontsize=11)

# Silhouette plot with color gradient showing quality
colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(silhouettes)))
ax2.scatter(k_range, silhouettes, c=colors, s=120, zorder=3, edgecolors='black', linewidth=1.5)
ax2.plot(k_range, silhouettes, 'k-', linewidth=1.5, alpha=0.4)
ax2.set_xlabel('Number of Clusters (k)', fontsize=12)
ax2.set_ylabel('Silhouette Score', fontsize=12)
ax2.set_title('Silhouette Score vs k (Higher = Better Separation)', fontsize=14, fontweight='bold')
ax2.grid(alpha=0.3)
# Set y-axis limits to zoom in and show variation
sil_min = min(silhouettes)
sil_max = max(silhouettes)
sil_range = sil_max - sil_min
ax2.set_ylim([sil_min - 0.1 * sil_range, sil_max + 0.15 * sil_range])
ax2.axvline(x=2, color='red', linestyle='--', alpha=0.7, linewidth=2, label='k=2 (AI vs Human)')

# Highlight k=2 with annotation - positioned inside the plot
k2_silhouette = silhouettes[0]
ax2.annotate(f'k=2: {k2_silhouette:.4f}\n(AI vs Human)', 
            xy=(2, k2_silhouette), xytext=(5, sil_max - 0.3 * sil_range),
            arrowprops=dict(arrowstyle='->', color='red', lw=2.5),
            fontsize=11, color='darkred', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='yellow', alpha=0.85, edgecolor='red', linewidth=2))

ax2.legend(loc='upper right', fontsize=11)

plt.tight_layout()
plt.savefig('embeddings_elbow_analysis.png', dpi=150)
plt.show()

print("✓ Plot 7 saved: embeddings_elbow_analysis.png")

optimal_k_silhouette = k_range[np.argmax(silhouettes)]
print(f"\nOptimal k by Silhouette Score: {optimal_k_silhouette}")

#%% Statistical comparison

from scipy import stats

# Compare means
t_stat_mean, p_val_mean = stats.ttest_ind(stats_0[:, 0], stats_1[:, 0])
print(f"\n=== Statistical Comparison ===")
print(f"Mean comparison (t-test):")
print(f"  t-statistic: {t_stat_mean:.4f}")
print(f"  p-value: {p_val_mean:.6f}")
print(f"  Significant: {'Yes' if p_val_mean < 0.05 else 'No'}")

# Compare standard deviations
t_stat_std, p_val_std = stats.ttest_ind(stats_0[:, 1], stats_1[:, 1])
print(f"\nStd deviation comparison (t-test):")
print(f"  t-statistic: {t_stat_std:.4f}")
print(f"  p-value: {p_val_std:.6f}")
print(f"  Significant: {'Yes' if p_val_std < 0.05 else 'No'}")

#%% Save statistics to CSV

df_stats = pd.DataFrame({
    'text_id': list(range(1, n_articles + 1)) * 2,
    'type': ['AI'] * n_articles + ['Human'] * n_articles,
    'mean': np.concatenate([stats_0[:, 0], stats_1[:, 0]]),
    'std': np.concatenate([stats_0[:, 1], stats_1[:, 1]])
})

df_stats.to_csv('embedding_statistics.csv', index=False)
print("\n✓ Statistics saved to: embedding_statistics.csv")

#%% Summary

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
print("\nGenerated files:")
print("  1. embeddings_mean_distribution.png")
print("  2. embeddings_mean_vs_std.png")
print("  3. embeddings_pca.png")
print("  4. embeddings_tsne.png")
print("  5. embeddings_kmeans_pca.png")
print("  6. embeddings_kmeans_tsne.png")
print("  7. embeddings_elbow_analysis.png")
print("  8. embedding_statistics.csv")
print("\nKey findings:")
print(f"  - AI texts have {'higher' if np.mean(stats_0[:, 0]) > np.mean(stats_1[:, 0]) else 'lower'} mean embeddings")
print(f"  - AI texts have {'higher' if np.mean(stats_0[:, 1]) > np.mean(stats_1[:, 1]) else 'lower'} std deviation")
print(f"  - Statistical significance: {'Yes' if p_val_mean < 0.05 else 'No'} (p={p_val_mean:.6f})")
print(f"  - K-means clustering accuracy: {accuracy:.1%}")
print(f"  - Optimal k by Silhouette: {optimal_k_silhouette}")
print(f"  - Silhouette score (k=2): {silhouette:.4f}")

#%% Sentence-level analysis of top representative articles

print("\n" + "="*60)
print("SENTENCE-LEVEL ANALYSIS")
print("="*60)

import re

def split_into_sentences(text):
    """Split text into sentences using regex"""
    # Split on . ! ? followed by space and capital letter
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    # Filter out very short sentences (likely artifacts)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return sentences

print("\nExtracting sentences from top 5 AI and top 5 Human representative articles...")

# Get the top 5 AI and Human texts (already identified earlier)
# top_5_ai_idx contains indices in the range [0, 299] for AI texts
# top_5_human_idx contains indices in the range [300, 599], but we need to map to wiki_list [0, 299]
top_ai_texts = [ai_list[idx] for idx in top_5_ai_idx]
top_human_texts = [wiki_list[idx - 300] for idx in top_5_human_idx]

# Extract sentences
ai_sentences = []
human_sentences = []

for text in top_ai_texts:
    ai_sentences.extend(split_into_sentences(text))

for text in top_human_texts:
    human_sentences.extend(split_into_sentences(text))

print(f"✓ Extracted {len(ai_sentences)} sentences from top 5 AI texts")
print(f"✓ Extracted {len(human_sentences)} sentences from top 5 Human texts")

# Generate embeddings for sentences
print("\nGenerating sentence embeddings...")
ai_sentence_embeddings = model.encode(ai_sentences, show_progress_bar=False)
human_sentence_embeddings = model.encode(human_sentences, show_progress_bar=False)

# Combine all sentence embeddings
all_sentence_embeddings = np.vstack([ai_sentence_embeddings, human_sentence_embeddings])
sentence_labels = np.array([0] * len(ai_sentences) + [1] * len(human_sentences))

print(f"AI sentence embeddings: {ai_sentence_embeddings.shape}")
print(f"Human sentence embeddings: {human_sentence_embeddings.shape}")

# Cluster sentences
print("\nClustering sentences (k=2)...")
kmeans_sentences = KMeans(n_clusters=2, random_state=42, n_init=10)
sentence_cluster_labels = kmeans_sentences.fit_predict(all_sentence_embeddings)

# Calculate distances to centroids
from scipy.spatial.distance import cdist
distances_to_centroids_sent = cdist(all_sentence_embeddings, kmeans_sentences.cluster_centers_)

# Determine which cluster is AI/Human
cluster_0_ai_sent = np.sum((sentence_cluster_labels == 0) & (sentence_labels == 0))
cluster_0_human_sent = np.sum((sentence_cluster_labels == 0) & (sentence_labels == 1))

ai_cluster_sent = 0 if cluster_0_ai_sent > cluster_0_human_sent else 1
human_cluster_sent = 1 - ai_cluster_sent

print(f"\nSentence Clustering Results:")
print(f"Cluster {ai_cluster_sent} (AI): {np.sum(sentence_cluster_labels == ai_cluster_sent)} sentences")
print(f"Cluster {human_cluster_sent} (Human): {np.sum(sentence_cluster_labels == human_cluster_sent)} sentences")

# Calculate clustering accuracy
if cluster_0_ai_sent > cluster_0_human_sent:
    predicted_sentence_labels = sentence_cluster_labels
else:
    predicted_sentence_labels = 1 - sentence_cluster_labels

sentence_accuracy = accuracy_score(sentence_labels, predicted_sentence_labels)
print(f"Sentence Clustering Accuracy: {sentence_accuracy:.1%}")

# Find most representative sentences (closest to centroids)
print("\n" + "="*60)
print("MOST REPRESENTATIVE SENTENCES")
print("="*60)

# Get 10 most representative AI sentences
ai_sent_indices = np.where(sentence_labels == 0)[0]
ai_sent_distances = distances_to_centroids_sent[ai_sent_indices, ai_cluster_sent]
top_10_ai_sent_idx = ai_sent_indices[np.argsort(ai_sent_distances)[:10]]

print(f"\n🤖 Top 10 Most Representative AI Sentences (Cluster {ai_cluster_sent}):")
for i, idx in enumerate(top_10_ai_sent_idx, 1):
    sentence = ai_sentences[idx] if idx < len(ai_sentences) else human_sentences[idx - len(ai_sentences)]
    distance = distances_to_centroids_sent[idx, ai_cluster_sent]
    # Truncate long sentences
    display_sentence = sentence[:150] + "..." if len(sentence) > 150 else sentence
    print(f"\n  {i}. (dist: {distance:.4f})")
    print(f"     {display_sentence}")

# Get 10 most representative Human sentences
human_sent_indices = np.where(sentence_labels == 1)[0]
human_sent_distances = distances_to_centroids_sent[human_sent_indices, human_cluster_sent]
top_10_human_sent_idx = human_sent_indices[np.argsort(human_sent_distances)[:10]]

print(f"\n\n👤 Top 10 Most Representative Human Sentences (Cluster {human_cluster_sent}):")
for i, idx in enumerate(top_10_human_sent_idx, 1):
    sentence = human_sentences[idx - len(ai_sentences)] if idx >= len(ai_sentences) else ai_sentences[idx]
    distance = distances_to_centroids_sent[idx, human_cluster_sent]
    # Truncate long sentences
    display_sentence = sentence[:150] + "..." if len(sentence) > 150 else sentence
    print(f"\n  {i}. (dist: {distance:.4f})")
    print(f"     {display_sentence}")

print("\n" + "="*60)
print("SENTENCE ANALYSIS COMPLETE")
print("="*60)
