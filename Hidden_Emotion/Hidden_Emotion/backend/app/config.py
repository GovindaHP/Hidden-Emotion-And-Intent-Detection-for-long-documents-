import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Hidden Emotion & Intent Detection API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-hidden-emotion-intent-key-2026-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "hidden_emotion_db")
    USE_FALLBACK_DB: bool = True
    
    # Model Hub Names
    EMOTION_MODEL_NAME: str = "j-hartmann/emotion-english-distilroberta-base"
    SENTIMENT_MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"
    SUMMARIZER_MODEL_NAME: str = "facebook/bart-large-cnn"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # NLP Parameters
    CHUNK_SIZE_WORDS: int = 250
    CHUNK_OVERLAP_WORDS: int = 50
    TOP_K_KEYWORDS: int = 20
    TOP_SENTENCES_COUNT: int = 10
    
    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt", ".md"}

    class Config:
        case_sensitive = True

settings = Settings()
