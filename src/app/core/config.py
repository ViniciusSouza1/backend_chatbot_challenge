# src/app/core/config.py
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    api_name: str = os.getenv("API_NAME", "Eloquent RAG Chat API")
    cors_origins: list[str] = (
        os.getenv("API_CORS_ORIGINS", "http://localhost:3000").split(",")
    )
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    database_echo: bool = os.getenv("DATABASE_ECHO", "false").lower() in {"1","true","yes"}

    # --- CONFIG ADMIN ---
    admin_emails: list[str] = os.getenv("ADMIN_EMAILS", "").split(",") if os.getenv("ADMIN_EMAILS") else []

    # --- CONFIG JWT ---
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-prod")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_exp_minutes: int = int(os.getenv("JWT_EXP_MINUTES", "60"))

settings = Settings()
