import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file from the backend folder
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(current_dir)
dotenv_path = os.path.join(backend_root, ".env")
load_dotenv(dotenv_path=dotenv_path)

class Settings:
    @property
    def DATABASE_URL(self) -> str:
        url = os.getenv("DATABASE_URL", "")
        if url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+pymysql://", 1)
        return url

    PORT: int = int(os.getenv("PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "development_secret_key_change_in_production_jwt_secret"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini") # gemini or openai
    
    APP_ENV: str = os.getenv("APP_ENV", "development")

settings = Settings()
