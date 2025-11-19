from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # OpenAI Settings
    openai_api_key: str = ""
    
    # Google Calendar Settings
    google_calendar_id: str = ""
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True
    
    # Twilio/Exotel Settings
    twilio_auth_token: Optional[str] = None
    
    # Session Secret
    session_secret: str = ""
    
    # Facilities Configuration Path
    facilities_config_path: str = "config/facilities.json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override from environment variables if not set
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if not self.google_calendar_id:
            self.google_calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "")
        if not self.session_secret:
            self.session_secret = os.getenv("SESSION_SECRET", "")


# Global settings instance
settings = Settings()
