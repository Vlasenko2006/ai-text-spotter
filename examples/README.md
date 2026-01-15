# Sample Cover Letters for Testing

This directory contains sample cover letters for testing the AI Text Spotter application.

## Files

- `human_written.txt` - Example of a human-written cover letter
- `ai_generated.txt` - Example of an AI-generated cover letter
- `mixed.txt` - Example with both human and AI-generated content

## Usage

You can use these files to test the application:

1. **Via Web Interface**:
   - Upload the file using the drag-and-drop area
   - Or copy the text and paste it directly

2. **Via API**:
   ```bash
   # Read file and analyze
   curl -X POST http://localhost:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d "{\"text\":\"$(cat examples/human_written.txt)\"}"
   ```

## Expected Results

- `human_written.txt`: Should show mostly green (human-written) sentences
- `ai_generated.txt`: Should show mostly red (AI-generated) sentences
- `mixed.txt`: Should show a mix of colors

Note: Results may vary based on the detector models and confidence thresholds.
