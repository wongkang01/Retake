from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Retake AI"
    VERSION: str = "v2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    API_KEY: str = "dev_key"
    
    # AI / External Services
    GEMINI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    
    # Database
    USE_CHROMA: bool = True
    CHROMA_PERSIST_DIRECTORY: str = "chroma_db"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"), 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()
