# 🚀 Quick Start Guide

Get AI Text Spotter up and running in 5 minutes!

## Prerequisites

- Python 3.10+ installed
- Git installed
- (Optional) Docker & Docker Compose for containerized deployment

## Option 1: Quick Local Setup (Recommended for Development)

### 1. Clone the Repository

```bash
git clone https://github.com/Vlasenko2006/ai-text-spotter.git
cd ai-text-spotter
```

### 2. Set Up Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 3. Configure Groq API Key (Optional but Recommended)

1. Visit https://console.groq.com/
2. Sign up for a free account
3. Create an API key
4. Edit `.env` and add your key:
   ```bash
   GROQ_API_KEY=your_actual_api_key_here
   ```

**Note**: The system works without the Groq API key, but the Jury detector will use a simple voting fallback instead of the Llama model.

### 4. Start Backend

```bash
# From backend directory
python -m app.main
```

The API will be available at http://localhost:8000

### 5. Open Frontend

Open a new terminal:

```bash
cd ../frontend
python -m http.server 8080
```

Open your browser to http://localhost:8080

### 6. Try It Out!

1. Paste some text or upload a document
2. Click "Analyze Text"
3. View the color-coded results
4. Click sentences for detailed analysis
5. Export to DOCX or PDF

## Option 2: Docker Deployment (Recommended for Production)

### 1. Clone and Configure

```bash
git clone https://github.com/Vlasenko2006/ai-text-spotter.git
cd ai-text-spotter

# Create .env file
cp backend/.env.example .env
# Edit .env and add GROQ_API_KEY (optional)
```

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

### 3. Access Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Check Logs

```bash
# View all logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend
```

### 5. Stop Services

```bash
docker-compose down
```

## Option 3: Testing Without Full Dependencies

If you want to test the core functionality without downloading heavy ML models:

```bash
cd backend
python -m venv venv
source venv/bin/activate

# Install minimal dependencies
pip install fastapi uvicorn pydantic pydantic-settings python-multipart python-dotenv httpx

# Run tests
python tests/test_core.py
```

This tests the mathematical detector, text processor, and API structure without requiring transformers or torch.

## Example Usage

### Using the Web Interface

1. **Direct Text Input**:
   - Paste your cover letter text
   - Click "Analyze Text"
   - Wait 5-30 seconds for analysis
   - View results with color highlighting

2. **File Upload**:
   - Drag and drop a PDF/DOCX/TXT file
   - Or click to select a file
   - Click "Analyze Text"
   - View results

3. **Export Results**:
   - After analysis, click "Download as DOCX" or "Download as PDF"
   - File will download with color highlighting preserved

### Using the API

**Analyze text**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am writing to express my strong interest in the Software Engineer position at your company. With over five years of experience in full-stack development, I have developed a deep expertise in Python, JavaScript, and cloud technologies."
  }'
```

**Check health**:
```bash
curl http://localhost:8000/api/health
```

**View API documentation**:
- Open http://localhost:8000/docs in your browser

## Troubleshooting

### Backend won't start

**Error: Module not found**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: Port 8000 already in use**
```bash
# Change port in .env file
PORT=8001

# Or kill the process using port 8000
# On Linux/Mac:
lsof -ti:8000 | xargs kill -9
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Frontend can't connect to backend

**CORS Error**:
- Check that CORS_ORIGINS in .env is set to `*` or includes your frontend URL
- Restart backend after changing .env

**Connection Refused**:
- Ensure backend is running on port 8000
- Check firewall settings

### Model download is slow

First run downloads ~250MB model. This is normal and only happens once.

To pre-download models:
```bash
cd backend
source venv/bin/activate
python -c "
from transformers import AutoTokenizer, AutoModelForSequenceClassification
model_name = 'Hello-SimpleAI/chatgpt-detector-roberta'
AutoTokenizer.from_pretrained(model_name, cache_dir='./models')
AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir='./models')
print('Models downloaded!')
"
```

### Docker issues

**Build fails**:
```bash
# Clear Docker cache and rebuild
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

**Out of memory**:
```bash
# Increase Docker memory limit (Docker Desktop settings)
# Or reduce mem_limit in docker-compose.yml
```

## Next Steps

- Read the [full README](README.md) for detailed documentation
- Check [TESTING.md](TESTING.md) for testing instructions
- Explore API documentation at http://localhost:8000/docs
- Customize configuration in `.env` file

## Need Help?

- Open an issue on GitHub
- Check existing issues for solutions
- Review the full documentation in README.md

## Performance Tips

1. **First Request**: May take 30 seconds as models load
2. **Subsequent Requests**: Should complete in 2-10 seconds
3. **Large Files**: Split into smaller sections if >5000 words
4. **Groq API**: Free tier has 14,400 requests/day limit
5. **Memory**: Keep texts under 10,000 characters for best performance

Enjoy using AI Text Spotter! 🔍
