"""
Configuration management for AI Text Spotter application.
Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Groq API Configuration
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    
    # Model Configuration
    llm_detector_model: str = "Hello-SimpleAI/chatgpt-detector-roberta"
    model_cache_dir: str = "./models"
    
    # Application Settings
    max_text_length: int = 10000
    max_file_size_mb: int = 5
    batch_size: int = 10
    enable_caching: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # CORS Settings
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Create model cache directory if it doesn't exist
Path(settings.model_cache_dir).mkdir(parents=True, exist_ok=True)
