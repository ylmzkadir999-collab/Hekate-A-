from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Anthropic
    ANTHROPIC_API_KEY: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str  # service_role key (backend only, never expose)

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_PREMIUM: str  # price_xxx from Stripe dashboard
    STRIPE_PRICE_PRO: str

    # App
    FRONTEND_URL: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"

    # Tier limits
    FREE_DAILY_MESSAGES: int = 5
    PREMIUM_DAILY_MESSAGES: int = 9999  # effectively unlimited
    PRO_DAILY_MESSAGES: int = 9999

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
