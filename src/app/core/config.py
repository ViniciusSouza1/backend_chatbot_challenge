from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    api_name: str = os.getenv("API_NAME", "Eloquent RAG Chat API")
    cors_origins: list[str] = (os.getenv("API_CORS_ORIGINS","http://localhost:3000")
                               .split(","))

settings = Settings()