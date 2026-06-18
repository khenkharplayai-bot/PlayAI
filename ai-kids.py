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

AIKIDS_LOGO = "https://raw.githubusercontent.com/khenkharplayai-bot/PlayAI/main/aikids_logo.png"
PLAYAI_LOGO = "https://raw.githubusercontent.com/khenkharplayai-bot/PlayAI/main/playai_logo.png"
COZMO_AVATAR = "https://raw.githubusercontent.com/khenkharplayai-bot/PlayAI/main/cozmo_avatar.png"

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
    page_icon="\U0001f916",
    layout="centered"
)

.stApp { background-color: #0f0c1e; color: #ffffff; }
    [data-testid="stExpander"] { background-color: #1a1a2e !important; border: 1px solid #2d2d4e !important; border-radius: 8px !important; }
    [data-testid="stExpander"] summary { color: #c4b5fd !important; }
    [data-testid="stExpanderDetails"] { background-color: #1a1a2e !important; }
    <style>
    .stApp { background-color: #0f0c1e; color: #ffffff; }
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
    .step-dot { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; }
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
    .module-card:hover { border-color: #a855f7; background: rgba(124, 58, 237, 0.18); }
    .module-card .module-icon { font-size: 2rem; margin-bottom: 0.4rem; }
    .module-card .module-name { font-weight: 700; color: #a78bfa; font-size: 0.95rem; }
    .module-card .module-desc { color: #9ca3af; font-size: 0.78rem; margin-top: 0.2rem; }
    .module-badge { display: inline-block; background: rgba(124, 58, 237, 0.25); border: 1px solid #a855f7; border-radius: 20px; padding: 3px 12px; font-size: 0.8rem; color: #c4b5fd; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

MODULES = [
    {"id": "lern_buddy", "icon": "\U0001f4da", "name": "Lern-Buddy", "desc": "Schulthemen spielerisch erklaeren", "prompt": "Du hilfst dem Kind, Schulthemen zu verstehen. Du gibst KEINE direkten Antworten. Stelle Gegenfragen die zum Denken bringen."},
    {"id": "denk_trainer", "icon": "\U0001f9e0", "name": "Denk-Trainer", "desc": "Logik, Kreativitaet & Querdenken", "prompt": "Du trainierst das logische und kreative Denken. Stelle immer Folgefragen: Warum denkst du das? Gibt es noch einen anderen Weg?"},
    {"id": "code_kids", "icon": "\U0001f4bb", "name": "Code-Kids", "desc": "Erste Schritte im Programmieren", "prompt": "Du bringst dem Kind Programmieren bei. Gib KEINEN fertigen Code. Frag stattdessen wie der Computer Schritt fuer Schritt vorgehen wuerde."},
    {"id": "kreativ_lab", "icon": "\U0001f3a8", "name": "Kreativ-Lab", "desc": "Schreiben, Erfinden & Geschichten", "prompt": "Du bist der kreative Begleiter. Schreib KEINE Geschichten fuer das Kind. Hilf mit Fragen wie: Wie koennte deine Figur aussehen?"},
    {"id": "loese_arena", "icon": "\U0001f9e9", "name": "Loese-Arena", "desc": "Knifflige Raetsel & Herausforderungen", "prompt": "Du bist der Raetsel-Meister. Beim Loesen gibst du KEINE Loesung sondern Hinweise in Form von Fragen."},
    {"id": "fokus_lab", "icon": "\U0001f3af", "name": "Fokus-Lab", "desc": "Konzentration & Lernorganisation", "prompt": "Du hilfst dem Kind, fokussiert und organisiert zu lernen. Frag zuerst: Was willst du heute schaffen?"},
    {"id": "hausaufgaben_held", "icon": "\u270f\ufe0f", "name": "Hausaufgaben-Held", "desc": "Hausaufgaben verstehen, nicht abschreiben", "prompt": "Du hilfst dem Kind, Hausaufgaben SELBST zu loesen. NIEMALS die fertige Antwort geben."}
]

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

PLAN_LIMITS = {"free": 1, "pro": 3, "family": 10}

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
    return get_children_count(user_id) == 0

def create_checkout_session(user_id, email, price_id, plan_name):
    try:
        profile = get_profile(user_id)
        customer_id = profile.get("stripe_customer_id") if profile else None
        if not customer_id:
            customer = stripe.Customer.create(email=email)
            customer_id = customer.id
            supabase_admin.table("profiles").update({"stripe_customer_id": customer_id}).eq("id", user_id).execute()
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
    supabase_admin.table("profiles").update({"subscription": plan}).eq("id", user_id).execute()

def render_steps(current_step):
    steps = ["Willkommen", "Dein Kind", "Plan waehlen"]
    cols = st.columns(len(steps) * 2 - 1)
    for i, label in enumerate(steps):
        col_idx = i * 2
        step_num = i + 1
        if step_num < current_step:
            dot_class, dot_content = "done", "v"
        elif step_num == current_step:
            dot_class, dot_content = "active", str(step_num)
        else:
            dot_class, dot_content = "inactive", str(step_num)
        with cols[col_idx]:
            st.markdown(f'<div style="text-align:center"><div class="step-dot {dot_class}" style="margin:0 auto 4px;">{dot_content}</div><div style="font-size:0.7rem;color:#9ca3af">{label}</div></div>', unsafe_allow_html=True)
        if i < len(steps) - 1:
            line_class = "done" if current_step > step_num else ""
            with cols[col_idx + 1]:
                st.markdown(f'<div class="step-line {line_class}" style="margin-top:14px"></div>', unsafe_allow_html=True)

# ── ONBOARDING ─────────────────────────────────────────────────
def show_onboarding():
    step = st.session_state.onboarding_step
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<img src="{AIKIDS_LOGO}" height="80" style="display:block;margin:0 auto">', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    render_steps(step)
    st.markdown("<br>", unsafe_allow_html=True)

    if step == 1:
        st.markdown("## Herzlich willkommen bei AI-Kids!")
        st.markdown('''<div class="onboarding-card"><h3>Ich bin Cozmo, dein KI-Lernfreund!</h3><p style="color:#c4b5fd;line-height:1.7">Ich stelle Fragen statt Antworten zu geben - damit dein Kind wirklich <strong>selbst denkt</strong>.</p></div>''', unsafe_allow_html=True)
        if st.button("Los geht's!", use_container_width=True):
            st.session_state.onboarding_step = 2
            st.rerun()

    elif step == 2:
        st.markdown("## Wie heisst dein Kind?")
        name = st.text_input("Name", placeholder="z.B. Lena", key="onb_name")
        age = st.number_input("Alter", min_value=6, max_value=14, value=9, key="onb_age")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Zurueck"):
                st.session_state.onboarding_step = 1
                st.rerun()
        with col2:
            if st.button("Weiter", use_container_width=True):
                if name.strip():
                    new_child = supabase_admin.table("children").insert({"parent_id": st.session_state.user.id, "name": name.strip(), "age": int(age)}).execute()
                    st.session_state.child = new_child.data[0]
                    st.session_state.onboarding_step = 3
                    st.rerun()
                else:
                    st.warning("Bitte gib einen Namen ein.")

    elif step == 3:
        child_name = st.session_state.child["name"] if st.session_state.child else "dein Kind"
        st.markdown(f"## Plan fuer {child_name}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('''<div class="onboarding-card" style="text-align:center"><div style="font-weight:800;font-size:1.1rem;color:#a78bfa">Free</div><div style="font-size:1.6rem;font-weight:900">0 EUR</div><div style="color:#c4b5fd;font-size:0.82rem;text-align:left">1 Kind, 10 Fragen/Tag</div></div>''', unsafe_allow_html=True)
            if st.button("Free starten", use_container_width=True, key="plan_free"):
                st.session_state.page = "module_select"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.session_state.onboarding_step = 1
                st.rerun()
        with col2:
            st.markdown('''<div class="onboarding-card" style="text-align:center;border-color:#a855f7"><div style="font-weight:800;font-size:1.1rem;color:#a78bfa">Pro</div><div style="font-size:1.6rem;font-weight:900">9,99 EUR</div><div style="color:#c4b5fd;font-size:0.82rem;text-align:left">Alle Module, unlimitiert</div></div>''', unsafe_allow_html=True)
            if st.button("Pro waehlen", use_container_width=True, key="plan_pro"):
                url = create_checkout_session(st.session_state.user.id, st.session_state.user.email, STRIPE_PRO_PRICE_ID, "pro")
                if url:
                    st.markdown(f"[Jetzt zu Stripe]({url})")
        with col3:
            st.markdown('''<div class="onboarding-card" style="text-align:center"><div style="font-weight:800;font-size:1.1rem;color:#a78bfa">Family</div><div style="font-size:1.6rem;font-weight:900">14,99 EUR</div><div style="color:#c4b5fd;font-size:0.82rem;text-align:left">Bis zu 4 Kinder</div></div>''', unsafe_allow_html=True)
            if st.button("Family waehlen", use_container_width=True, key="plan_family"):
                url = create_checkout_session(st.session_state.user.id, st.session_state.user.email, STRIPE_FAMILY_PRICE_ID, "family")
                if url:
                    st.markdown(f"[Jetzt zu Stripe]({url})")
        col1, _ = st.columns([1, 3])
        with col1:
            if st.button("Zurueck"):
                if st.session_state.child:
                    supabase_admin.table("children").delete().eq("id", st.session_state.child["id"]).execute()
                    st.session_state.child = None
                st.session_state.onboarding_step = 2
                st.rerun()

# ── LOGIN / REGISTRIERUNG ──────────────────────────────────────
def show_auth():
    st.markdown(f"""
<div style="text-align:center;padding:1.5rem 0 1rem 0">
    <div style="display:inline-flex;align-items:center;gap:12px">
        <img src="{AIKIDS_LOGO}" style="height:5rem;width:auto">
        <span style="font-size:2.5rem;font-weight:900;color:#a855f7;line-height:1">AI-Kids</span>
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
                res = supabase_auth.auth.sign_in_with_password({"email": email, "password": password})
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
                res = supabase_auth.auth.sign_up({"email": email, "password": password})
                supabase_admin.table("profiles").insert({"id": res.user.id, "email": email, "role": "parent", "subscription": "free"}).execute()
                st.session_state.user = res.user
                st.session_state.page = "onboarding"
                st.session_state.onboarding_step = 1
                st.rerun()
            except Exception as e:
                st.error(f"Fehler: {e}")

    st.markdown(f"""
<div style="text-align:center;padding:2rem 0 1rem 0">
    <div style="display:inline-flex;align-items:center;gap:8px">
        <img src="{PLAYAI_LOGO}" style="height:5rem;width:auto">
        <span style="font-size:1rem;color:#9ca3af">by PlayAI</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── ELTERN-DASHBOARD ───────────────────────────────────────────
def show_dashboard():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Eltern-Dashboard")
    with col2:
        st.markdown(f'<div style="padding-top:0.5rem"><img src="{PLAYAI_LOGO}" style="height:1.8rem;width:auto"></div>', unsafe_allow_html=True)

    st.markdown(f"Eingeloggt als: **{st.session_state.user.email}**")
    subscription = get_subscription(st.session_state.user.id)
    plan_badge = {"free": "Free", "pro": "Pro", "family": "Family"}
    st.markdown(f"**Aktueller Plan:** {plan_badge.get(subscription, 'Free')}")

    params = st.query_params
    if "success" in params:
        plan = params.get("plan", "pro")
        upgrade_subscription(st.session_state.user.id, plan)
        st.success(f"Upgrade auf {plan.capitalize()} erfolgreich!")
        st.query_params.clear()
        st.rerun()
    if "cancelled" in params:
        st.warning("Zahlung abgebrochen.")
        st.query_params.clear()

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Cozmo starten"):
            st.session_state.page = "child_select"
            st.rerun()
    with col2:
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.session_state.child = None
            st.session_state.active_module = None
            st.rerun()

    st.divider()
    st.markdown("### Chat-Sessions")
    sessions = supabase_admin.table("chat_sessions").select("*, children(name)").order("started_at", desc=True).execute()
    if not sessions.data:
        st.info("Noch keine Chat-Sessions vorhanden.")
        return
    for session in sessions.data:
        session_id = session["id"]
        started = session["started_at"][:16].replace("T", " ")
        child_name = session["children"]["name"] if session.get("children") else "Unbekannt"
        module_name = session.get("module_name", "")
        module_label = f" - {module_name}" if module_name else ""
        msgs = supabase_admin.table("messages").select("*").eq("session_id", session_id).order("created_at").execute()
        user_msgs = [m for m in msgs.data if m["role"] == "user"]
        with st.expander(f"{child_name}{module_label} - {started} - {len(user_msgs)} Fragen"):
            for msg in msgs.data:
                if msg["role"] == "user":
                    st.markdown(f"👦 **{child_name}:** {msg['content']}")
                else:
                    st.markdown(f"🤖 **Cozmo:** {msg['content']}")

# ── KIND AUSWÄHLEN ─────────────────────────────────────────────
def show_child_select():
    st.title("Kind-Profil")
    st.markdown("### Wer chattet heute mit Cozmo?")
    st.divider()
    children = supabase_admin.table("children").select("*").eq("parent_id", st.session_state.user.id).execute()
    if children.data:
        st.markdown("#### Vorhandene Kinder:")
        for child in children.data:
            if st.button(f"{child['name']} ({child['age']} Jahre)", key=child["id"]):
                st.session_state.child = child
                st.session_state.page = "module_select"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.session_state.active_module = None
                st.rerun()
        st.divider()
    allowed, subscription, limit, count = can_add_child(st.session_state.user.id)
    st.markdown("#### Neues Kind hinzufuegen:")
    if not allowed:
        st.warning(f"Dein {subscription.capitalize()}-Plan erlaubt max. {limit} Kind(er). Du hast bereits {count}.")
    else:
        name = st.text_input("Name des Kindes")
        age = st.number_input("Alter", min_value=6, max_value=14, value=9)
        if st.button("Hinzufuegen & starten"):
            if name:
                new_child = supabase_admin.table("children").insert({"parent_id": st.session_state.user.id, "name": name, "age": int(age)}).execute()
                st.session_state.child = new_child.data[0]
                st.session_state.page = "module_select"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.session_state.active_module = None
                st.rerun()
            else:
                st.warning("Bitte Namen eingeben.")
    if st.button("Zurueck"):
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
        st.markdown(f"<h2 style='text-align:center;color:#a855f7;margin-bottom:0'>Hey {child_name}!</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#9ca3af;margin-top:0'>Was moechtest du heute mit Cozmo machen?</p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Zurueck"):
            st.session_state.page = "child_select"
            st.rerun()
    st.divider()

    if "featured_module_idx" not in st.session_state:
        st.session_state.featured_module_idx = random.randint(0, len(MODULES) - 1)
    featured_idx = st.session_state.featured_module_idx
    featured = MODULES[featured_idx]
    others = [m for i, m in enumerate(MODULES) if i != featured_idx]

    st.markdown(f"""<div style='background:linear-gradient(135deg,rgba(124,58,237,0.35),rgba(168,85,247,0.15));border:2px solid #a855f7;border-radius:20px;padding:1.5rem;text-align:center;margin-bottom:0.5rem'><div style="font-size:0.7rem;font-weight:700;color:#22d3ee;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.5rem">HEUTE EMPFOHLEN</div><div style="font-size:3rem;margin-bottom:0.4rem">{featured['icon']}</div><div style="font-weight:800;font-size:1.3rem;color:#a855f7;margin-bottom:0.3rem">{featured['name']}</div><div style="color:#c4b5fd;font-size:0.9rem">{featured['desc']}</div></div>""", unsafe_allow_html=True)
    if st.button(f"Jetzt starten", key=f"mod_{featured['id']}", use_container_width=True):
        st.session_state.active_module = featured
        st.session_state.page = "chat"
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    for i in range(0, len(others), 2):
        col1, col2 = st.columns(2)
        for j, col in enumerate([col1, col2]):
            idx = i + j
            if idx < len(others):
                mod = others[idx]
                with col:
                    st.markdown(f'''<div class="module-card"><div class="module-icon">{mod['icon']}</div><div class="module-name">{mod['name']}</div><div class="module-desc">{mod['desc']}</div></div>''', unsafe_allow_html=True)
                    if st.button(f"Starten", key=f"mod_{mod['id']}", use_container_width=True):
                        st.session_state.active_module = mod
                        st.session_state.page = "chat"
                        st.session_state.messages = []
                        st.session_state.session_id = None
                        st.rerun()

# ── COZMO CHAT ─────────────────────────────────────────────────
def show_chat():
    import re
    child_name = st.session_state.child["name"] if st.session_state.child else "du"
    child_age = st.session_state.child["age"] if st.session_state.child else 10
    module = st.session_state.active_module

    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown(f'<div style="display:flex;align-items:center;justify-content:center;height:100%;padding-top:0.3rem"><img src="{AIKIDS_LOGO}" style="height:2.4rem;width:auto"></div>', unsafe_allow_html=True)
    with col2:
        st.markdown("<h2 style='text-align:center;color:#a855f7;margin-bottom:0'>Cozmo</h2>", unsafe_allow_html=True)
        if module:
            st.markdown(f"<p style='text-align:center;margin-top:4px'><span class='module-badge'>{module['icon']} {module['name']}</span></p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Module"):
            st.session_state.page = "module_select"
            st.session_state.messages = []
            st.session_state.session_id = None
            st.session_state.active_module = None
            st.rerun()
    st.divider()

    if "session_id" not in st.session_state or st.session_state.session_id is None:
        st.session_state.session_id = str(uuid.uuid4())
        child_id = st.session_state.child["id"] if st.session_state.child else None
        module_name = module["name"] if module else None
        try:
            supabase_admin.table("chat_sessions").insert({"id": st.session_state.session_id, "child_id": child_id, "module_name": module_name}).execute()
        except Exception:
            supabase_admin.table("chat_sessions").insert({"id": st.session_state.session_id, "child_id": child_id}).execute()

    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = []
        if module:
            welcome = f"Hey {child_name}! Ich bin Cozmo. Heute starten wir mit {module['icon']} {module['name']}! Was willst du angehen?"
        else:
            welcome = f"Hey {child_name}! Ich bin Cozmo, dein Lernbegleiter. Was moechtest du heute lernen?"
        st.session_state.messages.append({"role": "assistant", "content": welcome})
        supabase_admin.table("messages").insert({"session_id": st.session_state.session_id, "role": "assistant", "content": welcome}).execute()

    def render_cozmo_msg(text):
        safe_text = text.replace("<", "&lt;").replace(">", "&gt;")
        safe_text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe_text)
        safe_text = safe_text.replace("\n", "<br>")
        st.markdown(f'''
        <div style="display:flex;align-items:flex-start;gap:16px;margin-bottom:16px">
            <img src="{COZMO_AVATAR}" width="120" height="120"
                 style="border-radius:50%;flex-shrink:0;object-fit:cover;border:3px solid #a855f7">
            <div style="background:rgba(124,58,237,0.25);border:1px solid rgba(168,85,247,0.5);border-radius:16px;padding:14px 18px;color:#ffffff;font-size:16px;line-height:1.6;max-width:85%;margin-top:8px">
                {safe_text}
            </div>
        </div>
        ''', unsafe_allow_html=True)

    for message in st.session_state.messages:
        if message["role"] == "assistant":
            render_cozmo_msg(message["content"])
        else:
            with st.chat_message("user"):
                st.markdown(message["content"])

    if prompt := st.chat_input("Stell mir eine Frage..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        supabase_admin.table("messages").insert({"session_id": st.session_state.session_id, "role": "user", "content": prompt}).execute()

        base_prompt = f"Du bist Cozmo, ein freundlicher KI-Lernbegleiter fuer Kinder von AI-Kids. Du sprichst mit {child_name}, {child_age} Jahre alt. Passe deine Sprache dem Alter an. Halte Antworten kurz, max. 3-4 Saetze."
        if module:
            system_prompt = base_prompt + "\n\n" + module["prompt"]
        else:
            system_prompt = base_prompt + "\nDu gibst KEINE direkten Antworten, sondern stellst Gegenfragen. Das ist das Sokrates-Prinzip."

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
        supabase_admin.table("messages").insert({"session_id": st.session_state.session_id, "role": "assistant", "content": answer}).execute()

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
