"""
API routes for the AI Text Spotter application.
Implements FastAPI endpoints for text analysis, export, and health checks.
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Response
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    SentenceResult,
    OverallStats,
    ExportRequest,
    HealthResponse,
    DetectorScores,
    MathematicalFeatures
)
from app.detectors.mathematical import MathematicalDetector
from app.detectors.llm_detector import LLMDetector
from app.detectors.jury import JuryDetector
from app.services.text_processor import TextProcessor
from app.services.file_handler import FileHandler
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize detectors and services (lazy loading for LLM)
math_detector = MathematicalDetector()
llm_detector = LLMDetector()
jury_detector = JuryDetector()
text_processor = TextProcessor()
file_handler = FileHandler()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text for AI-generated content.
    
    Accepts either direct text or base64-encoded file.
    Returns sentence-by-sentence analysis with classifications.
    """
    try:
        # Extract text from request
        if request.text:
            text = request.text
        elif request.file and request.filename:
            # Decode file
            file_content = file_handler.decode_base64_file(request.file)
            text = file_handler.parse_file(file_content, request.filename)
        else:
            raise HTTPException(status_code=400, detail="Either text or file must be provided")
        
        # Check text length
        if len(text) > settings.max_text_length:
            raise HTTPException(
                status_code=400,
                detail=f"Text too long. Maximum {settings.max_text_length} characters allowed."
            )
        
        # Preprocess text
        text = text_processor.preprocess(text)
        
        # Split into sentences
        sentences = text_processor.split_into_sentences(text)
        
        if not sentences:
            raise HTTPException(status_code=400, detail="No valid sentences found in text")
        
        # Analyze each sentence
        results = []
        
        for i, sentence in enumerate(sentences):
            # Get context
            context = text_processor.extract_context(sentences, i)
            
            # Run mathematical detector
            math_result = math_detector.detect(sentence)
            
            # Run LLM detector
            llm_result = llm_detector.detect(sentence)
            
            # Run jury detector
            jury_result = jury_detector.decide(
                sentence=sentence,
                context=context,
                math_result=math_result,
                llm_result=llm_result
            )
            
            # Build result
            sentence_result = SentenceResult(
                text=sentence,
                classification=jury_result['classification'],
                confidence=jury_result['confidence'],
                scores=DetectorScores(
                    mathematical=math_result['score'],
                    llm=llm_result['score'],
                    jury_confidence=jury_result['confidence']
                ),
                reasoning=jury_result['reasoning'],
                mathematical_features=MathematicalFeatures(**math_result['features'])
            )
            
            results.append(sentence_result)
        
        # Calculate overall statistics
        total = len(results)
        human_count = sum(1 for r in results if r.classification == 'human')
        suspicious_count = sum(1 for r in results if r.classification == 'suspicious')
        ai_count = sum(1 for r in results if r.classification == 'ai')
        
        overall_stats = OverallStats(
            total_sentences=total,
            human_count=human_count,
            suspicious_count=suspicious_count,
            ai_count=ai_count,
            human_percentage=round((human_count / total) * 100, 2) if total > 0 else 0,
            suspicious_percentage=round((suspicious_count / total) * 100, 2) if total > 0 else 0,
            ai_percentage=round((ai_count / total) * 100, 2) if total > 0 else 0
        )
        
        return AnalyzeResponse(
            sentences=results,
            overall_stats=overall_stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/export")
async def export_analysis(request: ExportRequest):
    """
    Export analyzed text with highlighting to DOCX or PDF.
    
    Returns binary file download.
    """
    try:
        # Convert sentences to dict format
        sentences_data = [s.dict() for s in request.sentences]
        
        # Generate export based on format
        if request.format == 'docx':
            file_content = file_handler.export_docx(
                sentences_data,
                request.original_filename
            )
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            extension = 'docx'
        elif request.format == 'pdf':
            file_content = file_handler.export_pdf(
                sentences_data,
                request.original_filename
            )
            media_type = 'application/pdf'
            extension = 'pdf'
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'docx' or 'pdf'")
        
        # Determine filename
        if request.original_filename:
            # Replace extension
            base_name = request.original_filename.rsplit('.', 1)[0]
            filename = f"{base_name}_analyzed.{extension}"
        else:
            filename = f"analysis.{extension}"
        
        # Return file
        return Response(
            content=file_content,
            media_type=media_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during export: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns status of all detectors and models.
    """
    try:
        # Check mathematical detector (always available)
        math_loaded = True
        
        # Check LLM detector
        llm_loaded = llm_detector.is_loaded()
        
        # Check jury API
        jury_available = jury_detector.is_available()
        
        return HealthResponse(
            status="healthy",
            models_loaded={
                "mathematical": math_loaded,
                "llm": llm_loaded,
                "jury_api": jury_available
            }
        )
        
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        return HealthResponse(
            status="degraded",
            models_loaded={
                "mathematical": True,
                "llm": False,
                "jury_api": False
            }
        )
