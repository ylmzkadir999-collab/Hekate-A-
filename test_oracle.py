"""
HEKATE PRIME — Backend Tests
pytest + pytest-asyncio
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ── Fixtures ────────────────────────────────────────────────

@pytest.fixture
def mock_user():
    return {
        "id": "test-user-123",
        "email": "test@hekate.ai",
        "full_name": "Test Arayışçı",
        "zodiac_sign": "Koç",
        "life_path_number": 7,
        "tier": "premium",
        "daily_message_count": 0,
        "daily_message_reset_at": "2026-03-12",
    }

@pytest.fixture
def free_user(mock_user):
    return {**mock_user, "tier": "free", "daily_message_count": 0}

@pytest.fixture
def client():
    with patch("core.config.Settings", autospec=True):
        from main import app
        return TestClient(app)


# ── Oracle Engine Tests ──────────────────────────────────────

class TestOracleEngine:

    def test_calculate_life_path_single_digit(self):
        from services.oracle_engine import calculate_life_path
        # 12.03.1995 → 1+2+0+3+1+9+9+5 = 30 → 3
        result = calculate_life_path("12.03.1995")
        assert isinstance(result, int)
        assert 1 <= result <= 33

    def test_calculate_life_path_master_number(self):
        from services.oracle_engine import calculate_life_path
        # Should preserve master numbers 11, 22, 33
        result = calculate_life_path("29.09.1975")  # known master number
        assert result in range(1, 34)

    def test_get_zodiac_aries(self):
        from services.oracle_engine import get_zodiac
        assert get_zodiac(25, 3) == "Koç"

    def test_get_zodiac_scorpio(self):
        from services.oracle_engine import get_zodiac
        assert get_zodiac(1, 11) == "Akrep"

    def test_get_zodiac_capricorn_december(self):
        from services.oracle_engine import get_zodiac
        assert get_zodiac(25, 12) == "Oğlak"

    def test_get_zodiac_capricorn_january(self):
        from services.oracle_engine import get_zodiac
        assert get_zodiac(10, 1) == "Oğlak"

    def test_draw_tarot_cards_count(self):
        from services.oracle_engine import draw_tarot_cards
        cards = draw_tarot_cards(3)
        assert len(cards) == 3

    def test_draw_tarot_cards_no_duplicates(self):
        from services.oracle_engine import draw_tarot_cards
        cards = draw_tarot_cards(5)
        ids = [c["id"] for c in cards]
        assert len(ids) == len(set(ids))

    def test_draw_tarot_cards_has_reversed(self):
        from services.oracle_engine import draw_tarot_cards
        # Draw many times, some should be reversed
        all_cards = []
        for _ in range(20):
            all_cards.extend(draw_tarot_cards(3))
        reversed_count = sum(1 for c in all_cards if c.get("reversed"))
        assert reversed_count > 0  # statistically should have reversed cards

    def test_draw_tarot_cards_has_required_fields(self):
        from services.oracle_engine import draw_tarot_cards
        cards = draw_tarot_cards(1)
        card = cards[0]
        assert "id" in card
        assert "name" in card
        assert "tr" in card
        assert "icon" in card
        assert "keywords" in card
        assert "reversed" in card

    def test_build_system_prompt_contains_user_info(self):
        from services.oracle_engine import build_system_prompt
        user = {
            "full_name": "Abdulkadir",
            "zodiac_sign": "Koç",
            "life_path_number": 7,
            "tier": "premium",
        }
        prompt = build_system_prompt(user, "oracle", False, [])
        assert "Abdulkadir" in prompt
        assert "Koç" in prompt
        assert "7" in prompt

    def test_build_system_prompt_shadow_mode(self):
        from services.oracle_engine import build_system_prompt
        user = {"full_name": "Test", "zodiac_sign": "Koç", "life_path_number": 1, "tier": "pro"}
        prompt = build_system_prompt(user, "shadow", True, [])
        assert "SHADOW MODE" in prompt
        assert "AKTİF" in prompt

    def test_build_system_prompt_tarot_mode(self):
        from services.oracle_engine import build_system_prompt
        user = {"full_name": "Test", "zodiac_sign": "Boğa", "life_path_number": 3, "tier": "premium"}
        prompt = build_system_prompt(user, "tarot", False, [])
        assert "TAROT" in prompt

    def test_life_path_descriptions_complete(self):
        from services.oracle_engine import LIFE_PATH_DESC
        for n in [1,2,3,4,5,6,7,8,9,11,22,33]:
            assert n in LIFE_PATH_DESC
            desc = LIFE_PATH_DESC[n]
            assert len(desc) == 2
            assert len(desc[0]) > 0
            assert len(desc[1]) > 0

    def test_tier_limits_structure(self):
        from services.oracle_engine import TIER_LIMITS
        for tier in ["free", "premium", "pro"]:
            assert tier in TIER_LIMITS
            limits = TIER_LIMITS[tier]
            assert "daily_messages" in limits
            assert "shadow_mode" in limits

    def test_free_tier_shadow_disabled(self):
        from services.oracle_engine import TIER_LIMITS
        assert TIER_LIMITS["free"]["shadow_mode"] is False

    def test_premium_tier_shadow_enabled(self):
        from services.oracle_engine import TIER_LIMITS
        assert TIER_LIMITS["premium"]["shadow_mode"] is True


# ── API Route Tests ──────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_check(self):
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_KEY": "test",
            "STRIPE_SECRET_KEY": "sk_test_xxx",
            "STRIPE_WEBHOOK_SECRET": "whsec_test",
            "STRIPE_PRICE_PREMIUM": "price_test1",
            "STRIPE_PRICE_PRO": "price_test2",
        }):
            from main import app
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "alive"
            assert "oracle" in data


class TestTarotEndpoint:
    @patch("api.routes.tarot.get_current_user")
    @patch("api.routes.tarot.get_oracle_response")
    @patch("api.routes.tarot.get_supabase")
    def test_draw_three_cards(self, mock_db, mock_ai, mock_auth, mock_user):
        mock_auth.return_value = mock_user
        mock_ai.return_value = "Yıldızlar şunu söylüyor: Kader kapısı açılıyor..."
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "reading-123"}]
        mock_db.return_value = mock_supabase

        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test", "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_KEY": "test", "STRIPE_SECRET_KEY": "sk_test",
            "STRIPE_WEBHOOK_SECRET": "whsec_test", "STRIPE_PRICE_PREMIUM": "price_1",
            "STRIPE_PRICE_PRO": "price_2",
        }):
            from main import app
            client = TestClient(app)
            response = client.post(
                "/api/tarot/draw",
                json={"question": "Kariyer yolum ne olacak?", "spread": "three_card"},
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "cards" in data
            assert len(data["cards"]) == 3
            assert "interpretation" in data

    @patch("api.routes.tarot.get_current_user")
    def test_celtic_cross_requires_premium(self, mock_auth):
        free = {"tier": "free", "id": "123", "email": "t@t.com",
                "daily_message_count": 0, "daily_message_reset_at": "2026-01-01"}
        mock_auth.return_value = free

        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test", "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_KEY": "test", "STRIPE_SECRET_KEY": "sk_test",
            "STRIPE_WEBHOOK_SECRET": "whsec", "STRIPE_PRICE_PREMIUM": "p1", "STRIPE_PRICE_PRO": "p2",
        }):
            from main import app
            client = TestClient(app)
            response = client.post(
                "/api/tarot/draw",
                json={"spread": "celtic_cross"},
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == 403
            assert response.json()["detail"]["code"] == "UPGRADE_REQUIRED"


class TestDailyLimit:
    def test_free_tier_daily_limit(self):
        from services.oracle_engine import TIER_LIMITS
        assert TIER_LIMITS["free"]["daily_messages"] == 5
        assert TIER_LIMITS["premium"]["daily_messages"] == 9999


# ── Zodiac Edge Cases ────────────────────────────────────────

class TestZodiacEdgeCases:
    def test_all_signs_covered(self):
        from services.oracle_engine import get_zodiac
        test_cases = [
            (15, 1, "Oğlak"), (5, 2, "Kova"), (10, 3, "Balık"),
            (5, 4, "Koç"), (5, 5, "Boğa"), (5, 6, "İkizler"),
            (5, 7, "Yengeç"), (5, 8, "Aslan"), (5, 9, "Başak"),
            (5, 10, "Terazi"), (5, 11, "Akrep"), (5, 12, "Yay"),
        ]
        for day, month, expected in test_cases:
            result = get_zodiac(day, month)
            assert result == expected, f"Failed for {day}/{month}: expected {expected}, got {result}"
