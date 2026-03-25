"""
HEKATE PRIME — FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.config import settings
from api.routes import oracle, auth, stripe_webhooks, tarot, astro, profile

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔮 HEKATE PRIME Oracle Engine starting...")
    yield
    print("🌑 Oracle Engine shutting down...")

app = FastAPI(
    title="HEKATE PRIME API",
    description="AI Oracle Engine — Mistik SaaS Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router,             prefix="/api/auth",    tags=["Auth"])
app.include_router(oracle.router,           prefix="/api/oracle",  tags=["Oracle"])
app.include_router(tarot.router,            prefix="/api/tarot",   tags=["Tarot"])
app.include_router(astro.router,            prefix="/api/astro",   tags=["Astrology"])
app.include_router(profile.router,          prefix="/api/profile", tags=["Profile"])
app.include_router(stripe_webhooks.router,  prefix="/api/stripe",  tags=["Payments"])

@app.get("/health")
async def health():
    return {"status": "alive", "oracle": "HEKATE PRIME v1.0"}
