/**
 * Text display module
 * Handles displaying analyzed text with color-coded highlighting
 */

const TextDisplay = {
    currentResults: null,
    
    /**
     * Display analysis results
     * @param {Object} results - Analysis results from API
     */
    display(results) {
        this.currentResults = results;
        
        // Show results section
        document.getElementById('resultsSection').classList.remove('hidden');
        
        // Display statistics
        this.displayStats(results.overall_stats);
        
        // Display analyzed text
        this.displaySentences(results.sentences);
        
        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    },
    
    /**
     * Display overall statistics
     * @param {Object} stats - Overall statistics
     */
    displayStats(stats) {
        const statsContainer = document.getElementById('statsContainer');
        
        statsContainer.innerHTML = `
            <div class="stat-card human">
                <span class="stat-value">${stats.human_count}</span>
                <span class="stat-label">Human-written (${stats.human_percentage}%)</span>
            </div>
            <div class="stat-card suspicious">
                <span class="stat-value">${stats.suspicious_count}</span>
                <span class="stat-label">Suspicious (${stats.suspicious_percentage}%)</span>
            </div>
            <div class="stat-card ai">
                <span class="stat-value">${stats.ai_count}</span>
                <span class="stat-label">AI-generated (${stats.ai_percentage}%)</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.total_sentences}</span>
                <span class="stat-label">Total Sentences</span>
            </div>
        `;
    },
    
    /**
     * Display analyzed sentences with highlighting
     * @param {Array} sentences - Array of sentence results
     */
    displaySentences(sentences) {
        const container = document.getElementById('analyzedText');
        
        container.innerHTML = sentences.map((sentence, index) => {
            return `<span 
                class="sentence ${sentence.classification}" 
                data-index="${index}"
                role="button"
                tabindex="0"
                aria-label="Sentence ${index + 1}: ${sentence.classification}"
            >${sentence.text}</span> `;
        }).join('');
        
        // Add click listeners
        container.querySelectorAll('.sentence').forEach(element => {
            element.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.showSentenceDetails(sentences[index]);
            });
            
            // Keyboard support
            element.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const index = parseInt(e.target.dataset.index);
                    this.showSentenceDetails(sentences[index]);
                }
            });
        });
    },
    
    /**
     * Show detailed analysis for a sentence
     * @param {Object} sentence - Sentence result object
     */
    showSentenceDetails(sentence) {
        const modal = document.getElementById('sentenceModal');
        const modalBody = document.getElementById('modalBody');
        
        // Build features HTML
        const features = sentence.mathematical_features;
        const featuresHTML = features ? `
            <div class="modal-section">
                <h4>Statistical Features</h4>
                <div class="feature-grid">
                    <div class="feature-item">
                        <span>Burstiness:</span>
                        <strong>${(features.burstiness * 100).toFixed(1)}%</strong>
                    </div>
                    <div class="feature-item">
                        <span>Vocabulary Richness:</span>
                        <strong>${(features.vocabulary_richness * 100).toFixed(1)}%</strong>
                    </div>
                    <div class="feature-item">
                        <span>Word Frequency:</span>
                        <strong>${(features.word_frequency * 100).toFixed(1)}%</strong>
                    </div>
                    <div class="feature-item">
                        <span>Punctuation:</span>
                        <strong>${(features.punctuation * 100).toFixed(1)}%</strong>
                    </div>
                    <div class="feature-item">
                        <span>Complexity:</span>
                        <strong>${(features.complexity * 100).toFixed(1)}%</strong>
                    </div>
                    <div class="feature-item">
                        <span>Entropy:</span>
                        <strong>${(features.entropy * 100).toFixed(1)}%</strong>
                    </div>
                </div>
            </div>
        ` : '';
        
        modalBody.innerHTML = `
            <div class="modal-section">
                <h4>Sentence</h4>
                <p>"${sentence.text}"</p>
            </div>
            
            <div class="modal-section">
                <h4>Classification</h4>
                <p><strong class="sentence ${sentence.classification}">${sentence.classification.toUpperCase()}</strong></p>
                <p>Confidence: ${(sentence.confidence * 100).toFixed(1)}%</p>
            </div>
            
            <div class="modal-section">
                <h4>Detector Scores</h4>
                <p>Mathematical Detector: ${(sentence.scores.mathematical * 100).toFixed(1)}% (Human-like)</p>
                <p>LLM Detector: ${(sentence.scores.llm * 100).toFixed(1)}% (Human-like)</p>
                <p>Jury Confidence: ${(sentence.scores.jury_confidence * 100).toFixed(1)}%</p>
            </div>
            
            ${featuresHTML}
            
            <div class="modal-section">
                <h4>Reasoning</h4>
                <p>${sentence.reasoning}</p>
            </div>
        `;
        
        modal.classList.remove('hidden');
    },
    
    /**
     * Hide modal
     */
    hideModal() {
        document.getElementById('sentenceModal').classList.add('hidden');
    },
    
    /**
     * Clear results
     */
    clear() {
        this.currentResults = null;
        document.getElementById('resultsSection').classList.add('hidden');
        document.getElementById('statsContainer').innerHTML = '';
        document.getElementById('analyzedText').innerHTML = '';
    }
};

// Modal close handlers
document.getElementById('modalClose').addEventListener('click', () => {
    TextDisplay.hideModal();
});

document.getElementById('sentenceModal').addEventListener('click', (e) => {
    if (e.target.id === 'sentenceModal') {
        TextDisplay.hideModal();
    }
});

// Keyboard support for modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        TextDisplay.hideModal();
    }
});
