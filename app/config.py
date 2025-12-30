from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/btd_companion")
    
    # AI Providers
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    xai_api_key: str = os.getenv("XAI_API_KEY", "")
    
    x402_receiver_address: str = os.getenv("X402_RECEIVER_ADDRESS", "")
    x402_enabled: bool = os.getenv("X402_ENABLED", "True").lower() == "true"
    x402_testnet: bool = os.getenv("X402_TESTNET", "True").lower() == "true"
    
    # App Settings
    app_name: str = "BTD Companion"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
