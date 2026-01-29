"""
Configuration management using Pydantic settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Environment detection
    ENVIRONMENT: str = "development"  # Keep this default for environment detection
    
    # AI Provider (auto-detected based on environment)
    AI_PROVIDER: str
    
    # Groq API
    GROQ_API_KEY: str = ""  # Can be empty for local development
    GROQ_MODEL: str
    
    # Ollama (local development only)
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    
    # App
    APP_HOST: str = "0.0.0.0" 
    APP_PORT: int = 8000
    SECRET_KEY: str = "default-secret-change-in-production"
    
    # CORS - now as a single string that we'll split
    ALLOWED_ORIGINS: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if we're in production environment"""
        # Render sets PORT environment variable
        return (
            self.ENVIRONMENT.lower() == "production" or
            os.getenv("PORT") is not None or
            "render.com" in self.DATABASE_URL or
            "railway" in self.DATABASE_URL or
            "heroku" in self.DATABASE_URL
        )
    
    @property
    def effective_ai_provider(self) -> str:
        """Get the effective AI provider based on environment"""
        if self.AI_PROVIDER == "auto":
            # Auto-detect: Use Groq in production, Ollama in development
            return "groq" if self.is_production else "ollama"
        return self.AI_PROVIDER

settings = Settings()
