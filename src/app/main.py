from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, chat, debug, ingest

app = FastAPI(title=settings.api_name)

# CORS para o frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(debug.router)
