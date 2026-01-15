# Testing Guide

## Running Tests

### Core Functionality Tests

Test the core components without heavy ML dependencies:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python tests/test_core.py
```

This tests:
- Configuration loading
- Mathematical detector (all 6 statistical features)
- Text processor (sentence splitting, context extraction)
- API schemas (Pydantic models)
- FastAPI app initialization

### Manual API Testing

1. **Start the backend server**:
```bash
cd backend
source venv/bin/activate
python -m app.main
```

2. **Test health endpoint**:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "models_loaded": {
    "mathematical": true,
    "llm": false,
    "jury_api": false
  }
}
```

3. **Test analyze endpoint** (requires ML dependencies):
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am writing to express my strong interest in the Software Engineer position. With over five years of experience, I have developed expertise in multiple programming languages."
  }'
```

4. **Access API documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Testing

1. **Open the frontend**:
```bash
cd frontend
python -m http.server 8080
```

2. **Open in browser**: http://localhost:8080

3. **Test functionality**:
   - Upload a file (PDF, DOCX, TXT)
   - Paste text directly
   - Click "Analyze Text"
   - View results with color highlighting
   - Click sentences for details
   - Export to DOCX/PDF

### Full Integration Testing with Docker

```bash
# From project root
docker-compose up -d

# Wait for services to start
sleep 10

# Test health
curl http://localhost/api/health

# Test frontend
open http://localhost
```

## Test Coverage

### ✅ Tested Components

- **Mathematical Detector**: All 6 statistical features
  - Burstiness
  - Vocabulary richness
  - Word frequency
  - Punctuation patterns
  - Sentence complexity
  - Entropy

- **Text Processor**:
  - Sentence splitting
  - Context extraction
  - Abbreviation handling

- **Configuration**:
  - Environment variable loading
  - Settings validation

- **API Schemas**:
  - Request/response models
  - Validation rules

- **FastAPI App**:
  - Route registration
  - CORS middleware
  - Error handling

### 🔄 Requires Full Dependencies

The following components require installing all dependencies (transformers, torch, etc.):

- **LLM Detector**: DistilBERT model loading and inference
- **Jury Detector**: Groq API integration
- **File Handler**: PDF/DOCX parsing and export
- **Full analysis pipeline**: End-to-end text analysis

To install full dependencies:
```bash
cd backend
pip install -r requirements.txt
```

Note: This requires ~2GB download and 800MB RAM for models.

## Continuous Testing

### Pre-commit Checks

Before committing code, run:
```bash
# Test core functionality
python backend/tests/test_core.py

# Check Python syntax
python -m py_compile backend/app/**/*.py

# Lint JavaScript (if you have a linter)
# eslint frontend/js/**/*.js
```

### CI/CD Integration

For automated testing in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Test Core Functionality
  run: |
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install fastapi uvicorn pydantic pydantic-settings python-dotenv httpx
    python tests/test_core.py
```

## Troubleshooting

### Import Errors

If you get import errors, ensure you're in the correct directory:
```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Missing Dependencies

Install minimal dependencies for testing:
```bash
pip install fastapi uvicorn pydantic pydantic-settings python-multipart python-dotenv httpx
```

### Docker Build Fails

Check memory limits in docker-compose.yml:
```yaml
mem_limit: 900m  # Adjust based on available RAM
```

## Performance Testing

### Memory Usage

Monitor backend memory usage:
```bash
# On Linux
ps aux | grep python

# In Docker
docker stats ai-text-spotter-backend
```

### Response Time

Test API response time:
```bash
time curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Test sentence for analysis."}'
```

Target: <2 seconds for short texts, <10 seconds for full cover letters.

## Known Limitations

1. **Model Loading**: First request may be slow (~30s) as models load
2. **Memory**: Requires 800MB RAM with all models loaded
3. **Groq API**: Limited to 14,400 requests/day on free tier
4. **File Size**: Maximum 5MB per file upload
5. **Text Length**: Maximum 10,000 characters per analysis
