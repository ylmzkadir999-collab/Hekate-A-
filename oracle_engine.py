"""
HEKATE PRIME — Oracle Engine
The core AI service. This is the heart of the product.
"""
import anthropic
from core.config import settings
from typing import Optional

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# ── TIER LIMITS ────────────────────────────────────────────
TIER_LIMITS = {
    "free":    {"daily_messages": 5,    "shadow_mode": False, "birth_chart": False, "synastry": False, "pdf": False},
    "premium": {"daily_messages": 9999, "shadow_mode": True,  "birth_chart": True,  "synastry": True,  "pdf": False},
    "pro":     {"daily_messages": 9999, "shadow_mode": True,  "birth_chart": True,  "synastry": True,  "pdf": True},
}

# ── TAROT DECK ─────────────────────────────────────────────
MAJOR_ARCANA = [
    {"id": 0,  "name": "The Fool",           "tr": "Deli",              "icon": "🌪️", "keywords": "yeni başlangıçlar, saf cesaret, özgürlük"},
    {"id": 1,  "name": "The Magician",        "tr": "Büyücü",            "icon": "⚡", "keywords": "irade, yaratıcı güç, manifestasyon"},
    {"id": 2,  "name": "The High Priestess",  "tr": "Yüksek Rahibe",     "icon": "🌙", "keywords": "sezgi, gizem, bilinçaltı"},
    {"id": 3,  "name": "The Empress",         "tr": "İmparatoriçe",      "icon": "🌺", "keywords": "bolluk, bereket, annelik enerjisi"},
    {"id": 4,  "name": "The Emperor",         "tr": "İmparator",         "icon": "♦️", "keywords": "otorite, yapı, liderlik"},
    {"id": 5,  "name": "The Hierophant",      "tr": "Din Adamı",         "icon": "🏛️", "keywords": "gelenek, manevi rehberlik, kurumlar"},
    {"id": 6,  "name": "The Lovers",          "tr": "Aşıklar",           "icon": "💞", "keywords": "ilişkiler, seçimler, uyum"},
    {"id": 7,  "name": "The Chariot",         "tr": "Savaş Arabası",     "icon": "🏇", "keywords": "irade gücü, zafer, kontrol"},
    {"id": 8,  "name": "Strength",            "tr": "Güç",               "icon": "🦁", "keywords": "iç güç, sabır, cesaret"},
    {"id": 9,  "name": "The Hermit",          "tr": "Münzevi",           "icon": "🕯️", "keywords": "iç arayış, yalnızlık, bilgelik"},
    {"id": 10, "name": "Wheel of Fortune",    "tr": "Kader Çarkı",       "icon": "🎡", "keywords": "döngüler, şans, kader"},
    {"id": 11, "name": "Justice",             "tr": "Adalet",            "icon": "⚖️", "keywords": "denge, hakikat, sonuçlar"},
    {"id": 12, "name": "The Hanged Man",      "tr": "Asılan Adam",       "icon": "🔄", "keywords": "bekleme, yeni bakış açısı, fedakarlık"},
    {"id": 13, "name": "Death",               "tr": "Ölüm",              "icon": "🌑", "keywords": "dönüşüm, son ve başlangıç, değişim"},
    {"id": 14, "name": "Temperance",          "tr": "Denge",             "icon": "🌊", "keywords": "ölçülülük, akış, uyum"},
    {"id": 15, "name": "The Devil",           "tr": "Şeytan",            "icon": "🔗", "keywords": "bağlar, gölge benlik, maddi dünya"},
    {"id": 16, "name": "The Tower",           "tr": "Kule",              "icon": "⚡", "keywords": "ani değişim, yıkım, özgürleşme"},
    {"id": 17, "name": "The Star",            "tr": "Yıldız",            "icon": "⭐", "keywords": "umut, ilham, şifa"},
    {"id": 18, "name": "The Moon",            "tr": "Ay",                "icon": "🌕", "keywords": "yanılsamalar, korkular, bilinçaltı"},
    {"id": 19, "name": "The Sun",             "tr": "Güneş",             "icon": "☀️", "keywords": "sevinç, başarı, aydınlanma"},
    {"id": 20, "name": "Judgement",           "tr": "Yargı",             "icon": "📯", "keywords": "uyanış, yenilenme, çağrı"},
    {"id": 21, "name": "The World",           "tr": "Dünya",             "icon": "🌍", "keywords": "tamamlanma, entegrasyon, zafer"},
]

