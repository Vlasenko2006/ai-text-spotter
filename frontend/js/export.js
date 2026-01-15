/**
 * Export module
 * Handles downloading analyzed text as DOCX or PDF
 */

const Export = {
    /**
     * Export results to DOCX
     * @param {Object} results - Analysis results
     * @param {string} originalFilename - Original filename
     */
    async toDocx(results, originalFilename = null) {
        try {
            const data = {
                sentences: results.sentences,
                format: 'docx',
                original_filename: originalFilename
            };
            
            const blob = await API.export(data);
            
            // Determine filename
            const filename = this.generateFilename(originalFilename, 'docx');
            
            // Download
            this.downloadBlob(blob, filename);
            
        } catch (error) {
            console.error('Export to DOCX error:', error);
            alert('Failed to export to DOCX: ' + error.message);
        }
    },
    
    /**
     * Export results to PDF
     * @param {Object} results - Analysis results
     * @param {string} originalFilename - Original filename
     */
    async toPdf(results, originalFilename = null) {
        try {
            const data = {
                sentences: results.sentences,
                format: 'pdf',
                original_filename: originalFilename
            };
            
            const blob = await API.export(data);
            
            // Determine filename
            const filename = this.generateFilename(originalFilename, 'pdf');
            
            // Download
            this.downloadBlob(blob, filename);
            
        } catch (error) {
            console.error('Export to PDF error:', error);
            alert('Failed to export to PDF: ' + error.message);
        }
    },
    
    /**
     * Generate filename for export
     * @param {string} originalFilename - Original filename
     * @param {string} extension - File extension
     * @returns {string} Generated filename
     */
    generateFilename(originalFilename, extension) {
        if (originalFilename) {
            const baseName = originalFilename.replace(/\.[^/.]+$/, '');
            return `${baseName}_analyzed.${extension}`;
        }
        
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        return `analysis_${timestamp}.${extension}`;
    },
    
    /**
     * Download blob as file
     * @param {Blob} blob - File blob
     * @param {string} filename - Filename
     */
    downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};
