"""
Astrology API Routes — Planetary energies, birth chart basics
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from core.database import get_current_user, require_premium
from services.oracle_engine import get_oracle_response

router = APIRouter()

# Current planetary positions (in production: use Swiss Ephemeris or Astronomy API)
CURRENT_PLANETS = [
    {"planet": "☉ Güneş",   "symbol": "☉", "sign": "Balık",   "energy": "Ruhsal dönüşüm & sezgi",       "power": "high"},
    {"planet": "☽ Ay",      "symbol": "☽", "sign": "Kova",    "energy": "Yenilik & topluluk",            "power": "med"},
    {"planet": "☿ Merkür",  "symbol": "☿", "sign": "Koç",     "energy": "Cesaretli iletişim",           "power": "high"},
    {"planet": "♀ Venüs",   "symbol": "♀", "sign": "Balık",   "energy": "Romantizm & sezgisel sevgi",   "power": "high"},
    {"planet": "♂ Mars",    "symbol": "♂", "sign": "İkizler", "energy": "Çok yönlü aksiyon",            "power": "med"},
    {"planet": "♃ Jüpiter", "symbol": "♃", "sign": "Koç",     "energy": "Başlangıçlarda büyüme",        "power": "high"},
    {"planet": "♄ Satürn",  "symbol": "♄", "sign": "Kova",    "energy": "Yapı & sorumluluk (Rx)",       "power": "low"},
    {"planet": "⛢ Uranüs",  "symbol": "⛢", "sign": "Boğa",    "energy": "Ani değişim & bozulma",        "power": "med"},
    {"planet": "♆ Neptün",  "symbol": "♆", "sign": "Balık",   "energy": "Spiritüellik & yanılsamalar",  "power": "med"},
    {"planet": "♇ Plüton",  "symbol": "♇", "sign": "Oğlak",   "energy": "Dönüşüm & güç",                "power": "low"},
]

class SynastryRequest(BaseModel):
    person1_name: str
    person1_birth_date: str
    person2_name: str
    person2_birth_date: str

@router.get("/daily")
async def daily_energies(user: dict = Depends(get_current_user)):
    """Today's planetary energies + personalized message."""
    zodiac = user.get("zodiac_sign", "Koç")
    name = user.get("full_name", "Arayışçı")

    messages = [{
        "role": "user",
        "content": f"Bugünün gezegen enerjilerini {name} ({zodiac} burcu) için yorumla. "
                   f"Jüpiter Koç'ta, Venüs Balık'ta, Satürn Kova'da retrograt. "
                   f"Kısa, güçlü, mistik bir günlük mesaj ver."
    }]
    interpretation = await get_oracle_response(messages, user, "astro", False, [])

    return {
        "planets": CURRENT_PLANETS,
        "personalized_message": interpretation,
        "date": datetime.now().strftime("%d %B %Y"),
    }

@router.post("/synastry")
async def synastry(req: SynastryRequest, user: dict = Depends(require_premium)):
    """Relationship compatibility analysis. Premium only."""
    from services.oracle_engine import get_zodiac, calculate_life_path

    try:
        parts1 = req.person1_birth_date.split(".")
        sign1 = get_zodiac(int(parts1[0]), int(parts1[1]))
    except Exception:
        sign1 = "Bilinmeyen"

    try:
        parts2 = req.person2_birth_date.split(".")
        sign2 = get_zodiac(int(parts2[0]), int(parts2[1]))
    except Exception:
        sign2 = "Bilinmeyen"

    messages = [{
        "role": "user",
        "content": (
            f"Sinastri analizi yap:\n"
            f"Kişi 1: {req.person1_name}, {sign1} burcu, doğum: {req.person1_birth_date}\n"
            f"Kişi 2: {req.person2_name}, {sign2} burcu, doğum: {req.person2_birth_date}\n\n"
            f"İkisinin uyumunu, çekim dinamiklerini, karmasal gerilimlerini ve "
            f"mitolojik metaforlarla ilişki enerjisini yorumla. "
            f"Uyumluluk skoru ver (0-100)."
        )
    }]
    interpretation = await get_oracle_response(messages, user, "synastry", False, [])

    return {
        "person1": {"name": req.person1_name, "sign": sign1},
        "person2": {"name": req.person2_name, "sign": sign2},
        "interpretation": interpretation,
    }

@router.get("/zodiac/{sign}")
async def zodiac_info(sign: str, user: dict = Depends(get_current_user)):
    """Deep zodiac interpretation."""
    messages = [{
        "role": "user",
        "content": f"{sign} burcunun derin psikolojik, mitolojik ve arketipsel analizini yap. "
                   f"Güçlü yönler, gölge taraf, yaşam görevi."
    }]
    interpretation = await get_oracle_response(messages, user, "astro", False, [])
    return {"sign": sign, "interpretation": interpretation}
