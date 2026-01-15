#!/usr/bin/env python3
"""
Simple test script to validate core functionality without heavy ML dependencies.
Tests the mathematical detector, text processor, and basic API structure.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_mathematical_detector():
    """Test the mathematical detector."""
    print("Testing Mathematical Detector...")
    from app.detectors.mathematical import MathematicalDetector
    
    detector = MathematicalDetector()
    
    # Test sentence
    sentence = "I am writing to express my interest in this position."
    result = detector.detect(sentence)
    
    assert 'score' in result, "Score missing from result"
    assert 'features' in result, "Features missing from result"
    assert 0 <= result['score'] <= 1, "Score out of range"
    
    # Check all features are present
    expected_features = ['burstiness', 'vocabulary_richness', 'word_frequency', 
                        'punctuation', 'complexity', 'entropy']
    for feature in expected_features:
        assert feature in result['features'], f"Feature {feature} missing"
        assert 0 <= result['features'][feature] <= 1, f"Feature {feature} out of range"
    
    print("  ✓ Mathematical detector working correctly")
    return True


def test_text_processor():
    """Test the text processor."""
    print("Testing Text Processor...")
    from app.services.text_processor import TextProcessor
    
    processor = TextProcessor()
    
    # Test sentence splitting
    text = "This is sentence one. This is sentence two. This is sentence three."
    sentences = processor.split_into_sentences(text)
    
    assert len(sentences) == 3, f"Expected 3 sentences, got {len(sentences)}"
    
    # Test context extraction
    context = processor.extract_context(sentences, 1)
    assert 'before' in context, "Before context missing"
    assert 'after' in context, "After context missing"
    assert context['before'] is not None, "Before context should not be None"
    assert context['after'] is not None, "After context should not be None"
    
    print("  ✓ Text processor working correctly")
    return True


def test_config():
    """Test configuration loading."""
    print("Testing Configuration...")
    from app.config import settings
    
    assert settings.max_text_length > 0, "Max text length should be positive"
    assert settings.port > 0, "Port should be positive"
    assert settings.host is not None, "Host should not be None"
    
    print("  ✓ Configuration loaded correctly")
    return True


def test_api_schemas():
    """Test Pydantic schemas."""
    print("Testing API Schemas...")
    from app.models.schemas import (
        AnalyzeRequest, DetectorScores, MathematicalFeatures,
        SentenceResult, OverallStats, AnalyzeResponse
    )
    
    # Test creating schema instances
    scores = DetectorScores(
        mathematical=0.7,
        llm=0.6,
        jury_confidence=0.8
    )
    
    features = MathematicalFeatures(
        burstiness=0.5,
        vocabulary_richness=0.6,
        word_frequency=0.7,
        punctuation=0.5,
        complexity=0.6,
        entropy=0.7
    )
    
    sentence = SentenceResult(
        text="Test sentence",
        classification="human",
        confidence=0.8,
        scores=scores,
        reasoning="Test reasoning",
        mathematical_features=features
    )
    
    stats = OverallStats(
        total_sentences=10,
        human_count=6,
        suspicious_count=2,
        ai_count=2,
        human_percentage=60.0,
        suspicious_percentage=20.0,
        ai_percentage=20.0
    )
    
    response = AnalyzeResponse(
        sentences=[sentence],
        overall_stats=stats
    )
    
    assert response.sentences[0].text == "Test sentence"
    assert response.overall_stats.total_sentences == 10
    
    print("  ✓ API schemas working correctly")
    return True


def test_fastapi_app():
    """Test FastAPI app initialization."""
    print("Testing FastAPI App...")
    from app.main import app
    
    assert app.title == "AI Text Spotter", "App title incorrect"
    assert app.version == "1.0.0", "App version incorrect"
    
    # Check routes exist
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    assert '/api/analyze' in routes, "Analyze route missing"
    assert '/api/export' in routes, "Export route missing"
    assert '/api/health' in routes, "Health route missing"
    
    print("  ✓ FastAPI app initialized correctly")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Text Spotter - Core Functionality Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_config,
        test_mathematical_detector,
        test_text_processor,
        test_api_schemas,
        test_fastapi_app
    ]
    
    failed = []
    passed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__} failed: {e}")
            failed.append(test.__name__)
    
    print()
    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if failed:
        print(f"Failed tests: {', '.join(failed)}")
        print("=" * 60)
        return 1
    else:
        print("All core tests passed! ✓")
        print("=" * 60)
        return 0


if __name__ == '__main__':
    sys.exit(main())
