/**
 * Main application logic
 * Orchestrates all modules and handles user interactions
 */

class App {
    constructor() {
        this.init();
    }
    
    init() {
        // Initialize modules
        FileHandler.init();
        
        // Bind event listeners
        this.bindEvents();
        
        // Check API health on load
        this.checkHealth();
    }
    
    bindEvents() {
        // Text input character count
        const textInput = document.getElementById('textInput');
        const charCount = document.getElementById('charCount');
        
        textInput.addEventListener('input', () => {
            const length = textInput.value.length;
            charCount.textContent = `${length} / 10,000 characters`;
            
            // Clear file if text is entered
            if (length > 0 && window.currentFile) {
                FileHandler.reset();
            }
        });
        
        // Analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.addEventListener('click', () => {
            this.analyze();
        });
        
        // Export buttons
        const exportDocxBtn = document.getElementById('exportDocxBtn');
        const exportPdfBtn = document.getElementById('exportPdfBtn');
        
        exportDocxBtn.addEventListener('click', () => {
            if (TextDisplay.currentResults) {
                const filename = window.currentFile ? window.currentFile.filename : null;
                Export.toDocx(TextDisplay.currentResults, filename);
            }
        });
        
        exportPdfBtn.addEventListener('click', () => {
            if (TextDisplay.currentResults) {
                const filename = window.currentFile ? window.currentFile.filename : null;
                Export.toPdf(TextDisplay.currentResults, filename);
            }
        });
        
        // Error close button
        const errorCloseBtn = document.getElementById('errorCloseBtn');
        errorCloseBtn.addEventListener('click', () => {
            this.hideError();
        });
    }
    
    async checkHealth() {
        try {
            const health = await API.health();
            console.log('API Health:', health);
            
            if (health.status !== 'healthy') {
                console.warn('API is not fully healthy:', health);
            }
        } catch (error) {
            console.error('Health check failed:', error);
        }
    }
    
    async analyze() {
        try {
            // Hide previous results and errors
            this.hideError();
            TextDisplay.clear();
            
            // Get input
            const textInput = document.getElementById('textInput');
            const text = textInput.value.trim();
            const file = window.currentFile;
            
            // Validate input
            if (!text && !file) {
                throw new Error('Please enter text or upload a file');
            }
            
            if (text && text.length < 50) {
                throw new Error('Text is too short. Please enter at least 50 characters.');
            }
            
            // Disable analyze button
            const analyzeBtn = document.getElementById('analyzeBtn');
            analyzeBtn.disabled = true;
            analyzeBtn.querySelector('.btn-text').textContent = 'Analyzing...';
            
            // Show loading
            document.getElementById('loadingSection').classList.remove('hidden');
            
            // Prepare request data
            const data = {};
            if (text) {
                data.text = text;
            } else if (file) {
                data.file = file.content;
                data.filename = file.filename;
            }
            
            // Call API
            const results = await API.analyze(data);
            
            // Hide loading
            document.getElementById('loadingSection').classList.add('hidden');
            
            // Display results
            TextDisplay.display(results);
            
            // Re-enable button
            analyzeBtn.disabled = false;
            analyzeBtn.querySelector('.btn-text').textContent = 'Analyze Text';
            
        } catch (error) {
            console.error('Analysis error:', error);
            
            // Hide loading
            document.getElementById('loadingSection').classList.add('hidden');
            
            // Show error
            this.showError(error.message);
            
            // Re-enable button
            const analyzeBtn = document.getElementById('analyzeBtn');
            analyzeBtn.disabled = false;
            analyzeBtn.querySelector('.btn-text').textContent = 'Analyze Text';
        }
    }
    
    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorSection.classList.remove('hidden');
        
        // Scroll to error
        errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    hideError() {
        document.getElementById('errorSection').classList.add('hidden');
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new App();
    });
} else {
    new App();
}
