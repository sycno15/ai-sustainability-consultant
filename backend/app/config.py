import logging
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings
from pydantic import Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai-sustainability-consultant")

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = Field(..., min_length=1)
    SUPABASE_URL: str = Field(..., min_length=1)
    SUPABASE_ANON_KEY: str = Field(..., min_length=1)
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., min_length=1)
    DATABASE_URL: str = Field(..., min_length=1)
    JWT_SECRET: str = Field(..., min_length=1)
    RESEND_API_KEY: str = Field(..., min_length=1)
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

try:
    settings = Settings()
    logger.info("Environment variables loaded and validated successfully.")
except Exception as e:
    logger.error(f"Environment validation failed: {str(e)}")
    raise e
