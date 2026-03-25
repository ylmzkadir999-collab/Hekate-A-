"""
Profile API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date

from core.database import get_current_user, get_supabase
from services.oracle_engine import calculate_life_path, get_zodiac, LIFE_PATH_DESC

router = APIRouter()

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[str] = None  # DD.MM.YYYY
    birth_time: Optional[str] = None
    birth_city: Optional[str] = None

@router.get("/me")
async def get_profile(user: dict = Depends(get_current_user)):
    return user

@router.patch("/me")
async def update_profile(body: ProfileUpdate, user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    updates = {}

    if body.full_name:
        updates["full_name"] = body.full_name
    if body.birth_date:
        updates["birth_date"] = body.birth_date
        # Auto-calculate zodiac and life path
        try:
            parts = body.birth_date.split(".")
            day, month = int(parts[0]), int(parts[1])
            updates["zodiac_sign"] = get_zodiac(day, month)
            updates["life_path_number"] = calculate_life_path(body.birth_date)
        except Exception:
            pass
    if body.birth_time:
        updates["birth_time"] = body.birth_time
    if body.birth_city:
        updates["birth_city"] = body.birth_city

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = supabase.table("profiles").update(updates).eq("id", user["id"]).execute()
    return result.data[0] if result.data else user

@router.get("/life-path")
async def get_life_path(user: dict = Depends(get_current_user)):
    lp = user.get("life_path_number")
    if not lp:
        raise HTTPException(status_code=404, detail="Birth date not set")
    desc = LIFE_PATH_DESC.get(lp, ("Gizemli", "Sayının sırları henüz çözülmedi."))
    return {
        "number": lp,
        "archetype": desc[0],
        "description": desc[1],
        "zodiac": user.get("zodiac_sign"),
    }
