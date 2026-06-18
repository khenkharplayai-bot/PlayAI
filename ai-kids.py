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
    /* Logos auf #a855f7 einfärben */
    img[src^="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAE"] {
    filter: brightness(0) saturate(100%) invert(44%) sepia(100%) saturate(3000%) hue-rotate(237deg) brightness(100%) !important;
    }
    img[src^="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAD"] {
    filter: brightness(0) saturate(100%) invert(44%) sepia(100%) saturate(3000%) hue-rotate(237deg) brightness(100%) !important;
    }
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
        <div style="display:flex;align-items:center;justify-content:center;gap:4px">
            <img src="{AIKIDS_LOGO}" style="height:3.4rem;width:auto;display:block">
            <span style="font-size:2rem;font-weight:900;color:#a855f7;line-height:1">AI-Kids</span>
        </div>
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
        <div style="display:flex;align-items:center;justify-content:center;gap:4px">
            <img src="{PLAYAI_LOGO}" style="height:1.7rem;width:auto;display:block">
            <span style="font-size:1rem;color:#9ca3af;line-height:1">by PlayAI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── ELTERN-DASHBOARD ───────────────────────────────────────────
def show_dashboard():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📊 Eltern-Dashboard")
    with col2:
        st.markdown(f'<div style="display:flex;align-items:center;height:100%;padding-top:0.5rem"><img src="{PLAYAI_LOGO}" style="height:1.8rem;width:auto"></div>', unsafe_allow_html=True)

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
        st.markdown(f'<div style="display:flex;align-items:center;justify-content:center;height:100%;padding-top:0.3rem"><img src="{AIKIDS_LOGO}" style="height:2.4rem;width:auto"></div>', unsafe_allow_html=True)
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
        st.markdown(f'<div style="display:flex;align-items:center;justify-content:center;height:100%;padding-top:0.3rem"><img src="{AIKIDS_LOGO}" style="height:2.4rem;width:auto"></div>', unsafe_allow_html=True)
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
