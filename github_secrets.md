# GitHub Secrets Kurulum Rehberi
# Settings → Secrets and variables → Actions → New repository secret

## Backend Secrets
ANTHROPIC_API_KEY        # sk-ant-...
SUPABASE_URL             # https://xxx.supabase.co
SUPABASE_SERVICE_KEY     # eyJ... (service_role key)
STRIPE_SECRET_KEY        # sk_live_...
STRIPE_WEBHOOK_SECRET    # whsec_...
STRIPE_PRICE_PREMIUM     # price_...
STRIPE_PRICE_PRO         # price_...
BACKEND_URL              # https://hekate-api.railway.app

## Frontend Secrets (Vercel)
VERCEL_TOKEN             # vercel.com/account/tokens
VERCEL_ORG_ID            # vercel.com/account → Settings → General
VERCEL_PROJECT_ID        # vercel.com → Project → Settings → General
FRONTEND_URL             # https://hekate.yourdomain.com

## Railway Secret
RAILWAY_TOKEN            # railway.app → Account → Tokens
