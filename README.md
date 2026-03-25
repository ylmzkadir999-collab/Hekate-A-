# 𓂀 HEKATE PRIME — AI Oracle SaaS

> Mistik AI danışman platformu. Python FastAPI + Next.js 14 + Supabase + Stripe + Claude API.

## Stack

| Katman | Teknoloji |
|--------|-----------|
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| Backend | Python FastAPI |
| Database | PostgreSQL (Supabase) |
| Auth | Supabase Auth (Email + Google OAuth) |
| Payments | Stripe Subscriptions |
| AI | Anthropic Claude API (HEKATE PRIME prompt) |
| Deploy | Vercel (frontend) + Railway/Render (backend) |

## Tier Sistemi

| Tier | Fiyat | Özellikler |
|------|-------|------------|
| Free | $0 | 5 mesaj/gün, günlük tarot, burç yorumu |
| Premium | $9.99/ay | Sınırsız mesaj, doğum haritası, sinastri |
| Pro | $19.99/ay | Shadow Mode, PDF rapor, ritual takvimi |

## Kurulum

### 1. Ortam Değişkenleri

#### Backend `.env`
```
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PREMIUM=price_...
STRIPE_PRICE_PRO=price_...
FRONTEND_URL=https://yourdomain.com
```

#### Frontend `.env.local`
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

### 2. Supabase Setup

SQL sorgularını `docs/supabase_schema.sql` dosyasından çalıştır.

### 3. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Stripe Webhook (local test)

```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

## Deploy

### Backend → Railway
```bash
railway login
railway init
railway up
```

### Frontend → Vercel
```bash
vercel --prod
```
