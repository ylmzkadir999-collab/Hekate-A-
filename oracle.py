"""
Oracle API Routes — Chat, sessions, memory
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import date
import json

from core.database import get_current_user, require_premium
from core.config import settings
from services.oracle_engine import (
    stream_oracle_response, get_oracle_response,
    TIER_LIMITS, draw_tarot_cards
)
from core.database import get_supabase

router = APIRouter()

# ── Request Models ──────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: str = "oracle"
    shadow_mode: bool = False
    stream: bool = True

class SessionCreate(BaseModel):
    mode: str = "oracle"
    title: Optional[str] = None

# ── Helpers ─────────────────────────────────────────────────

def check_daily_limit(user: dict) -> None:
    tier = user.get("tier", "free")
    limit = TIER_LIMITS[tier]["daily_messages"]
    reset_at = user.get("daily_message_reset_at")
    count = user.get("daily_message_count", 0)

    # Reset if new day
    if str(reset_at) != str(date.today()):
        supabase = get_supabase()
        supabase.table("profiles").update({
            "daily_message_count": 0,
            "daily_message_reset_at": str(date.today())
        }).eq("id", user["id"]).execute()
        count = 0

    if count >= limit:
        raise HTTPException(
            status_code=429,
            detail={
                "code": "DAILY_LIMIT_REACHED",
                "message": f"Günlük {limit} mesaj limitine ulaştın. Sınırsız mesaj için Premium'a geç.",
                "upgrade_url": "/pricing"
            }
        )

def check_feature_access(user: dict, feature: str) -> None:
    tier = user.get("tier", "free")
    if not TIER_LIMITS.get(tier, {}).get(feature, False):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "UPGRADE_REQUIRED",
                "feature": feature,
                "message": "Bu özellik için tier yükseltmen gerekiyor.",
                "upgrade_url": "/pricing"
            }
        )

async def get_user_memory(user_id: str) -> list[str]:
    supabase = get_supabase()
    result = supabase.table("user_memory") \
        .select("content") \
        .eq("user_id", user_id) \
        .order("importance", desc=True) \
        .limit(10) \
        .execute()
    return [row["content"] for row in (result.data or [])]

async def get_session_messages(session_id: str) -> list[dict]:
    supabase = get_supabase()
    result = supabase.table("messages") \
        .select("role,content") \
        .eq("session_id", session_id) \
        .order("created_at") \
        .limit(20) \
        .execute()
    return [{"role": r["role"], "content": r["content"]} for r in (result.data or [])]

def save_messages(session_id: str, user_id: str, user_msg: str, ai_msg: str, mode: str):
    supabase = get_supabase()
    supabase.table("messages").insert([
        {"session_id": session_id, "user_id": user_id, "role": "user", "content": user_msg, "mode": mode},
        {"session_id": session_id, "user_id": user_id, "role": "assistant", "content": ai_msg, "mode": mode},
    ]).execute()
    # Increment daily count
    supabase.rpc("increment_message_count", {"uid": user_id}).execute()

def auto_save_memory(user_id: str, message: str, response: str):
    """Save important context to memory."""
    keywords = ["doğum", "ilişki", "kariyer", "aşk", "para", "sağlık", "korku", "hedef", "kaygı"]
    if any(k in message.lower() for k in keywords):
        supabase = get_supabase()
        memory_entry = f"Kullanıcı şunu söyledi: {message[:120]}"
        supabase.table("user_memory").insert({
            "user_id": user_id,
            "memory_type": "concern",
            "content": memory_entry,
            "importance": 6
        }).execute()

# ── Routes ──────────────────────────────────────────────────

@router.post("/chat")
async def oracle_chat(
    req: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """Main oracle chat endpoint. Supports streaming."""
    # Rate limiting
    check_daily_limit(user)

    # Shadow mode requires premium
    if req.shadow_mode:
        check_feature_access(user, "shadow_mode")

    # Get or create session
    supabase = get_supabase()
    session_id = req.session_id

    if not session_id:
        session_res = supabase.table("oracle_sessions").insert({
            "user_id": user["id"],
            "mode": req.mode,
            "title": f"Seans — {req.mode.capitalize()}"
        }).execute()
        session_id = session_res.data[0]["id"]

    # Build conversation history
    history = await get_session_messages(session_id)
    history.append({"role": "user", "content": req.message})

    # Get memory context
    memory = await get_user_memory(user["id"])

    if req.stream:
        async def generate():
            full_response = ""
            # Send session_id first
            yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"

            async for chunk in stream_oracle_response(history, user, req.mode, req.shadow_mode, memory):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'text', 'text': chunk})}\n\n"

            # Save after stream complete
            save_messages(session_id, user["id"], req.message, full_response, req.mode)
            auto_save_memory(user["id"], req.message, full_response)
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        response = await get_oracle_response(history, user, req.mode, req.shadow_mode, memory)
        save_messages(session_id, user["id"], req.message, response, req.mode)
        auto_save_memory(user["id"], req.message, response)
        return {"reply": response, "session_id": session_id}

@router.get("/sessions")
async def list_sessions(user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("oracle_sessions") \
        .select("id,mode,title,message_count,created_at") \
        .eq("user_id", user["id"]) \
        .order("created_at", desc=True) \
        .limit(20) \
        .execute()
    return result.data

@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str, user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    # Verify ownership
    session = supabase.table("oracle_sessions") \
        .select("id").eq("id", session_id).eq("user_id", user["id"]).single().execute()
    if not session.data:
        raise HTTPException(status_code=404)

    messages = supabase.table("messages") \
        .select("*").eq("session_id", session_id).order("created_at").execute()
    return messages.data

@router.get("/memory")
async def get_memory(user: dict = Depends(get_current_user)):
    memory = await get_user_memory(user["id"])
    return {"memory": memory}

@router.delete("/memory")
async def clear_memory(user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    supabase.table("user_memory").delete().eq("user_id", user["id"]).execute()
    return {"status": "cleared"}
