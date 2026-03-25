"""
Auth Routes — Supabase handles the heavy lifting
These are helper endpoints for profile setup post-signup
"""
from fastapi import APIRouter, Depends
from core.database import get_current_user

router = APIRouter()

@router.get("/me")
async def auth_me(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "email": user["email"],
        "tier": user.get("tier", "free"),
        "full_name": user.get("full_name"),
        "zodiac_sign": user.get("zodiac_sign"),
        "life_path_number": user.get("life_path_number"),
    }
