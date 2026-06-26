from flask import Flask, request, jsonify
import stripe
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SECRET_KEY")
)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except Exception as e:
        print(f"Webhook Fehler: {e}")
        return jsonify({"error": str(e)}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        print(f"🔍 Customer ID: {customer_id}")
        plan = session.get("metadata", {}).get("plan", "pro")
        
        profile = supabase.table("profiles")\
            .select("id")\
            .eq("stripe_customer_id", customer_id)\
            .execute()
        
        if profile.data and len(profile.data) > 0:
            supabase.table("profiles").update({
                "subscription": plan
            }).eq("id", profile.data[0]["id"]).execute()
            print(f"✅ Upgrade auf {plan} für customer {customer_id}")

    elif event["type"] in ["customer.subscription.deleted", "invoice.payment_failed"]:
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        
        profile = supabase.table("profiles")\
            .select("id")\
            .eq("stripe_customer_id", customer_id)\
            .execute()
        
        if profile.data and len(profile.data) > 0:
            supabase.table("profiles").update({
                "subscription": "free"
            }).eq("id", profile.data["id"]).execute()
            print(f"⬇️ Downgrade auf free für customer {customer_id}")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
   app.run(host="127.0.0.1", port=8502, debug=True)
