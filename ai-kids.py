import streamlit as st
import anthropic
from dotenv import load_dotenv
import os
from supabase import create_client
import uuid
import stripe

load_dotenv()

client = anthropic.Anthropic()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

STRIPE_FREE_PRICE_ID = os.getenv("STRIPE_FREE_PRICE_ID")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID")
STRIPE_FAMILY_PRICE_ID = os.getenv("STRIPE_FAMILY_PRICE_ID")

supabase_admin = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SECRET_KEY")
)
supabase_auth = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

st.set_page_config(
    page_title="AI-Kids | Cozmo",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
    .stApp { background-color: #0f0f1a; color: #ffffff; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; color: #ffffff; }
    h1 { color: #a855f7; }
    h2 { color: #a855f7; }
    h3 { color: #ffffff; }
    p { color: #ffffff; }
    label { color: #ffffff !important; }
    [data-testid="stChatMessage"] p { color: #ffffff !important; font-size: 16px !important; }
    .stChatInputContainer { border-top: 1px solid #2d2d4e; }
    .stTextInput input { background-color: #1a1a2e; color: #ffffff; border: 1px solid #a855f7; }
    .stButton button { background-color: #a855f7; color: #ffffff; border: none; border-radius: 8px; }
    .stNumberInput input { background-color: #1a1a2e; color: #ffffff; border: 1px solid #a855f7; }

    /* Onboarding */
    .onboarding-card {
        background: rgba(124, 58, 237, 0.08);
        border: 1px solid rgba(167, 139, 250, 0.25);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .plan-card {
        background: rgba(124, 58, 237, 0.08);
        border: 2px solid rgba(167, 139, 250, 0.2);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        cursor: pointer;
        transition: border-color 0.2s;
    }
    .plan-card.selected {
        border-color: #a855f7;
        background: rgba(124, 58, 237, 0.2);
    }
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
        font-size: 0.85rem;
        color: #9ca3af;
    }
    .step-dot {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .step-dot.active { background: #a855f7; color: white; }
    .step-dot.done { background: #22d3ee; color: #0f0f1a; }
    .step-dot.inactive { background: #2d2d4e; color: #9ca3af; }
    .step-line { flex: 1; height: 1px; background: #2d2d4e; }
    .step-line.done { background: #22d3ee; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "child" not in st.session_state:
    st.session_state.child = None
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 1

PLAN_LIMITS = {
    "free": 1,
    "pro": 3,
    "family": 10
}

# ── HELPERS ────────────────────────────────────────────────────
def get_profile(user_id):
    res = supabase_admin.table("profiles").select("*").eq("id", user_id).single().execute()
    return res.data

def get_subscription(user_id):
    profile = get_profile(user_id)
    return profile.get("subscription", "free") if profile else "free"

def get_children_count(user_id):
    res = supabase_admin.table("children").select("id").eq("parent_id", user_id).execute()
    return len(res.data)

def can_add_child(user_id):
    subscription = get_subscription(user_id)
    limit = PLAN_LIMITS.get(subscription, 1)
    count = get_children_count(user_id)
    return count < limit, subscription, limit, count

def is_new_user(user_id):
    """Prüft ob der User noch kein Kind hat → Onboarding nötig"""
    count = get_children_count(user_id)
    return count == 0

def create_checkout_session(user_id, email, price_id, plan_name):
    try:
        profile = get_profile(user_id)
        customer_id = profile.get("stripe_customer_id") if profile else None

        if not customer_id:
            customer = stripe.Customer.create(email=email)
            customer_id = customer.id
            supabase_admin.table("profiles").update({
                "stripe_customer_id": customer_id
            }).eq("id", user_id).execute()

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url="http://localhost:8501?success=true&plan=" + plan_name,
            cancel_url="http://localhost:8501?cancelled=true",
        )
        return session.url
    except Exception as e:
        st.error(f"Stripe Fehler: {e}")
        return None

def upgrade_subscription(user_id, plan):
    supabase_admin.table("profiles").update({
        "subscription": plan
    }).eq("id", user_id).execute()

def render_steps(current_step):
    steps = ["Willkommen", "Dein Kind", "Plan wählen"]
    cols = st.columns(len(steps) * 2 - 1)
    for i, label in enumerate(steps):
        col_idx = i * 2
        step_num = i + 1
        if step_num < current_step:
            dot_class = "done"
            dot_content = "✓"
        elif step_num == current_step:
            dot_class = "active"
            dot_content = str(step_num)
        else:
            dot_class = "inactive"
            dot_content = str(step_num)

        with cols[col_idx]:
            st.markdown(
                f'<div style="text-align:center">'
                f'<div class="step-dot {dot_class}" style="margin:0 auto 4px;">{dot_content}</div>'
                f'<div style="font-size:0.7rem;color:#9ca3af">{label}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        if i < len(steps) - 1:
            line_class = "done" if current_step > step_num else ""
            with cols[col_idx + 1]:
                st.markdown(
                    f'<div class="step-line {line_class}" style="margin-top:14px"></div>',
                    unsafe_allow_html=True
                )

# ── ONBOARDING ─────────────────────────────────────────────────
def show_onboarding():
    step = st.session_state.onboarding_step

    st.markdown("<br>", unsafe_allow_html=True)
    render_steps(step)
    st.markdown("<br>", unsafe_allow_html=True)

    # STEP 1: Willkommen
    if step == 1:
        st.markdown("## 👋 Herzlich willkommen bei AI-Kids!")
        st.markdown("""
        <div class="onboarding-card">
            <h3 style="margin-bottom:0.5rem">🤖 Ich bin Cozmo – dein KI-Lernfreund!</h3>
            <p style="color:#c4b5fd;line-height:1.7">
            Ich bin kein gewöhnlicher Chatbot. Ich stelle Fragen statt Antworten zu geben –
            damit dein Kind wirklich <strong>selbst denkt und versteht</strong>.<br><br>
            Das Sokrates-Prinzip: Durch die richtigen Fragen zum echten Verstehen.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Was dich erwartet:**")
        st.markdown("""
        - 📚 **Lern-Buddy** – Schulthemen spielerisch erklären
        - 🧠 **Denk-Trainer** – Logik und Kreativität
        - 💻 **Code-Kids** – Erstes Programmieren
        - 🎨 **Kreativ-Lab** – Schreiben und Erfinden
        - 🧩 **Löse-Arena** – Knifflige Rätsel
        - 🎯 **Fokus-Lab** – Konzentrations-Übungen
        - ✏️ **Hausaufgaben-Held** – Mit Cozmo, nicht abschreiben
        """)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Los geht's! →", use_container_width=True):
            st.session_state.onboarding_step = 2
            st.rerun()

    # STEP 2: Kind anlegen
    elif step == 2:
        st.markdown("## 👦 Wie heißt dein Kind?")
        st.markdown("Cozmo passt seine Sprache und Erklärungen automatisch ans Alter an.")
        st.markdown("<br>", unsafe_allow_html=True)

        name = st.text_input("Name deines Kindes", placeholder="z.B. Lena", key="onb_name")
        age = st.number_input("Alter", min_value=6, max_value=14, value=9, key="onb_age")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("← Zurück"):
                st.session_state.onboarding_step = 1
                st.rerun()
        with col2:
            if st.button("Weiter →", use_container_width=True):
                if name.strip():
                    # Kind in DB speichern
                    new_child = supabase_admin.table("children").insert({
                        "parent_id": st.session_state.user.id,
                        "name": name.strip(),
                        "age": int(age)
                    }).execute()
                    st.session_state.child = new_child.data[0]
                    st.session_state.onboarding_step = 3
                    st.rerun()
                else:
                    st.warning("Bitte gib einen Namen ein.")

    # STEP 3: Plan wählen
    elif step == 3:
        child_name = st.session_state.child["name"] if st.session_state.child else "dein Kind"
        st.markdown(f"## 🚀 Welchen Plan möchtest du für {child_name}?")
        st.markdown("Du kannst jederzeit upgraden oder kündigen.")
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="onboarding-card" style="text-align:center;min-height:220px">
                <div style="font-size:1.8rem;margin-bottom:0.5rem">🆓</div>
                <div style="font-weight:800;font-size:1.1rem;color:#a78bfa">Free</div>
                <div style="font-size:1.6rem;font-weight:900;margin:0.3rem 0">0€</div>
                <div style="color:#9ca3af;font-size:0.8rem;margin-bottom:0.75rem">pro Monat</div>
                <div style="color:#c4b5fd;font-size:0.82rem;text-align:left">
                ✓ 1 Kind-Profil<br>
                ✓ Alle Module (begrenzt)<br>
                ✓ 10 Fragen/Tag
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Free starten", use_container_width=True, key="plan_free"):
                # Free Plan → direkt in den Chat
                st.session_state.page = "chat"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.session_state.onboarding_step = 1
                st.rerun()

        with col2:
            st.markdown("""
            <div class="onboarding-card" style="text-align:center;min-height:220px;border-color:#a855f7;background:rgba(124,58,237,0.18)">
                <div style="font-size:0.7rem;font-weight:700;color:#22d3ee;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem">⭐ Empfohlen</div>
                <div style="font-weight:800;font-size:1.1rem;color:#a78bfa">Pro</div>
                <div style="font-size:1.6rem;font-weight:900;margin:0.3rem 0">9,99€</div>
                <div style="color:#9ca3af;font-size:0.8rem;margin-bottom:0.75rem">pro Monat</div>
                <div style="color:#c4b5fd;font-size:0.82rem;text-align:left">
                ✓ 1 Kind-Profil<br>
                ✓ Alle Module unlimitiert<br>
                ✓ Lernstatistiken<br>
                ✓ Eltern-Dashboard
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Pro wählen ⭐", use_container_width=True, key="plan_pro"):
                url = create_checkout_session(
                    st.session_state.user.id,
                    st.session_state.user.email,
                    STRIPE_PRO_PRICE_ID,
                    "pro"
                )
                if url:
                    st.markdown(f"[➡️ Jetzt zu Stripe]({url})")

        with col3:
            st.markdown("""
            <div class="onboarding-card" style="text-align:center;min-height:220px">
                <div style="font-size:1.8rem;margin-bottom:0.5rem">👨‍👩‍👧</div>
                <div style="font-weight:800;font-size:1.1rem;color:#a78bfa">Family</div>
                <div style="font-size:1.6rem;font-weight:900;margin:0.3rem 0">14,99€</div>
                <div style="color:#9ca3af;font-size:0.8rem;margin-bottom:0.75rem">pro Monat</div>
                <div style="color:#c4b5fd;font-size:0.82rem;text-align:left">
                ✓ Bis zu 4 Kinder<br>
                ✓ Alle Module unlimitiert<br>
                ✓ Individuelle Profile<br>
                ✓ Eltern-Dashboard
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Family wählen", use_container_width=True, key="plan_family"):
                url = create_checkout_session(
                    st.session_state.user.id,
                    st.session_state.user.email,
                    STRIPE_FAMILY_PRICE_ID,
                    "family"
                )
                if url:
                    st.markdown(f"[➡️ Jetzt zu Stripe]({url})")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, _ = st.columns([1, 3])
        with col1:
            if st.button("← Zurück"):
                # Kind wieder löschen wenn zurück
                if st.session_state.child:
                    supabase_admin.table("children").delete().eq("id", st.session_state.child["id"]).execute()
                    st.session_state.child = None
                st.session_state.onboarding_step = 2
                st.rerun()

# ── LOGIN / REGISTRIERUNG ──────────────────────────────────────
def show_auth():
    st.title("🤖 AI-Kids")
    st.markdown("### Eltern-Bereich")
    st.divider()

    tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])

    with tab1:
        email = st.text_input("E-Mail", key="login_email")
        password = st.text_input("Passwort", type="password", key="login_password")
        if st.button("Anmelden"):
            try:
                res = supabase_auth.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = res.user
                # Prüfen ob Onboarding nötig
                if is_new_user(res.user.id):
                    st.session_state.page = "onboarding"
                    st.session_state.onboarding_step = 1
                else:
                    st.session_state.page = "dashboard"
                st.rerun()
            except Exception as e:
                st.error(f"Fehler: {e}")

    with tab2:
        email = st.text_input("E-Mail", key="reg_email")
        password = st.text_input("Passwort (min. 6 Zeichen)", type="password", key="reg_password")
        if st.button("Registrieren"):
            try:
                res = supabase_auth.auth.sign_up({
                    "email": email,
                    "password": password
                })
                supabase_admin.table("profiles").insert({
                    "id": res.user.id,
                    "email": email,
                    "role": "parent",
                    "subscription": "free"
                }).execute()
                # Direkt einloggen und Onboarding starten
                st.session_state.user = res.user
                st.session_state.page = "onboarding"
                st.session_state.onboarding_step = 1
                st.rerun()
            except Exception as e:
                st.error(f"Fehler: {e}")

# ── ELTERN-DASHBOARD ───────────────────────────────────────────
def show_dashboard():
    st.title("📊 Eltern-Dashboard")
    st.markdown(f"Eingeloggt als: **{st.session_state.user.email}**")

    subscription = get_subscription(st.session_state.user.id)
    plan_badge = {"free": "🆓 Free", "pro": "⭐ Pro", "family": "👨‍👩‍👧 Family"}
    st.markdown(f"**Aktueller Plan:** {plan_badge.get(subscription, '🆓 Free')}")

    # URL Parameter prüfen (nach Stripe Checkout)
    params = st.query_params
    if "success" in params:
        plan = params.get("plan", "pro")
        upgrade_subscription(st.session_state.user.id, plan)
        st.success(f"✅ Upgrade auf {plan.capitalize()} erfolgreich!")
        st.query_params.clear()
        st.rerun()
    if "cancelled" in params:
        st.warning("Zahlung abgebrochen.")
        st.query_params.clear()

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🤖 Cozmo starten"):
            st.session_state.page = "child_select"
            st.rerun()
    with col2:
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.session_state.child = None
            st.rerun()

    if subscription == "free":
        st.divider()
        st.markdown("### 🚀 Upgrade")
        st.markdown("Schalte mehr Kinderprofile und Features frei!")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⭐ Pro — 9,99€/Monat")
            st.markdown("- Bis zu 3 Kinder\n- Alle Lernmodule\n- Chat-Verlauf")
            if st.button("Pro wählen"):
                url = create_checkout_session(
                    st.session_state.user.id,
                    st.session_state.user.email,
                    STRIPE_PRO_PRICE_ID,
                    "pro"
                )
                if url:
                    st.markdown(f"[➡️ Jetzt upgraden]({url})")

        with col2:
            st.markdown("#### 👨‍👩‍👧 Family — 14,99€/Monat")
            st.markdown("- Bis zu 10 Kinder\n- Alle Features\n- Priorität-Support")
            if st.button("Family wählen"):
                url = create_checkout_session(
                    st.session_state.user.id,
                    st.session_state.user.email,
                    STRIPE_FAMILY_PRICE_ID,
                    "family"
                )
                if url:
                    st.markdown(f"[➡️ Jetzt upgraden]({url})")

    st.divider()
    st.markdown("### 💬 Chat-Sessions")

    sessions = supabase_admin.table("chat_sessions")\
        .select("*, children(name)")\
        .order("started_at", desc=True)\
        .execute()

    if not sessions.data:
        st.info("Noch keine Chat-Sessions vorhanden.")
        return

    for session in sessions.data:
        session_id = session["id"]
        started = session["started_at"][:16].replace("T", " ")
        child_name = session["children"]["name"] if session.get("children") else "Unbekannt"

        msgs = supabase_admin.table("messages")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at")\
            .execute()

        user_msgs = [m for m in msgs.data if m["role"] == "user"]
        msg_count = len(user_msgs)

        with st.expander(f"👦 {child_name} — 📅 {started} — {msg_count} Fragen"):
            for msg in msgs.data:
                if msg["role"] == "user":
                    st.markdown(f"👦 **{child_name}:** {msg['content']}")
                else:
                    st.markdown(f"🤖 **Cozmo:** {msg['content']}")
                st.divider()

# ── KIND AUSWÄHLEN / ANLEGEN ───────────────────────────────────
def show_child_select():
    st.title("👦 Kind-Profil")
    st.markdown("### Wer chattet heute mit Cozmo?")
    st.divider()

    children = supabase_admin.table("children")\
        .select("*")\
        .eq("parent_id", st.session_state.user.id)\
        .execute()

    if children.data:
        st.markdown("#### Vorhandene Kinder:")
        for child in children.data:
            if st.button(f"👦 {child['name']} ({child['age']} Jahre)", key=child["id"]):
                st.session_state.child = child
                st.session_state.page = "chat"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.rerun()

        st.divider()

    allowed, subscription, limit, count = can_add_child(st.session_state.user.id)

    st.markdown("#### Neues Kind hinzufügen:")

    if not allowed:
        st.warning(f"⚠️ Dein **{subscription.capitalize()}**-Plan erlaubt max. {limit} Kind(er). Du hast bereits {count}.")
        st.info("👉 Upgrade im Dashboard um mehr Kinder hinzuzufügen.")
    else:
        st.markdown(f"*{count}/{limit} Kinder-Slots genutzt*")
        name = st.text_input("Name des Kindes")
        age = st.number_input("Alter", min_value=6, max_value=14, value=9)

        if st.button("➕ Hinzufügen & starten"):
            if name:
                new_child = supabase_admin.table("children").insert({
                    "parent_id": st.session_state.user.id,
                    "name": name,
                    "age": int(age)
                }).execute()
                st.session_state.child = new_child.data[0]
                st.session_state.page = "chat"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.rerun()
            else:
                st.warning("Bitte Namen eingeben.")

    if st.button("← Zurück"):
        st.session_state.page = "dashboard"
        st.rerun()

# ── COZMO CHAT ─────────────────────────────────────────────────
def show_chat():
    child_name = st.session_state.child["name"] if st.session_state.child else "du"
    child_age = st.session_state.child["age"] if st.session_state.child else 10

    st.title("🤖 Cozmo")
    st.markdown(f"### Hallo {child_name}! Bereit zum Lernen?")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("← Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

    st.divider()

    if "session_id" not in st.session_state or st.session_state.session_id is None:
        st.session_state.session_id = str(uuid.uuid4())
        child_id = st.session_state.child["id"] if st.session_state.child else None
        supabase_admin.table("chat_sessions").insert({
            "id": st.session_state.session_id,
            "child_id": child_id
        }).execute()

    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = []
        welcome = f"Hey {child_name}! 👋 Ich bin Cozmo – dein Lernbegleiter. Ich helfe dir beim Denken, nicht beim Abschreiben 😄 Was möchtest du heute lernen?"
        st.session_state.messages.append({"role": "assistant", "content": welcome})
        supabase_admin.table("messages").insert({
            "session_id": st.session_state.session_id,
            "role": "assistant",
            "content": welcome
        }).execute()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Stell mir eine Frage..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        supabase_admin.table("messages").insert({
            "session_id": st.session_state.session_id,
            "role": "user",
            "content": prompt
        }).execute()

        with st.chat_message("assistant"):
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=f"""Du bist Cozmo, ein freundlicher KI-Lernbegleiter für Kinder von AI-Kids.
                Du sprichst mit {child_name}, {child_age} Jahre alt.
                Passe deine Sprache dem Alter an — einfach, klar und ermutigend.
                Du gibst KEINE direkten Antworten, sondern stellst Gegenfragen die das Kind zum Denken bringen.
                Das ist das Sokrates-Prinzip.
                Halte Antworten kurz – maximal 3 Sätze.
                Sprich {child_name} manchmal direkt mit dem Namen an.""",
                messages=st.session_state.messages
            )
            answer = response.content[0].text
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        supabase_admin.table("messages").insert({
            "session_id": st.session_state.session_id,
            "role": "assistant",
            "content": answer
        }).execute()

# ── ROUTING ────────────────────────────────────────────────────
if st.session_state.user is None:
    show_auth()
elif st.session_state.page == "onboarding":
    show_onboarding()
elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "child_select":
    show_child_select()
elif st.session_state.page == "chat":
    show_chat()