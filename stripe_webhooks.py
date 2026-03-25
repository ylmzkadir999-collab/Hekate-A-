"""
Stripe Payment Routes
Handles subscription creation, webhook events, customer portal
"""
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional

from core.config import settings
from core.database import get_current_user, get_supabase

stripe.api_key = settings.STRIPE_SECRET_KEY
router = APIRouter()

TIER_PRICES = {
    "premium": settings.STRIPE_PRICE_PREMIUM,
    "pro":     settings.STRIPE_PRICE_PRO,
}

class CheckoutRequest(BaseModel):
    tier: str  # "premium" | "pro"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

# ── Create Checkout Session ──────────────────────────────────

@router.post("/create-checkout")
async def create_checkout(req: CheckoutRequest, user: dict = Depends(get_current_user)):
    if req.tier not in TIER_PRICES:
        raise HTTPException(status_code=400, detail="Invalid tier")

    supabase = get_supabase()

    # Get or create Stripe customer
    customer_id = user.get("stripe_customer_id")
    if not customer_id:
        customer = stripe.Customer.create(
            email=user["email"],
            metadata={"supabase_user_id": user["id"], "name": user.get("full_name", "")}
        )
        customer_id = customer.id
        supabase.table("profiles").update({"stripe_customer_id": customer_id}).eq("id", user["id"]).execute()

    success_url = req.success_url or f"{settings.FRONTEND_URL}/dashboard?upgrade=success&tier={req.tier}"
    cancel_url  = req.cancel_url  or f"{settings.FRONTEND_URL}/pricing?canceled=true"

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": TIER_PRICES[req.tier], "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        subscription_data={"metadata": {"user_id": user["id"], "tier": req.tier}},
        allow_promotion_codes=True,
        billing_address_collection="auto",
    )
    return {"checkout_url": session.url, "session_id": session.id}

# ── Customer Portal ──────────────────────────────────────────

@router.post("/portal")
async def customer_portal(user: dict = Depends(get_current_user)):
    customer_id = user.get("stripe_customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer found")

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{settings.FRONTEND_URL}/dashboard",
    )
    return {"portal_url": session.url}

# ── Webhook Handler ──────────────────────────────────────────

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    supabase = get_supabase()

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        sub_id = session.get("subscription")
        customer_id = session.get("customer")

        if sub_id and customer_id:
            sub = stripe.Subscription.retrieve(sub_id)
            tier = sub.metadata.get("tier", "premium")
            user_id = sub.metadata.get("user_id")

            if user_id:
                _update_user_tier(supabase, user_id, tier, sub_id, sub)

    elif event["type"] in ("customer.subscription.updated", "customer.subscription.deleted"):
        sub = event["data"]["object"]
        user_id = sub.metadata.get("user_id")

        if user_id:
            if event["type"] == "customer.subscription.deleted" or sub["status"] in ("canceled", "unpaid", "past_due"):
                _downgrade_user(supabase, user_id)
            else:
                tier = sub.metadata.get("tier", "premium")
                _update_user_tier(supabase, user_id, tier, sub["id"], sub)

    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        # Log payment
        profile = supabase.table("profiles").select("id").eq("stripe_customer_id", customer_id).single().execute()
        if profile.data:
            supabase.table("payments").insert({
                "user_id": profile.data["id"],
                "stripe_invoice_id": invoice["id"],
                "amount": invoice["amount_paid"],
                "currency": invoice["currency"],
                "status": "succeeded",
                "tier": "premium",
            }).execute()

    return {"received": True}

def _update_user_tier(supabase, user_id: str, tier: str, sub_id: str, sub):
    from datetime import datetime
    supabase.table("profiles").update({
        "tier": tier,
        "stripe_subscription_id": sub_id,
        "subscription_status": sub["status"],
        "subscription_current_period_end": datetime.fromtimestamp(sub["current_period_end"]).isoformat(),
    }).eq("id", user_id).execute()

def _downgrade_user(supabase, user_id: str):
    supabase.table("profiles").update({
        "tier": "free",
        "stripe_subscription_id": None,
        "subscription_status": "canceled",
        "subscription_current_period_end": None,
    }).eq("id", user_id).execute()

# ── Get current subscription status ─────────────────────────

@router.get("/subscription")
async def get_subscription(user: dict = Depends(get_current_user)):
    return {
        "tier": user.get("tier", "free"),
        "status": user.get("subscription_status"),
        "current_period_end": user.get("subscription_current_period_end"),
        "stripe_customer_id": user.get("stripe_customer_id"),
    }
