-- ============================================================
-- HEKATE PRIME — Supabase Schema
-- Run this in Supabase SQL Editor
-- ============================================================

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- ── PROFILES ──────────────────────────────────────────────
create table public.profiles (
  id uuid references auth.users on delete cascade primary key,
  email text unique not null,
  full_name text,
  avatar_url text,
  birth_date date,
  birth_time time,
  birth_city text,
  zodiac_sign text,
  life_path_number integer,
  tier text not null default 'free' check (tier in ('free', 'premium', 'pro')),
  stripe_customer_id text unique,
  stripe_subscription_id text,
  subscription_status text default 'inactive',
  subscription_current_period_end timestamptz,
  daily_message_count integer not null default 0,
  daily_message_reset_at date not null default current_date,
  total_readings integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, full_name, avatar_url)
  values (
    new.id,
    new.email,
    new.raw_user_meta_data->>'full_name',
    new.raw_user_meta_data->>'avatar_url'
  );
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ── ORACLE SESSIONS ────────────────────────────────────────
create table public.oracle_sessions (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  mode text not null default 'oracle' check (mode in ('oracle', 'tarot', 'astro', 'synastry', 'numerology', 'shadow', 'coffee', 'palm')),
  title text,
  summary text,
  message_count integer default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ── MESSAGES ───────────────────────────────────────────────
create table public.messages (
  id uuid default uuid_generate_v4() primary key,
  session_id uuid references public.oracle_sessions(id) on delete cascade not null,
  user_id uuid references public.profiles(id) on delete cascade not null,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  mode text default 'oracle',
  tokens_used integer default 0,
  created_at timestamptz not null default now()
);

-- ── TAROT READINGS ─────────────────────────────────────────
create table public.tarot_readings (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  session_id uuid references public.oracle_sessions(id) on delete set null,
  spread_type text not null default 'three_card' check (spread_type in ('single', 'three_card', 'celtic_cross')),
  cards jsonb not null,  -- [{name, position, reversed, interpretation}]
  question text,
  overall_interpretation text,
  created_at timestamptz not null default now()
);

-- ── BIRTH CHARTS ───────────────────────────────────────────
create table public.birth_charts (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  birth_date date not null,
  birth_time time,
  birth_city text,
  latitude numeric(10,7),
  longitude numeric(10,7),
  planets jsonb,   -- {sun: {sign, degree, house}, moon: {...}, ...}
  houses jsonb,    -- {1: {sign, degree}, ...}
  aspects jsonb,   -- [{planet1, planet2, aspect, orb}]
  interpretation text,
  created_at timestamptz not null default now()
);

-- ── SYNASTRY ───────────────────────────────────────────────
create table public.synastry_readings (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  person1_name text not null,
  person1_birth_date date not null,
  person1_zodiac text,
  person2_name text not null,
  person2_birth_date date not null,
  person2_zodiac text,
  compatibility_score integer check (compatibility_score between 0 and 100),
  aspects jsonb,
  interpretation text,
  created_at timestamptz not null default now()
);

-- ── USER MEMORY (Oracle context) ───────────────────────────
create table public.user_memory (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  memory_type text not null check (memory_type in ('preference', 'event', 'concern', 'relationship', 'goal', 'reading')),
  content text not null,
  importance integer default 5 check (importance between 1 and 10),
  created_at timestamptz not null default now()
);

-- ── PAYMENTS ───────────────────────────────────────────────
create table public.payments (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  stripe_payment_intent_id text unique,
  stripe_invoice_id text,
  amount integer not null,  -- cents
  currency text default 'usd',
  status text not null,
  tier text not null,
  created_at timestamptz not null default now()
);

-- ── INDEXES ────────────────────────────────────────────────
create index idx_messages_session on public.messages(session_id);
create index idx_messages_user on public.messages(user_id);
create index idx_sessions_user on public.oracle_sessions(user_id);
create index idx_tarot_user on public.tarot_readings(user_id);
create index idx_memory_user on public.user_memory(user_id, importance desc);

-- ── ROW LEVEL SECURITY ─────────────────────────────────────
alter table public.profiles enable row level security;
alter table public.oracle_sessions enable row level security;
alter table public.messages enable row level security;
alter table public.tarot_readings enable row level security;
alter table public.birth_charts enable row level security;
alter table public.synastry_readings enable row level security;
alter table public.user_memory enable row level security;
alter table public.payments enable row level security;

-- Users can only see/edit their own data
create policy "Users own their profile" on public.profiles for all using (auth.uid() = id);
create policy "Users own their sessions" on public.oracle_sessions for all using (auth.uid() = user_id);
create policy "Users own their messages" on public.messages for all using (auth.uid() = user_id);
create policy "Users own their tarot" on public.tarot_readings for all using (auth.uid() = user_id);
create policy "Users own their charts" on public.birth_charts for all using (auth.uid() = user_id);
create policy "Users own their synastry" on public.synastry_readings for all using (auth.uid() = user_id);
create policy "Users own their memory" on public.user_memory for all using (auth.uid() = user_id);
create policy "Users own their payments" on public.payments for select using (auth.uid() = user_id);

-- ── UPDATED_AT TRIGGER ─────────────────────────────────────
create or replace function update_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;

create trigger profiles_updated_at before update on public.profiles for each row execute procedure update_updated_at();
create trigger sessions_updated_at before update on public.oracle_sessions for each row execute procedure update_updated_at();
