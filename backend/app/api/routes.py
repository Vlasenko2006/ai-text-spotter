"""
API routes for the AI Text Spotter application.
Implements FastAPI endpoints for text analysis, export, and health checks.
"""
import logging
from typing import List, Optional
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
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Global detector and service instances (lazy initialization)
_semantic_detector = None  # NEW: Semantic embedding detector (replaces unreliable ensemble)
_text_processor = None
_file_handler = None


def get_detectors_and_services():
    """Lazy initialization of detectors and services."""
    global _semantic_detector, _text_processor, _file_handler
    
    if _semantic_detector is None:
        from app.detectors.semantic_embedding import SemanticEmbeddingDetector
        _semantic_detector = SemanticEmbeddingDetector()
    
    if _text_processor is None:
        from app.services.text_processor import TextProcessor
        _text_processor = TextProcessor()
    
    if _file_handler is None:
        from app.services.file_handler import FileHandler
        _file_handler = FileHandler()
    
    return _semantic_detector, _text_processor, _file_handler


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text for AI-generated content.
    
    Accepts either direct text or base64-encoded file.
    Returns sentence-by-sentence analysis with classifications.
    """
    try:
        # Get detectors and services
        semantic_detector, text_processor, file_handler = get_detectors_and_services()
        
        # Extract text from request
        if request.text:
            text = request.text
        elif request.file and request.filename:
            # Decode file
            file_content = file_handler.decode_base64_file(request.file)
            text = file_handler.parse_file(file_content, request.filename)
        else:
            raise HTTPException(status_code=400, detail="Either text or file must be provided")
        
        # Truncate text if too long (instead of rejecting)
        if len(text) > settings.max_text_length:
            text = text[:settings.max_text_length]
        
        # Preprocess text
        text = text_processor.preprocess(text)
        
        # Split into sentences
        sentences = text_processor.split_into_sentences(text)
        
        if not sentences:
            raise HTTPException(status_code=400, detail="No valid sentences found in text")
        
        # Run semantic embedding detection on FULL TEXT (not sentence-by-sentence)
        # This provides document-level analysis based on embedding variability
        semantic_result = semantic_detector.detect(text)
        
        logger.info(f"Semantic embedding detection: "
                   f"STD={semantic_result['std']:.6f}, "
                   f"Classification={semantic_result['classification']}, "
                   f"Score={semantic_result['score']:.4f}, "
                   f"Confidence={semantic_result['confidence']:.2%}")
        
        # Apply the same classification to all sentences (document-level decision)
        # This is consistent with the semantic embedding approach which analyzes full documents
        results = []
        
        for sentence in sentences:
            sentence_result = SentenceResult(
                text=sentence,
                classification=semantic_result['classification'],
                confidence=semantic_result['confidence'],
                scores=DetectorScores(
                    mathematical=semantic_result['score'],
                    llm=semantic_result['score'],
                    ai_pattern=semantic_result['score'],
                    predictability=semantic_result['score'],
                    jury_confidence=semantic_result['confidence']
                ),
                reasoning=f"Document STD: {semantic_result['std']:.6f} "
                         f"(Human: <{semantic_result['thresholds']['human_mean']:.6f}, "
                         f"AI: >{semantic_result['thresholds']['ai_mean']:.6f})",
                mathematical_features=MathematicalFeatures(
                    burstiness=0.5,
                    vocabulary_richness=0.5,
                    word_frequency=0.5,
                    punctuation=0.5,
                    complexity=0.5,
                    entropy=0.5
                )
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
        # Get file handler
        _, _, file_handler = get_detectors_and_services()
        
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
    
    Returns status of semantic embedding detector.
    """
    try:
        # Check if semantic detector has been initialized
        semantic_loaded = _semantic_detector is not None
        
        return HealthResponse(
            status="healthy",
            models_loaded={
                "semantic_embedding": semantic_loaded
            }
        )
        
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        return HealthResponse(
            status="degraded",
            models_loaded={
                "semantic_embedding": False
            }
        )
