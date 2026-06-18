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

AIKIDS_LOGO = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj4KICA8IS0tIExpbmtlciBTY2hyw6Rnc3RyaWNoICgvKSAtLT4KICA8cG9seWdvbiBwb2ludHM9IjE1LDg1IDI4LDg1IDQ4LDE1IDM1LDE1IiBmaWxsPSIjYTg1NWY3Ii8+CiAgPCEtLSBSZWNodGVyIFRlaWwgWCAtIG9iZXJlciBTdHJpY2ggLS0+CiAgPHBvbHlnb24gcG9pbnRzPSI1MiwxNSA2NSwxNSA4NSw1NSA3Miw1NSIgZmlsbD0iI2E4NTVmNyIvPgogIDwhLS0gUmVjaHRlciBUZWlsIFggLSB1bnRlcmVyIFN0cmljaCAtLT4KICA8cG9seWdvbiBwb2ludHM9IjcyLDQ1IDg1LDQ1IDY1LDg1IDUyLDg1IiBmaWxsPSIjYTg1NWY3Ii8+CiAgPCEtLSBLcmVpcyBpbiBkZXIgTWl0dGUgLS0+CiAgPGNpcmNsZSBjeD0iNDIiIGN5PSI1MCIgcj0iOCIgZmlsbD0id2hpdGUiLz4KPC9zdmc+"
PLAYAI_LOGO = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgODAiPgogIDwhLS0gS2xlaW5lcyBEcmVpZWNrIGxpbmtzIC0tPgogIDxwb2x5Z29uIHBvaW50cz0iMjIsNjUgMzgsNjUgMzAsNDgiIGZpbGw9IiNhODU1ZjciLz4KICA8IS0tIEdyb8OfZXMgQSByZWNodHMgKGxpbmtlciBTY2hlbmtlbCkgLS0+CiAgPHBvbHlnb24gcG9pbnRzPSIzOCw2NSA1Miw2NSA2MiwyMCA1MCwyMCIgZmlsbD0iI2E4NTVmNyIvPgogIDwhLS0gR3Jvw59lcyBBIHJlY2h0cyAocmVjaHRlciBTY2hlbmtlbCkgLS0+CiAgPHBvbHlnb24gcG9pbnRzPSI1Miw2NSA2OCw2NSA1OCwyMCA0NiwyMCIgZmlsbD0iI2E4NTVmNyIvPgogIDwhLS0gV2Vpw59lciBLcmVpcyAtLT4KICA8Y2lyY2xlIGN4PSI1NCIgY3k9IjM4IiByPSI5IiBmaWxsPSJ3aGl0ZSIvPgogIDwhLS0gS2xlaW5lciBEcmVpZWNrIG9iZW4gLS0+CiAgPHBvbHlnb24gcG9pbnRzPSI1MCwxNSA1OCwxNSA1NCwyMiIgZmlsbD0iI2E4NTVmNyIvPgo8L3N2Zz4="

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
