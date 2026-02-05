/**
 * File handler module
 * Handles file upload, drag-and-drop, and text extraction
 */

const FileHandler = {
    maxFileSize: 5 * 1024 * 1024, // 5MB
    supportedTypes: ['.pdf', '.docx', '.doc', '.txt'],
    
    /**
     * Initialize file handler
     */
    init() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Keyboard support
        uploadArea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInput.click();
            }
        });
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFile(file);
            }
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const file = e.dataTransfer.files[0];
            if (file) {
                this.handleFile(file);
            }
        });
    },
    
    /**
     * Handle file upload
     * @param {File} file - Uploaded file
     */
    async handleFile(file) {
        try {
            // Validate file type
            const extension = '.' + file.name.split('.').pop().toLowerCase();
            if (!this.supportedTypes.includes(extension)) {
                throw new Error(`Unsupported file type. Please use ${this.supportedTypes.join(', ')}`);
            }
            
            // Validate file size
            if (file.size > this.maxFileSize) {
                throw new Error(`File too large. Maximum size is ${this.maxFileSize / 1024 / 1024}MB`);
            }
            
            // Read file as base64
            const base64 = await this.fileToBase64(file);
            
            // Store for analysis
            window.currentFile = {
                content: base64,
                filename: file.name
            };
            
            // Update UI
            const uploadArea = document.getElementById('uploadArea');
            uploadArea.innerHTML = `
                <div class="upload-icon">✓</div>
                <p class="upload-text">${file.name}</p>
                <p class="upload-hint">File loaded successfully. Click "Analyze Text" to continue.</p>
            `;
            
            // Clear text input
            document.getElementById('textInput').value = '';
            
        } catch (error) {
            console.error('File handling error:', error);
            alert(error.message);
        }
    },
    
    /**
     * Convert file to base64
     * @param {File} file - File to convert
     * @returns {Promise<string>} Base64 encoded string
     */
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                resolve(reader.result);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    },
    
    /**
     * Reset file upload
     */
    reset() {
        window.currentFile = null;
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        // Clear file input value before removing it
        if (fileInput) {
            fileInput.value = '';
        }
        
        uploadArea.innerHTML = `
            <div class="upload-icon">📄</div>
            <p class="upload-text">Drag and drop a file here, or click to select</p>
            <p class="upload-hint">Supports PDF, DOCX, TXT (max 5MB)</p>
            <input type="file" id="fileInput" accept=".pdf,.docx,.doc,.txt" hidden aria-label="File input">
        `;
        
        // Re-initialize file input event listener
        const newFileInput = document.getElementById('fileInput');
        newFileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFile(file);
            }
        });
    }
};
