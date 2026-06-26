from flask import Flask, request, jsonify
import stripe
import os
from supabase import create_client

app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY", "")

print(f"DEBUG SUPABASE_URL='{SUPABASE_URL[:20] if SUPABASE_URL else 'LEER'}'")
print(f"DEBUG SUPABASE_KEY='{SUPABASE_KEY[:10] if SUPABASE_KEY else 'LEER'}'")

@app.route("/webhook", methods=["POST"])
def webhook():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        plan = session.get("metadata", {}).get("plan", "pro")
        profile = supabase.table("profiles").select("id").eq("stripe_customer_id", customer_id).execute()
        if profile.data and len(profile.data) > 0:
            supabase.table("profiles").update({"subscription": plan}).eq("id", profile.data[0]["id"]).execute()
    elif event["type"] in ["customer.subscription.deleted", "invoice.payment_failed"]:
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        profile = supabase.table("profiles").select("id").eq("stripe_customer_id", customer_id).execute()
        if profile.data and len(profile.data) > 0:
            supabase.table("profiles").update({"subscription": "free"}).eq("id", profile.data[0]["id"]).execute()
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8502)))