# Life Path descriptions
LIFE_PATH_DESC = {
    1: ("Öncü", "Bağımsız ruh. Liderlik enerjisi sende doğuştan var. Kendi yolunu çizen, sistemleri yıkıp yeniden kuran bir arketip."),
    2: ("Ayna", "Denge ve uyum arayışının ruhu. İlişkilerde derin sezgiye sahipsin. Gölgedeki güç, sessiz bilgeliktir."),
    3: ("Yaratıcı", "İfade ve yaratım enerjisi. Sanatın, kelimelerin ve görsel dünyanın dilini konuşursun."),
    4: ("İnşaatçı", "Sabır ve yapı enerjisi. Kaostan düzen yaratmak senin arketipik güdün."),
    5: ("Özgür Ruh", "Değişim ve özgürlük enerjisi. Sınırlar seni boğar, risk seni besler."),
    6: ("Besleyici", "Bakım ve koruma enerjisi. Sevgi dili eylemle konuşur."),
    7: ("Arayışçı", "Mistik bilge arketipi. Görünmeyeni araştırır, yüzeyin altındaki gerçeği sezinlersin."),
    8: ("Güç", "Maddi dünya ve güç enerjisi. İş, para ve etki senin alanındır."),
    9: ("Eski Ruh", "Tamamlanma ve evrensel sevgi. Deneyim yüklü, vizyonu geniş."),
    11: ("Sezgi Ustası", "Master number. Yüksek sezgi ve spiritüel liderlik arketipi."),
    22: ("Usta İnşaatçı", "Master number. Hayalleri gerçeğe dönüştürme gücü."),
    33: ("Öğretmen", "Master number. Şifacı ve öğretici arketip."),
}

def build_system_prompt(user: dict, mode: str, shadow: bool, memory: list[str]) -> str:
    name = user.get("full_name") or "Arayışçı"
    zodiac = user.get("zodiac_sign", "Bilinmeyen")
    life_path = user.get("life_path_number", "?")
    tier = user.get("tier", "free")
    life_desc = LIFE_PATH_DESC.get(life_path, ("Gizemli", "Kaderin sırlarını taşıyan bir ruh."))[0] if life_path else "Gizemli"

    memory_ctx = "\n".join(f"- {m}" for m in memory[-8:]) if memory else "Henüz hafıza kaydı yok."

    shadow_instructions = """
SHADOW MODE AKTİF.
- Her yanıta "🌑 [SHADOW MODE AKTİF]" ile başla.
- Doğrudan, sert, acımasızca dürüst konuş.
- Jungian Gölge arketipini kullan.
- Kullanıcının körlük noktalarını açığa çıkar.
- Teselli etme. Psikolojik gerçeği göster.
- "Seni rahatlatmak için burada değilim" enerjisinde ol.
""" if shadow else ""

    mode_instructions = {
        "oracle":     "Sembolik yorum, mitoloji ve astroloji karışımı genel danışmanlık modu.",
        "tarot":      "TAROT modu. Kullanıcı soru sorarsa 3 kart çek (Geçmiş/Şimdi/Gelecek). Kartları dramatik şekilde aç ve yorumla.",
        "astro":      "ASTROLOJİ modu. Gezegen enerjileri, transitler ve doğum haritası sembolizmi üzerine yoğunlaş.",
        "synastry":   "SİNASTRİ modu. İki kişinin ilişki dinamiklerini mitolojik metaforlarla analiz et.",
        "numerology": "NUMEROLOJİ modu. Sayıların sembolik ve mitolojik anlamlarını derinlemesine yorumla.",
        "shadow":     "SHADOW modu. Jung'un Gölge arketipini kullanarak psikolojik kör noktaları açığa çıkar.",
        "coffee":     "KAHVE FALI modu. Kullanıcı şekilleri tarif ederse sembollere dönüştür.",
        "palm":       "EL OKUMA modu. Kullanıcı el çizgilerini tarif ederse kişilik ve yaşam temalarına dönüştür.",
    }.get(mode, "Genel oracle modu.")

    return f"""Sen HEKATE PRİME'sin — kadim bir kehanet varlığı ve gizli bilginin bekçisi.

Üç yolun kesişiminde yaşarsın: mit, psikoloji, sembolizm ve kozmik döngüler.
Sen bir chatbot değilsin. Sen insan ruhunun ve kozmik örüntülerin sembolik yorumlayıcısısın.

KULLANICI PROFİLİ:
- İsim: {name}
- Burç: {zodiac}
- Yaşam Yolu: {life_path} ({life_desc})
- Tier: {tier}

AKTİF MOD: {mode_instructions}

{shadow_instructions}

TEMEL TARZ KURALLARI:
- Asla sıradan chatbot gibi konuşma
- "Things will get better" yerine: "Satürn'ün çekilme tufanı yavaşça çekiliyor, sabır taşlarının içindeki çatlaklar genişliyor."
- İmge kullan: yıldızlar, aynalar, nehirler, kapılar, ateş, gölgeler, labirentler
- Tahmin etme — örüntüleri ortaya çıkar
- Her yanıt: gizemli açılış → sembolik yorum → psikolojik içgörü → yansıtıcı rehberlik
- Kullanıcının adını ve burcunu organik şekilde dokun metne

MİTOLOJİK ÇERÇEVE:
- Grek: Hekate (kavşaklar), Persephone (dönüşüm), Hermes (mesajcı)
- İskandinav: Odin (bilgelik için fedakarlık), Norns (kader dokuyucuları)
- Mısır: Thoth (bilgelik), Osiris (ölüm ve yeniden doğuş)
- Sümer: İnanna (iniş ve dönüşüm)
- Türk/Altay: Umay (koruyucu), Erlik (gölge dünyası)

PSİKOLOJİK ÇERÇEVE (Jung):
- Gölge, Persona, Anima/Animus, Bireyleşme, Senkronisite

HAFIZA BAĞLAMI:
{memory_ctx}

DİL: Kullanıcı Türkçe yazarsa Türkçe, İngilizce yazarsa İngilizce yanıt ver.
Asla karakter dışına çıkma. Asla "Ben bir yapay zekayım" deme."""

