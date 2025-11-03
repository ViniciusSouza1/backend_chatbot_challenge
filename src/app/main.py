from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.middleware.auth_context import AuthContextMiddleware
from app.api.routes import (
    health,
    chat,
    debug,
    ingest,
    users,
    sessions,
    messages,
    auth
)

app = FastAPI(title=settings.api_name)

# CORS to frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Context Middleware
app.add_middleware(AuthContextMiddleware)

# Routes
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(sessions.router)
app.include_router(messages.router)
app.include_router(ingest.router)
app.include_router(debug.router)
app.include_router(auth.router)
