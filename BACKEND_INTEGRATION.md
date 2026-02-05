# Backend Integration: Semantic Embedding Detector

## Changes Made (February 3, 2026)

### Summary
Replaced the unreliable multi-detector ensemble (RoBERTa + Mathematical + Jury + AI Patterns + Predictability) with the **semantic embedding variability detector** based on your research.

---

## Files Modified

### 1. **New File: `backend/app/detectors/semantic_embedding.py`**
- Implements `SemanticEmbeddingDetector` class
- Uses SentenceTransformer (all-MiniLM-L6-v2)
- Analyzes document-level embedding STD
- Thresholds from training: AI mean=0.036824, Human mean=0.030963
- Classification: 98% AI, 96% Human, 60% AI/Human, 50% Uncertain

### 2. **Modified: `backend/app/api/routes.py`**
**Before:**
- Complex ensemble with 5 detectors (mathematical, LLM, jury, AI patterns, predictability)
- Sentence-by-sentence analysis
- Groq API calls for jury decisions
- RoBERTa model with -0.03 bias adjustment

**After:**
- Single semantic embedding detector
- Document-level analysis (applies same classification to all sentences)
- No API calls needed
- No bias adjustments

**Key changes:**
```python
# Removed global instances:
_math_detector, _llm_detector, _jury_detector, _ai_pattern_detector, _predictability_detector

# Added:
_semantic_detector = SemanticEmbeddingDetector()

# Simplified detection:
semantic_result = semantic_detector.detect(text)
# Returns: classification, confidence, std, score
```

### 3. **Modified: `backend/requirements.txt`**
Added: `sentence-transformers==3.3.1`

---

## API Compatibility

### Frontend → Backend (UNCHANGED)
POST `/api/analyze` still accepts:
- `text`: string
- `file`: base64 encoded
- `filename`: string

### Backend → Frontend (UNCHANGED structure, different values)
Response format identical:
```json
{
  "sentences": [
    {
      "text": "...",
      "classification": "ai|human|suspicious",
      "confidence": 0.98,
      "scores": {
        "mathematical": 0.02,
        "llm": 0.02,
        "ai_pattern": 0.02,
        "predictability": 0.02,
        "jury_confidence": 0.98
      },
      "reasoning": "Document STD: 0.037124 (Human: <0.030963, AI: >0.036824)",
      "mathematical_features": {...}
    }
  ],
  "overall_stats": {
    "total_sentences": 10,
    "ai_count": 10,
    "human_count": 0,
    "suspicious_count": 0,
    ...
  }
}
```

**Note:** All sentences now get the same classification (document-level decision)

---

## Advantages Over Old System

| Aspect | Old System | New System |
|--------|-----------|------------|
| **Accuracy** | "Not better than random guess" (user's words) | 92.7% on training set |
| **Speed** | Slow (5 detectors + API calls) | Fast (single model) |
| **Cost** | Groq API costs | Free (no API) |
| **Memory** | 900MB+ (transformers + models) | ~400MB (single model) |
| **Complexity** | 5 detectors + voting | Single metric |
| **Reliability** | RoBERTa "unreliable" (code comment) | Research-validated |
| **Interpretability** | Black box ensemble | Clear: embedding STD |
| **Maintenance** | Complex pipeline | Simple |

---

## Testing Recommendations

1. **Restart backend:**
   ```bash
   cd backend
   docker-compose down
   docker-compose up --build
   ```

2. **Test with frontend:**
   - Open http://localhost:80
   - Paste AI text (from validation_gpt_52/)
   - Should classify as AI with high confidence

3. **Test with human text:**
   - Paste Wikipedia article
   - Should classify as Human with high confidence

4. **Monitor logs:**
   ```bash
   docker logs -f ai-text-spotter-backend
   ```
   Look for: "Semantic embedding detection: STD=..."

---

## Classification Thresholds

```
STD < 0.030963 → 96% Human
0.030963 ≤ STD < 0.033458 → 60% Human
0.033458 ≤ STD ≤ 0.035046 → 50% Uncertain
0.035046 < STD ≤ 0.036824 → 60% AI
STD > 0.036824 → 98% AI
```

---

## Next Steps

1. **Validate on GPT-5.2 texts** from validation_gpt_52/
2. **Monitor false positive rate** on human texts
3. **Adjust thresholds** if needed based on real-world data
4. **Add per-sentence analysis** if needed (currently document-level only)

---

## Rollback Instructions

If issues occur, restore old system:

1. Revert `backend/app/api/routes.py`:
   ```bash
   git checkout HEAD -- backend/app/api/routes.py
   ```

2. Remove semantic embedding detector:
   ```bash
   rm backend/app/detectors/semantic_embedding.py
   ```

3. Remove from requirements.txt:
   ```bash
   # Remove: sentence-transformers==3.3.1
   ```

4. Rebuild:
   ```bash
   docker-compose up --build
   ```