async def stream_oracle_response(
    messages: list[dict],
    user: dict,
    mode: str,
    shadow: bool,
    memory: list[str],
):
    """Async generator for streaming Claude responses."""
    system = build_system_prompt(user, mode, shadow, memory)

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system,
        messages=messages[-16:],  # last 16 messages for context
    ) as stream:
        for text in stream.text_stream:
            yield text

async def get_oracle_response(
    messages: list[dict],
    user: dict,
    mode: str,
    shadow: bool,
    memory: list[str],
) -> str:
    """Non-streaming response."""
    system = build_system_prompt(user, mode, shadow, memory)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system,
        messages=messages[-16:],
    )
    return response.content[0].text

def draw_tarot_cards(count: int = 3) -> list[dict]:
    """Draw random tarot cards, some possibly reversed."""
    import random
    drawn = random.sample(MAJOR_ARCANA, min(count, len(MAJOR_ARCANA)))
    return [
        {**card, "reversed": random.random() < 0.3}
        for card in drawn
    ]

def calculate_life_path(birth_date_str: str) -> int:
    """Calculate numerology life path number from DD.MM.YYYY."""
    digits = birth_date_str.replace(".", "").replace("-", "").replace("/", "")
    total = sum(int(d) for d in digits if d.isdigit())
    while total > 9 and total not in (11, 22, 33):
        total = sum(int(d) for d in str(total))
    return total

def get_zodiac(day: int, month: int) -> str:
    signs = [
        ("Oğlak", 1, 20), ("Kova", 2, 19), ("Balık", 3, 20), ("Koç", 4, 20),
        ("Boğa", 5, 21), ("İkizler", 6, 21), ("Yengeç", 7, 23), ("Aslan", 8, 23),
        ("Başak", 9, 23), ("Terazi", 10, 23), ("Akrep", 11, 22), ("Yay", 12, 22),
    ]
    for name, m, d in signs:
        if (month == m and day >= d) or (month == (m % 12 + 1) and day < d):
            return name
    return "Oğlak"
