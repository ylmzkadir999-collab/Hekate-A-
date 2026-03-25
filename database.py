from supabase import create_client, Client
from fastapi import HTTPException, Depends, Header
from typing import Optional
from core.config import settings

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Validate Supabase JWT and return user profile."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ")[1]
    supabase = get_supabase()

    try:
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = user_response.user.id

        # Fetch profile with tier info
        profile = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        if not profile.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        return profile.data

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth error: {str(e)}")

async def require_premium(user=Depends(get_current_user)):
    if user["tier"] not in ("premium", "pro"):
        raise HTTPException(
            status_code=403,
            detail={"code": "UPGRADE_REQUIRED", "message": "Bu özellik Premium veya Pro tier gerektirir."}
        )
    return user

async def require_pro(user=Depends(get_current_user)):
    if user["tier"] != "pro":
        raise HTTPException(
            status_code=403,
            detail={"code": "UPGRADE_REQUIRED", "message": "Bu özellik Pro tier gerektirir."}
        )
    return user
