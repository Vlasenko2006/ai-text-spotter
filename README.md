# Distinguishing AI-Generated from Human-Written Text: A Semantic Analysis

## Introduction


Each writer has its unique style of reasoning/explanation, which is also true for large language models. This style is a kind of literature fingerprint, allowing to spot the authorship. Based on this fact we develped a method ***ai-spotter*** that defines AI written texts with accuracy greater than 75%. Although the modern AI detectors show higher accuracy, our method stays out due to its simplicity and mathematical explainability. It can be used as a separate tool for identifying AI texts or serve as a suplementary to existing ones to sharpen their accuracy.  

### Intuition behind the method

Comparing AI and human written texts approximately of the same length and topic we noticed that: humans use concrete imagery with concise descriptions in their explanations, while AI-generated content tends to be more abstract and verbose. Presenting texts in the embedded symantical space, where each symantic expression corresponds to a vector in this space we found 25% larger spread of these vectors corresponding to AI texts. We used this spread as keystone marker in our detection technique.

### Text processing and limitation of the method

The AI-spotter splits the input text splits 50 chuncks approximately of the same length, consisting of several sentences with the smallest size of a chunk of one sentence. It converts these chunks into semantic vectors using HuggingFace's `SentenceTransfomer` and computes standard deviation of those. Then it compares the mean standard deviation of the resulted set to the reference mean standard deviation values obtained for AI and Human texts and makes it classification.

If the input text has less than 50 sentenses, each chunk becomes equal to the sentence, and the total amount of chunks is equal to the amout of sentences. Since the reliable standard deviation estimates requires large number of chuncks, the method has lesser accuracy for the texts with small sentence contnent.    

## Treining and Testing AI-spotter

We test our method on 600 wikipedia articles and AI generated texts on the same topics. We used LLama 3.1/3.3 and GPT-5 mini LLMs for AI text generation. In additio we found that AI texts have the same spread irrespective of the language model used, which also indicates on the common way of generationg textsExpected Outcomes
Each writer has its unique style of reasoning/explanation, which is also true for large language models. This style is similar to fingerprint, allowing t. 


**AI-generated text detection system for cover letters using ensemble detection**

[![Security](https://img.shields.io/badge/security-updated-brightgreen)](SECURITY.md)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)


> **Security Note**: All dependencies updated to latest secure versions (January 2025). See [SECURITY.md](SECURITY.md) for details.


## 📋 Requirements

### Backend
- Python 3.10+
- 800MB RAM (optimized for AWS t3.micro)
- Groq API key (free tier: 14,400 requests/day)

### Frontend
- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled

## 🛠️ Installation

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/Vlasenko2006/ai-text-spotter.git
cd ai-text-spotter
```

2. **Set up backend**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

3. **Run backend**
```bash
# From backend directory
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Run frontend**
```bash
# Open frontend/index.html in browser
# Or use a simple HTTP server:
cd frontend
python -m http.server 8080
# Then open http://localhost:8080
```

### Docker Deployment

1. **Create .env file**
```bash
cp backend/.env.example .env
# Edit .env and add your GROQ_API_KEY
```

2. **Run with Docker Compose**
```bash
docker-compose up -d
```

3. **Access application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### AWS t3.micro Deployment

**Optimizations for 1GB RAM:**
- Single worker process
- Lazy model loading
- Request queuing
- Memory limits enforced

**Steps:**

1. **Launch t3.micro instance** (Ubuntu 22.04 LTS)

2. **Install Docker & Docker Compose**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

3. **Clone and configure**
```bash
git clone https://github.com/Vlasenko2006/ai-text-spotter.git
cd ai-text-spotter
cp backend/.env.example .env
nano .env  # Add GROQ_API_KEY
```

4. **Deploy**
```bash
docker-compose up -d
```

5. **Configure security group**
- Allow inbound: HTTP (80), HTTPS (443), SSH (22)
- Restrict SSH to your IP

6. **Optional: Set up domain & SSL**
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

## 🔧 Configuration

### Environment Variables

```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Model Configuration
LLM_DETECTOR_MODEL=Hello-SimpleAI/chatgpt-detector-roberta
MODEL_CACHE_DIR=./models

# Application Settings
MAX_TEXT_LENGTH=10000
MAX_FILE_SIZE_MB=5
BATCH_SIZE=10
ENABLE_CACHING=true

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1

# CORS
CORS_ORIGINS=*
```

### Getting Groq API Key

1. Visit https://console.groq.com/
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and add to your .env file

**Free tier limits:**
- 14,400 requests per day
- 30 requests per minute
- Sufficient for personal use and small deployments

## 📚 API Documentation

### POST /api/analyze

Analyze text for AI-generated content.

**Request:**
```json
{
  "text": "optional direct text",
  "file": "optional base64 encoded file",
  "filename": "optional filename"
}
```

**Response:**
```json
{
  "sentences": [
    {
      "text": "sentence content",
      "classification": "human|suspicious|ai",
      "confidence": 0.85,
      "scores": {
        "mathematical": 0.72,
        "llm": 0.68,
        "jury_confidence": 0.85
      },
      "reasoning": "brief explanation",
      "mathematical_features": {
        "burstiness": 0.65,
        "vocabulary_richness": 0.78,
        "word_frequency": 0.55,
        "punctuation": 0.62,
        "complexity": 0.70,
        "entropy": 0.68
      }
    }
  ],
  "overall_stats": {
    "total_sentences": 20,
    "human_count": 12,
    "suspicious_count": 5,
    "ai_count": 3,
    "human_percentage": 60.0,
    "suspicious_percentage": 25.0,
    "ai_percentage": 15.0
  }
}
```

### POST /api/export

Export analyzed text with highlighting.

**Request:**
```json
{
  "sentences": [...],
  "format": "docx|pdf",
  "original_filename": "optional"
}
```

**Response:** Binary file download

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": {
    "mathematical": true,
    "llm": true,
    "jury_api": true
  }
}
```

## 🎨 Frontend Usage

1. **Upload or paste text**
   - Drag and drop a file (PDF, DOCX, TXT)
   - Or click to select a file
   - Or paste text directly

2. **Analyze**
   - Click "Analyze Text" button
   - Wait for analysis to complete

3. **View results**
   - See overall statistics
   - Read color-coded text
   - Click sentences for detailed analysis

4. **Export**
   - Download as DOCX with highlighting
   - Download as PDF with highlighting

## 🧪 Testing

### Test Mathematical Detector
```bash
cd backend
python -c "
from app.detectors.mathematical import MathematicalDetector
detector = MathematicalDetector()
result = detector.detect('This is a test sentence with varied complexity.')
print(result)
"
```

### Test API
```bash
# Health check
curl http://localhost:8000/api/health

# Analyze text
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"I am writing to express my strong interest in the position."}'
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Style

- Python: Follow PEP 8
- JavaScript: Use ESLint
- Add comments for complex logic
- Write descriptive commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **HuggingFace** for transformer models
- **Groq** for Llama API access
- **FastAPI** for the backend framework
- Open source community

## 📧 Contact

Project Link: [https://github.com/Vlasenko2006/ai-text-spotter](https://github.com/Vlasenko2006/ai-text-spotter)

## ⚠️ Disclaimer

This tool is for educational and analytical purposes. Detection results should not be used as definitive proof of AI generation. Always consider context and use multiple verification methods.
