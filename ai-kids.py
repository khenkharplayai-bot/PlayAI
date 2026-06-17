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

AIKIDS_LOGO = "data:image/png;base64,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"
PLAYAI_LOGO = "data:image/png;base64,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"

COZMO_AVATAR = "PASTE_BASE64_HERE"

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
    .stApp { background-color: #0f0c1e; color: #ffffff; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; color: #ffffff; }
    h1 { color: #a855f7; }
    h2 { color: #a855f7; }
    h3 { color: #ffffff; }
    p { color: #ffffff; }
    label { color: #ffffff !important; }
    [data-testid="stChatMessage"] p { color: #ffffff !important; font-size: 16px !important; }
    [data-testid="stChatMessage"] li { color: #ffffff !important; font-size: 16px !important; }
    [data-testid="stChatMessage"] ol { color: #ffffff !important; }
    [data-testid="stChatMessage"] * { color: #ffffff !important; }
    .stChatInputContainer { border-top: 1px solid #2d2d4e; }
    .stTextInput input { background-color: #1a1a2e; color: #ffffff; border: 1px solid #a855f7; }
    .stButton button { background-color: #a855f7; color: #ffffff; border: none; border-radius: 8px; }
    .stNumberInput input { background-color: #1a1a2e; color: #ffffff; border: 1px solid #a855f7; }

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

    .module-card {
        background: rgba(124, 58, 237, 0.08);
        border: 2px solid rgba(167, 139, 250, 0.2);
        border-radius: 16px;
        padding: 1.2rem 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 0.5rem;
        min-height: 130px;
    }
    .module-card:hover {
        border-color: #a855f7;
        background: rgba(124, 58, 237, 0.18);
    }
    .module-card .module-icon { font-size: 2rem; margin-bottom: 0.4rem; }
    .module-card .module-name { font-weight: 700; color: #a78bfa; font-size: 0.95rem; }
    .module-card .module-desc { color: #9ca3af; font-size: 0.78rem; margin-top: 0.2rem; }

    .module-badge {
        display: inline-block;
        background: rgba(124, 58, 237, 0.25);
        border: 1px solid #a855f7;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.8rem;
        color: #c4b5fd;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── MODULE DEFINITION ──────────────────────────────────────────
MODULES = [
    {
        "id": "lern_buddy",
        "icon": "📚",
        "name": "Lern-Buddy",
        "desc": "Schulthemen spielerisch erklären",
        "prompt": """Du hilfst dem Kind, Schulthemen zu verstehen — Mathe, Deutsch, Sachkunde, Geschichte, Englisch etc.
        Du gibst KEINE direkten Antworten. Stattdessen fragst du zurück, was das Kind bereits weiß,
        und führst es Schritt für Schritt mit Fragen zur Antwort.
        Wenn das Kind z.B. fragt "Wie viel ist 7x8?", fragst du "Weißt du, wie Multiplikation funktioniert?"
        oder "Was wäre 7x4, und wie könntest du daraus 7x8 berechnen?" — niemals "56".
        Bleib geduldig, locker und ermutigend."""
    },
    {
        "id": "denk_trainer",
        "icon": "🧠",
        "name": "Denk-Trainer",
        "desc": "Logik, Kreativität & Querdenken",
        "prompt": """Du trainierst das logische und kreative Denken des Kindes.
        Du stellst Rätsel, Denksport-Fragen und fordere es heraus, aus der Box zu denken.
        Stell immer Folgefragen: "Warum denkst du das?", "Gibt es noch einen anderen Weg?", "Was würde passieren wenn...?"
        Lob gutes Denken, nicht nur richtige Antworten. Der Denkprozess ist das Ziel."""
    },
    {
        "id": "code_kids",
        "icon": "💻",
        "name": "Code-Kids",
        "desc": "Erste Schritte im Programmieren",
        "prompt": """Du bringst dem Kind Programmieren bei — Scratch, Python-Basics, logisches Denken in Code.
        Erkläre alles mit einfachen Alltagsbeispielen (Rezepte = Algorithmen, Lichtschalter = if/else).
        Gib KEINEN fertigen Code. Frag stattdessen: "Was muss der Computer als erstes wissen?"
        "Wenn du ein Roboter wärst, wie würdest du Schritt für Schritt vorgehen?"
        Mach es spielerisch und zeig, dass Fehler normal sind ("Debugging ist wie Detektivarbeit!")."""
    },
    {
        "id": "kreativ_lab",
        "icon": "🎨",
        "name": "Kreativ-Lab",
        "desc": "Schreiben, Erfinden & Geschichten",
        "prompt": """Du bist der kreative Begleiter — Geschichten schreiben, Welten erfinden, Texte gestalten.
        Schreib KEINE Geschichten für das Kind. Hilf ihm stattdessen mit Fragen:
        "Wie könnte deine Figur aussehen?", "Was wäre das spannendste Problem für deinen Helden?"
        "Was passiert als nächstes — was denkst du?" Begeistere für kreatives Schreiben.
        Locker, spielerisch, inspirierend."""
    },
    {
        "id": "loese_arena",
        "icon": "🧩",
        "name": "Löse-Arena",
        "desc": "Knifflige Rätsel & Herausforderungen",
        "prompt": """Du bist der Rätsel-Meister. Du stellst dem Kind knifflige Rätsel, Logikaufgaben und Denksport.
        Beim Lösen gibst du KEINE Lösung — du gibst Hinweise in Form von Fragen:
        "Was weißt du schon sicher?", "Welche Möglichkeiten gibt es?", "Was kannst du ausschließen?"
        Steigere den Schwierigkeitsgrad langsam. Feiere jeden Fortschritt mit Begeisterung."""
    },
    {
        "id": "fokus_lab",
        "icon": "🎯",
        "name": "Fokus-Lab",
        "desc": "Konzentration & Lernorganisation",
        "prompt": """Du hilfst dem Kind, fokussiert und organisiert zu lernen.
        Themen: Lernplanung, Konzentrationstipps, Pausen-Strategien, Gedächtnistricks.
        Frag zuerst: "Was willst du heute schaffen?" und "Wie lange hast du Zeit?"
        Dann führe durch kleine Schritte. Erkläre Techniken wie Pomodoro kindgerecht.
        Ruhig, strukturiert, motivierend."""
    },
    {
        "id": "hausaufgaben_held",
        "icon": "✏️",
        "name": "Hausaufgaben-Held",
        "desc": "Hausaufgaben verstehen — nicht abschreiben",
        "prompt": """Du hilfst dem Kind, Hausaufgaben SELBST zu lösen — nicht indem du sie erledigst.
        Bei jeder Aufgabe fragst du zuerst: "Was hast du schon versucht?" und "Was verstehst du noch nicht genau?"
        Dann führst du mit gezielten Fragen durch den Lösungsweg.
        NIEMALS die fertige Antwort geben. Immer den letzten Schritt dem Kind überlassen.
        Extra geduldig, ermutigend, schulmäßig klar."""
    }
]

# ── SESSION STATE ──────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "child" not in st.session_state:
    st.session_state.child = None
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 1
if "active_module" not in st.session_state:
    st.session_state.active_module = None

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
            success_url="https://ai-kids.streamlit.app/?success=true&plan=pro",
            cancel_url="https://ai-kids.streamlit.app/?cancelled=true",
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

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<img src="{AIKIDS_LOGO}" width="100" style="display:block;margin:0 auto">', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    render_steps(step)
    st.markdown("<br>", unsafe_allow_html=True)

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
                ✓ 1 Kind-Profil<br>✓ Alle Module (begrenzt)<br>✓ 10 Fragen/Tag
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Free starten", use_container_width=True, key="plan_free"):
                st.session_state.page = "module_select"
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
                ✓ 1 Kind-Profil<br>✓ Alle Module unlimitiert<br>✓ Lernstatistiken<br>✓ Eltern-Dashboard
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
                ✓ Bis zu 4 Kinder<br>✓ Alle Module unlimitiert<br>✓ Individuelle Profile<br>✓ Eltern-Dashboard
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
                if st.session_state.child:
                    supabase_admin.table("children").delete().eq("id", st.session_state.child["id"]).execute()
                    st.session_state.child = None
                st.session_state.onboarding_step = 2
                st.rerun()

# ── LOGIN / REGISTRIERUNG ──────────────────────────────────────
def show_auth():
    st.markdown(f"""
    <div style="text-align:center;padding:1.5rem 0 1rem 0">
        <img src="{AIKIDS_LOGO}" width="110" style="margin-bottom:8px">
        <div style="font-size:2rem;font-weight:900;color:#a855f7;line-height:1.1">AI-Kids</div>
        <div style="font-size:1rem;color:#9ca3af;margin-top:6px">Eltern-Bereich</div>
    </div>
    """, unsafe_allow_html=True)
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
                st.session_state.user = res.user
                st.session_state.page = "onboarding"
                st.session_state.onboarding_step = 1
                st.rerun()
            except Exception as e:
                st.error(f"Fehler: {e}")

    st.markdown(f"""
    <div style="text-align:center;padding:2rem 0 1rem 0">
        <img src="{PLAYAI_LOGO}" width="110" style="margin-bottom:8px">
        <div style="font-size:1rem;color:#9ca3af;margin-top:6px">by PlayAI</div>
    </div>
    """, unsafe_allow_html=True)

# ── ELTERN-DASHBOARD ───────────────────────────────────────────
def show_dashboard():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📊 Eltern-Dashboard")
    with col2:
        st.markdown(f'<img src="{PLAYAI_LOGO}" width="70" >', unsafe_allow_html=True)

    st.markdown(f"Eingeloggt als: **{st.session_state.user.email}**")

    subscription = get_subscription(st.session_state.user.id)
    plan_badge = {"free": "🆓 Free", "pro": "⭐ Pro", "family": "👨‍👩‍👧 Family"}
    st.markdown(f"**Aktueller Plan:** {plan_badge.get(subscription, '🆓 Free')}")

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
            st.session_state.active_module = None
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
        module_name = session.get("module_name", "")
        module_label = f" — {module_name}" if module_name else ""

        msgs = supabase_admin.table("messages")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at")\
            .execute()

        user_msgs = [m for m in msgs.data if m["role"] == "user"]
        msg_count = len(user_msgs)

        with st.expander(f"👦 {child_name}{module_label} — 📅 {started} — {msg_count} Fragen"):
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
                st.session_state.page = "module_select"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.session_state.active_module = None
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
                st.session_state.page = "module_select"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.session_state.active_module = None
                st.rerun()
            else:
                st.warning("Bitte Namen eingeben.")

    if st.button("← Zurück"):
        st.session_state.page = "dashboard"
        st.rerun()

# ── MODUL-AUSWAHL ──────────────────────────────────────────────
def show_module_select():
    import random
    child_name = st.session_state.child["name"] if st.session_state.child else "du"

    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown(f'<img src="{AIKIDS_LOGO}" width="60">', unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h2 style='text-align:center;color:#a855f7;margin-bottom:0'>Hey {child_name}! 👋</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#9ca3af;margin-top:0'>Was möchtest du heute mit Cozmo machen?</p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back"):
            st.session_state.page = "child_select"
            st.rerun()

    st.divider()

    # Zufällig 1 Modul featuren, Rest symmetrisch 2-spaltig
    if "featured_module_idx" not in st.session_state:
        st.session_state.featured_module_idx = random.randint(0, len(MODULES) - 1)

    featured_idx = st.session_state.featured_module_idx
    featured = MODULES[featured_idx]
    others = [m for i, m in enumerate(MODULES) if i != featured_idx]

    # Featured Modul — volle Breite, hervorgehoben
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(124,58,237,0.35),rgba(168,85,247,0.15));
         border:2px solid #a855f7;border-radius:20px;padding:1.5rem;text-align:center;margin-bottom:0.5rem">
        <div style="font-size:0.7rem;font-weight:700;color:#22d3ee;letter-spacing:0.12em;
             text-transform:uppercase;margin-bottom:0.5rem">✨ Heute empfohlen</div>
        <div style="font-size:3rem;margin-bottom:0.4rem">{featured['icon']}</div>
        <div style="font-weight:800;font-size:1.3rem;color:#a855f7;margin-bottom:0.3rem">{featured['name']}</div>
        <div style="color:#c4b5fd;font-size:0.9rem">{featured['desc']}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"{featured['icon']} Jetzt starten", key=f"mod_{featured['id']}", use_container_width=True):
        st.session_state.active_module = featured
        st.session_state.page = "chat"
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9ca3af;font-size:0.85rem;margin-bottom:0.5rem'>Oder wähle ein anderes Modul:</p>", unsafe_allow_html=True)

    # Restliche 6 Module — 2-spaltig symmetrisch
    for i in range(0, len(others), 2):
        col1, col2 = st.columns(2)
        for j, col in enumerate([col1, col2]):
            idx = i + j
            if idx < len(others):
                mod = others[idx]
                with col:
                    st.markdown(f"""
                    <div class="module-card">
                        <div class="module-icon">{mod['icon']}</div>
                        <div class="module-name">{mod['name']}</div>
                        <div class="module-desc">{mod['desc']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"{mod['icon']} Starten", key=f"mod_{mod['id']}", use_container_width=True):
                        st.session_state.active_module = mod
                        st.session_state.page = "chat"
                        st.session_state.messages = []
                        st.session_state.session_id = None
                        st.rerun()

# ── COZMO CHAT ─────────────────────────────────────────────────
def show_chat():
    child_name = st.session_state.child["name"] if st.session_state.child else "du"
    child_age = st.session_state.child["age"] if st.session_state.child else 10
    module = st.session_state.active_module

    # Header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown(f'<img src="{AIKIDS_LOGO}" width="60">', unsafe_allow_html=True)
    with col2:
        st.markdown("<h2 style='text-align:center;color:#a855f7;margin-bottom:0'>Cozmo</h2>", unsafe_allow_html=True)
        if module:
            st.markdown(
                f"<p style='text-align:center;margin-top:4px'>"
                f"<span class='module-badge'>{module['icon']} {module['name']}</span></p>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"<p style='text-align:center;color:#9ca3af;margin-top:0'>Hallo {child_name}! 🚀</p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Module"):
            st.session_state.page = "module_select"
            st.session_state.messages = []
            st.session_state.session_id = None
            st.session_state.active_module = None
            st.rerun()

    st.divider()

    # Session anlegen
    if "session_id" not in st.session_state or st.session_state.session_id is None:
        st.session_state.session_id = str(uuid.uuid4())
        child_id = st.session_state.child["id"] if st.session_state.child else None
        module_name = module["name"] if module else None
        try:
            supabase_admin.table("chat_sessions").insert({
                "id": st.session_state.session_id,
                "child_id": child_id,
                "module_name": module_name
            }).execute()
        except Exception:
            # Falls module_name Spalte noch nicht existiert
            supabase_admin.table("chat_sessions").insert({
                "id": st.session_state.session_id,
                "child_id": child_id
            }).execute()

    # Begrüßung
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = []
        if module:
            welcome = f"Hey {child_name}! 👋 Ich bin Cozmo. Heute starten wir mit **{module['icon']} {module['name']}**! {module['desc']}. Was willst du angehen?"
        else:
            welcome = f"Hey {child_name}! 👋 Ich bin Cozmo – dein Lernbegleiter. Was möchtest du heute lernen?"
        st.session_state.messages.append({"role": "assistant", "content": welcome})
        supabase_admin.table("messages").insert({
            "session_id": st.session_state.session_id,
            "role": "assistant",
            "content": welcome
        }).execute()

    # CSS: Cozmo Avatar über data URL ins DOM injizieren
    st.markdown(f"""
    <style>
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) img,
    [data-testid="chatAvatarIcon-assistant"] {{
        display: none !important;
    }}
    [data-testid="chatAvatarIcon-assistant"] {{
        background-image: url("{COZMO_AVATAR}") !important;
        background-size: cover !important;
        background-color: transparent !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: block !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    def render_cozmo_msg(text):
        import re
        # Markdown manuell in HTML umwandeln – st.markdown() parst innerhalb von
        # unsafe_allow_html-Blöcken kein verschachteltes Markdown mehr.
        safe_text = text.replace("<", "&lt;").replace(">", "&gt;")
        safe_text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe_text)
        safe_text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", safe_text)
        safe_text = safe_text.replace("\n", "<br>")
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:12px">
            <img src="{COZMO_AVATAR}" width="48" height="48"
                 style="border-radius:50%;flex-shrink:0;object-fit:cover;border:2px solid #a855f7">
            <div style="background:rgba(124,58,237,0.15);border:1px solid rgba(168,85,247,0.3);
                        border-radius:12px;padding:12px 16px;color:#ffffff;font-size:16px;line-height:1.6;
                        max-width:85%">
                {safe_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat-Verlauf
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            render_cozmo_msg(message["content"])
        else:
            with st.chat_message("user"):
                st.markdown(message["content"])

    # Eingabe
    if prompt := st.chat_input("Stell mir eine Frage..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        supabase_admin.table("messages").insert({
            "session_id": st.session_state.session_id,
            "role": "user",
            "content": prompt
        }).execute()

        # System-Prompt zusammenbauen
        base_prompt = f"""Du bist Cozmo, ein freundlicher KI-Lernbegleiter für Kinder von AI-Kids.
Du sprichst mit {child_name}, {child_age} Jahre alt.
Passe deine Sprache dem Alter an — einfach, klar und ermutigend.
Halte Antworten kurz – maximal 3-4 Sätze.
Sprich {child_name} manchmal direkt mit dem Namen an.
"""
        if module:
            system_prompt = base_prompt + "\n\n" + module["prompt"]
        else:
            system_prompt = base_prompt + "\nDu gibst KEINE direkten Antworten, sondern stellst Gegenfragen die das Kind zum Denken bringen. Das ist das Sokrates-Prinzip."

        with st.spinner("Cozmo denkt..."):
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=system_prompt,
                messages=st.session_state.messages
            )
            answer = response.content[0].text

        render_cozmo_msg(answer)

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
elif st.session_state.page == "module_select":
    show_module_select()
elif st.session_state.page == "chat":
    show_chat()
