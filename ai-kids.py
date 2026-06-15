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

AIKIDS_LOGO = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQCAYAAACAvzbMAAATlElEQVR4nO3dPY5c15mA4SNBCSMC1gII0DtwKG1AqVMD3sTAIYXBwAwNb8KAU6XagBXODiSAC5AARcykCTglNburuu7P+fm+c54HGBj2kOyqe2+ft893q6pLAQAAAAAAAAAAAAAAAAAAgIc+Gf0AoJc3X/z4a6+v9fa7z31vMT0XOen1DENtQkNmLl5SyByJo8SF6FyghLJiKPYSFqJwITKMWNQjKozgoqMbwehHUOjBRUYzghGHoNCCi4qqRCM+MaEWFxKnCEZ+gsJRLhx2E415iQl7uFjYRDTWIybc4wLhJtHgQky4xkXBE8LBLULCQy4GSimiwX5iggtgccLBWUKyLid+QaJBK2KyFid7IcJBL0KyBid5AcLBKEIyNyd3YsJBFEIyJyd1QsJBVEIyFydzIsLxvJevX3T7Wj//8L7b18pISObgJE5AOPrGoRaREZLsnLzEVgtHxkgctVpchCQnJy2hFcKxUiy2WiEqQpKLk5XIzOEQjP1mDoqQ5OAkJTBjOASjvhmDIiSxOTnBzRIPwehvlqCISFxOTFAzhEM04pghJkISjxMSTOZwCEYemYMiJHE4EYFkjIdo5JcxJiISg5MQgHAQgZCwl4M/WKZ4iMY6MsVERMZx4AcRDjIQEp7jgA+QIR6iwWMZYiIifTnYHQkHMxASLhzkTqLHQzjYK3pIRKQ9B7iDqPEQDWqJGhMRacvBbUg4WI2QrMVBbSRiPISDXiKGRETqc0AbiBYP4WCUaCERkboczIqihaMU8WC8aBEpRUhqcRAriRYP4SCaaCERkfMcwAoixUM4iC5SSETkHAfvpCjxEA6yiRISETnOgTsoSjhKEQ/yihKRUoTkCAfsgCjxEA5mESUkIrKPg7VThHgIB7OKEBIR2e7T0Q8gE/GAtiJc3xG+z7NQ2o1GX1QRvrGgp9G7ETuR++xANhAP6G/0dT/6+z4Dhb1j5EU0+hsIohi5G7ETuc2BuWH0Tx/iAR8z0orHCOsK8YB4Rn9fjF4XIlLUR4ysID4jrRjsQB4QD8hh5PeLncjvBOT/iQfkIiLj2YqVcReDcEAdo0Zaq4+zlt+BiAfE919v//zs/3/U99PqO5GlAyIeEN8lHi0i8j///suhx/TQyhFZdvslHhDbtWD88803d//e1nHWtXj891/+venvXrPiOGvJHciIeLx8/UI8YIdrsbi3Cynl+PfamXiUsuZOZMmA9CYc0N9z33c1RlcsGJDePyWIBxx3dBdysfX77+zu42K1XchSAREPmMOZiLTefawUkWUCIh6Q05Yb5/c89/1Ya/fx0CoRWSIg4gG5nR1llfLh+7LnvY8VIjJ9QMQDuKXF7uOh2SMydUDEA+Zxdheyd8dSy8wRmTYg4gE8p/Xu46FZIzJtQHoSD+jj6C7k2p/xfXvelAHpWXsXIfS1NyLPfSRKz+/fGXch0wVEPIDnPA6QiBw3VUDEA9awdRey9ca5iBwzTUDEA7jnuTclish+0wSkF/GAGO7tQo68bNf39z5TBKRXzV1cEN+tcGz9SJRe3+cz7ELSB0Q8YF23onD2TYMisk3qgIgHsGVnceQDGUXkvs9GP4DoxAPqGvWRIke8fP1i86/IXVHa3+Hbo9riAfVlCsg9NT8OJePvVE85whIPYDYZR1npApLxIANskW19cw/kCrsPaKfGbxi8ZqbRWBapAmJ0BRxVK1ytb6q/+eLHX7PcD0kzwhIP4Jaeu48e60SWUVaagLQmHpDT1njUjIz14oMUAclSYyCGf775ptm9ll4yrHvhA2J0Bdzy3C+L2vrnjzLKShCQ1sQDctoSg6O/Aner1deP0AFpXd/VTz7M5lowWo+yWq8jkXchYV8qlmV09bd/idDs/vHX+y/bdB309cu7r578b5+++rban7/mueugx+dlRXxpb+gdSEt2H7COvbHYa9X1JGRAjK6AW2rsJm79O2esOMoKGZCWxAPyOrPot96FlLLe+hLuo0wiVnan70c/AE77Y4V/w3XQxpNz8+mrb/cc64/+/i/vvnru79e4DqqK9jEnoXYgRlfALb+8++psPK7++Wv/7hkrjbJCBaQl8YC8ai7ye6NzxCrrTZiARKoqEF/NENTehbQWZb0ME5CWVvlpAGZUY3RV++9vscK6EyIgLWu6wkkEzmuxC2m5/kTYhYQICMA1LXYftf+dlQ0PiN0HcMunr779vudCbxeyz/CAANxziUjtmDz8d3vHagZDA2L3AWzVanHPfkN95C5kyh2IeADRzLguDQvI6NkdwCxGrafhPgvrrBkrD6WU8vWXP6V6s1tPf//PH1Lcu3j5+kWX3x3Sy5AdiN0HQF0j1tWp7oHYfbRz9KdfPzXDx2Zap7qPsOw+8noYg+dGBqIBY/T+uPdp7oHMVPVorgXhcUyei8bXX/70xywzauhhlnshXUdYrXYf4jGWHQfs12rd6jnlmeoeCAD9dAuI3UdOtXYXdinwVPZdiB0IAId0CYjdB8B1mXch07wKi/pqj528GuucEcfu6DXgPK8h7QjL7gOYRdb1rHlAvHEQYIzW62/aHQhttXrVlFdjwTyaBsTNc4BtMt5MtwMB4JB0AbH7AGaVbX1rFhA3z/NqfZ/CfRDoq9V6nGoHkq3OAHtlWueaBMTuAyCWFutyqh0I7fUaLxljQX5pApJpWwdwRpb1rnpAjK8AYqq9PqfYgWSpcXa9x0rGWHBbhnUvRUAAiKdqQIyvAGKruU6H34Fk2MbNYNQ4yRgLbou+/oUPCPH55UGwpmoBaTG+il5fgNZarIO11ms7EIaPkUZ/feAYAeGUy/jKGAvWEzYgxlcAH0RdD6sExMt384oyPoryOGAVNdbtsDsQ4ns8tjLGgrUICACHnA6Il+/mFW1sFO3xQCQRX85rB8Iht8ZVxliwDgEB4JBwATG+6iPquCjq44IIoq2PpwLi5btrujemMsaCPM6s4+F2IADkICALij4miv74gA9CBSTafI+nto6njLGgjUjr5OGAuP8BMIej63moHQgAeQjIYs7cX9g7ljozxnIfBOILE5BIcz2AyKKsl2ECAkAuhwLiBnpOPcdXZ/9eKcZY0NORdd0OBIBDQgQkyjwPIIsI62aIgNBe1nFQ1scNKxAQ7jr7rnLvSoc5CQgAh+wOiFdg5ZN9DJT98UMWe9f34TuQCDeCuK3W+MkYC+obvX4ODwgAOQnI5GYZ/8zyPGAmAsJNtcdOxlgwFwEB4BABmdhsY5/Zng9ktysgXsK7jlbjJmMsiG3POj90BzL6JWgA2Y1cR42wJjXruGfW5wUZCQhPtB4zGWPBHAQEgEMEZEKzj3lmf36QhYDwkV7jJWMsyE9AADhEQCazynhnlecJkQkIv+k9VjLGgtw2B6T2u9C9iRCgjtrr6db13g4EgEMEZCJn7guMGied+brug8BYAgLAIQICwCECMomM46saX98YC8YREAAOERAADhGQCaw+xln9+cMon41+AIxnAQaOsAMB4BABSc7u4QPHAfoTEAAOERAADhGQxIxtPuZ4QF8CAsAhAgLAIQKSlHHNdY4L9CMgABzinegLGv3pu1vYSUB8diAJWVyf5/hAHwKymAy7j1LyPE5YmYAAcIiAJGM8s43jBO0JyEKyjYWyPV5YjYAAcIiAJGIss4/jBW1tDsjb7z7/pOYX/vmH9zX/Oe7IOg7K+rihp9rr6db13g4EgEMEBIBDBCSJM/P87GOgM4/ffRBoR0AAOERAADhEQBJYeXx1YYwF8QgIAIcICACHDA2INxPeZ/xSh+PIrEauo7sCUvvd6LQ1y/2Pi9meD0S0Z503wgLgEAEJzNilLscT6hKQSc067pn1eUFGAgLAIQISlHFLG44r1DM8IF7KW9/sY57Znx9sNXr93B0QL+UFmNPe9X34DoSnjFnacnyhDgGZzCrjnVWeJ0QmIAAcEiIgo28ERWK80ofjTHYR1s0QAaGO1cY6qz1fiOZQQLwSC2AuR9Z1O5BAjFX6crzhnDABiTDPy2zVcc6qz5u1RVkvwwQEgFwEJAjjlDEcdzjucEDcSI9j9THO6s8fzjq6nofagUSZ6wFEFWmdDBUQAPIQkADOzOGNbz44cxzcB4FjTgXEfRCA3M6s4+F2IJHmewCRRFsfwwVkNcZX9RhjQV8CAsAhpwPS4j5ItG0awGgt1sWz67cdyEDGJrE4H7CPgCTl/sd1jgv0UyUgXs4LkEuNdTvsDmT2+yDGJTE5L0QUdT0MGxBuM6Z5nuMDfXw2+gEA22TaHfV+rH5oGKPaDsTLebfLtBCs6Osvfxr9EOA3EV++e2GElYyftLZxnKC98COsn394X16+fjH6YVT1cHGzG4njwXlxTggh+hSmakDefvf5J2+++PHXmv/m7B7/pCwo/dilsKKatxvC70BW89zuxIK3z9//84fvHUNoJ0VAZhxjbWHUVYdokFH08VUpDW6ie1d6GxbBYxw3+F3t9TnNq7Ay1BighizrXZqAABBLk3sgXo0F9RnHcUaL2wupdiBZtnUAR2Va55oFxM10gBharcepdiCl5KozwB7Z1rd0AQEghqYBabVtylZpgHtarWstbyfYgQBwSPOAuJkOMEbr9TftDsQYC5hF1vUsbUAAGKtLQNxMB7gu483zixQf556Mj12nFNcBC+g2wrILAfhY5t1HKe6BAHBQ14DYhQB8kH33UUop3d+j0fJj3lf8tbdAPi1/6O0ZkO4jLG8sBGij9/o61T0QoywgupnWqSEBsQsBqGvEujrVDqSUueoOzGW29WlYQOxCAOoYtZ5OtwMpZb7KA/nNuC4NDUjLas54soCcZnnZ7mNT7kAAaC/EfYieby78279e/LnV1wL4x1/ff/Pwv8+6+yjFDgSAg0J8nPvb7z7/pNUu5Ocf3t/6iJP/bfH1gGX96fH/MPPuo5RFdiBuqAO9rbDuhAlIhJoCZBBlvQwTkNZW+GkAiGGV9SZUQFpXdZWTCozTep2JsvsoJVhASol1cAAiibY+hgsIADmEDEi0ygKMFnFdDBkQAOILG5CItQUYIep6GDYgpcQ9aAC9RF4HQweEU96NfgDA3MIHJHJ9A3v36D+BhKKvfyE+TPGelh+22MGtRfxVx6/VyrWvd+Z59TxWEFr0eJSSYAfCZrcW31ZR6f31gGDSBCRDjQe6t2jXXtR7fz1YSpb1Lk1ASslzUDt6V7Yt1jVHQFvjICJwQKZ1LsU9EK7qHQ6Aj6TagZSSq84NiQdMKNv6li4gpeQ7yJWJB0wo47qWMiCl5DzYJ2253/GqiAekk3U9cw8kh0i7jlcl7o37Fl8buCHtDqSUvNXeKVI8tn49CzhslHkdSx2QUnIf/DtGvER3D5GAk7KvX+kDUkr+k3DF1nBYxCGpGdatKQIymci7DoDfTBOQCWoefWQFVDLBelVKmSggpaQ+KUZWz1v1eTOhxOvUE1MFpJSUJ8euAxaRcH161nQBKSXVSRKPbfbs0BwvQkq0Lm3mjYTjbHlXOfc5TjDIlDuQUtLX3qK4jeNECsnXo5um3oEk/VW4FsVtMhynHr+i168BDm7WeJQy8Q7kItnJ802/TfbjVOuXbfmlXcElW392mz4gpaQ4iW7+bpfpOD33WN89+r8ttv6dTMdoWgnWndOmHmE9FHic5ZudUuwmprJCPEpZZAdyscpJJZRon5RMYyutM0sFJCg/eW6XdXHs+btaoBsBiUFE5tfyPpd7aAyxzD2QBC4RsRDM7XJ+a/zQ4FphKAGJ512xMKzg8Tn2sTakIyAx2Y3M78gO5PHfcX0wlHsgsbk3Mp897/vo+W/BbgIyztYbnxaIebQ6l64RhhCQ8bZGxCKRW+vz5/qgOwGJwW5km6zPv9fjznp8SMpN9FhelfuLgFdp5bJ1Ua/1A4Trg24EJJ6tEbn8WeKq/UvDHv755/5tEaELI6yYjLRum+E513jnuHefM5yAxCYi1634nCEcI6z4jLSuyzCm6fH4oh8DJmYHkoOR1nWrPV8IRUBy8Z6Rp1Z7vhCGgOSzdWQx06K6J5wzPW8ITUByMtIChhOQ3FYaaXnZKgTjVVj5bf0FRRletXTLDAGE6diBzONeHLLGAwhKQOZyKxLiAVRnhNVe78W75u/c3vq1av97RlaQgB3IvF49+k+AqgRkbuIBNGOERUTCBwnYgQBwiIAAcIiAAHCIgABwyMo30f80+gEAZGYHAsAhn4x+APzuzRc//jr6Mez18vWL0Q+Bk37+4f3oh7Db2+8+t3YF4CQEkzEiF2KSR8ZoXIhHHE5EUJlDciEocWQOxoVwxOOEBDdDSEoRkxFmiEYpwhGZE5PALBF5SFDqmyUYD4lHbE5OIjOG5EJQ9psxGBfCkYOTlNDMIbkQlKdmDsaFcOTiZCW2QkgeWikqK8TiIeHIyUmbwGohuSZjXFaLxDXCkZuTNxEheV7PyIjD84RjDk7ihISEqIRjLk7mxISEKIRjTk7qAoSEUYRjbk7uQoSEXoRjDU7ygoSEVoRjLU724sSEs0RjXU48pRQhYT/hwAXAE2LCLaLBQy4GbhISLoSDa1wUbCIm6xEN7nGBsJuYzEs02MPFwilikp9ocJQLh6oEJT7BoBYXEs2ISRyiQQsuKroRlH4Egx5cZAwjKPUIBiO46AhFVO4TC6JwIZLCimERCqJzgZJe5riIBJm5eFlGz9AIAwAAAAAAAAAAAAAAAAAAqf0fTG0g84ykqCQAAAAASUVORK5CYII="
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

    # 2 Spalten Grid für Module
    for i in range(0, len(MODULES), 2):
        col1, col2 = st.columns(2)
        for j, col in enumerate([col1, col2]):
            idx = i + j
            if idx < len(MODULES):
                mod = MODULES[idx]
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

    # Chat-Verlauf
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
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

        with st.chat_message("assistant"):
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=system_prompt,
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
elif st.session_state.page == "module_select":
    show_module_select()
elif st.session_state.page == "chat":
    show_chat()
