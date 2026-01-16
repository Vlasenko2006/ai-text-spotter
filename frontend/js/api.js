/**
 * API communication module
 * Handles all backend API calls
 */

const API = {
    // Always use relative URL to go through nginx proxy
    baseURL: '/api',
    
    /**
     * Analyze text for AI-generated content
     * @param {Object} data - Request data with text or file
     * @returns {Promise<Object>} Analysis results
     */
    async analyze(data) {
        try {
            const response = await fetch(`${this.baseURL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Analysis failed');
            }
            
            return await response.json();
        } catch (error) {
            console.error('API analyze error:', error);
            throw error;
        }
    },
    
    /**
     * Export analyzed text to file
     * @param {Object} data - Export request data
     * @returns {Promise<Blob>} File blob
     */
    async export(data) {
        try {
            const response = await fetch(`${this.baseURL}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Export failed');
            }
            
            return await response.blob();
        } catch (error) {
            console.error('API export error:', error);
            throw error;
        }
    },
    
    /**
     * Check API health
     * @returns {Promise<Object>} Health status
     */
    async health() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            
            if (!response.ok) {
                throw new Error('Health check failed');
            }
            
            return await response.json();
        } catch (error) {
            console.error('API health error:', error);
            throw error;
        }
    }
};
