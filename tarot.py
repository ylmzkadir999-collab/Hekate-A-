"""
HEKATE PRIME — Tarot API Routes
78 kartlık tam deste: Major + Minor Arcana
"""
import random
from fastapi import APIRouter, Depends, HTTPException
from core.database import supabase
from middleware.auth import get_current_user
from data.tarot_deck import FULL_DECK, MAJOR_ARCANA, get_deck_stats

router = APIRouter()

SPREADS = {
    "single":  {"count":1,  "positions":["Mesajın"]},
    "three":   {"count":3,  "positions":["Geçmiş","Şimdi","Gelecek"]},
    "celtic":  {"count":10, "positions":["Mevcut","Zorluk","Bilinçaltı","Geçmiş","Olası Gelecek","Yakın Gelecek","İç Durum","Dış Etkiler","Umutlar/Korkular","Sonuç"]},
    "love":    {"count":5,  "positions":["Sen","Partner","İlişki Enerjisi","Engel","Olası Gelecek"]},
    "career":  {"count":4,  "positions":["Mevcut Durum","Güçlerin","Gelişme Alanı","Öneri"]},
    "shadow":  {"count":3,  "positions":["Bilinçli Ben","Gölge (Bastırılan)","Bütünleşme Yolu"]},
    "year":    {"count":12, "positions":["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]},
}

def draw_cards(count: int, major_only: bool = False) -> list:
    deck = MAJOR_ARCANA if major_only else FULL_DECK
    drawn = random.sample(deck, min(count, len(deck)))
    result = []
    for card in drawn:
        rev = random.random() < 0.3
        result.append({**card, "reversed": rev,
                        "display_name": f"{card['tr']} {'(Ters)' if rev else ''}".strip(),
                        "meaning": card["reversed"] if rev else card["upright"]})
    return result

@router.post("/draw")
async def draw(spread: str = "three", question: str = "", major_only: bool = False,
               user: dict = Depends(get_current_user)):
    cfg   = SPREADS.get(spread, SPREADS["three"])
    cards = draw_cards(cfg["count"], major_only)
    positioned = [{**c, "position": cfg["positions"][i] if i < len(cfg["positions"]) else f"Kart {i+1}"}
                  for i, c in enumerate(cards)]
    try:
        supabase.table("tarot_readings").insert({
            "user_id": user["id"], "spread_type": spread,
            "question": question[:500] or None,
            "cards_json": str([c["tr"] for c in positioned]),
        }).execute()
    except: pass
    return {"spread": spread, "question": question, "positions": cfg["positions"],
            "cards": positioned, "deck_mode": "major_only" if major_only else "full_78"}

@router.get("/spreads")
async def list_spreads(user: dict = Depends(get_current_user)):
    return {k: {"count": v["count"], "positions": v["positions"]} for k, v in SPREADS.items()}

@router.get("/deck")
async def deck_info(suit: str = "", user: dict = Depends(get_current_user)):
    if suit:
        cards = [c for c in FULL_DECK if c.get("suit") == suit]
        return {"suit": suit, "count": len(cards), "cards": cards}
    return {"stats": get_deck_stats()}

@router.get("/card/{card_id}")
async def get_card(card_id: str, user: dict = Depends(get_current_user)):
    card = (next((c for c in MAJOR_ARCANA if c["id"] == int(card_id)), None)
            if card_id.isdigit()
            else next((c for c in FULL_DECK if c["id"] == card_id), None))
    if not card: raise HTTPException(404, "Kart bulunamadı")
    return card

@router.get("/history")
async def reading_history(user: dict = Depends(get_current_user)):
    try:
        r = supabase.table("tarot_readings").select("id,spread_type,question,cards_json,created_at") \
            .eq("user_id", user["id"]).order("created_at", desc=True).limit(20).execute()
        return {"readings": r.data}
    except: return {"readings": []}
