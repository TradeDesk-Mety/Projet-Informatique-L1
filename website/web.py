"""
web.py — Point d'entrée principal du Simulateur Boursier L1
Gère : authentification + session + navigation vers les pages Streamlit.
"""
import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from equities.equities import Portfolio
from data.database import PORTFOLIO_DB_PATH

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulateur Place Boursière — L1",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0E1117; }
  [data-testid="stSidebar"]          { background: #111827; border-right: 1px solid #1F2937; }
  .stMetric { background: #1F2937; border-radius: 10px; padding: 12px; }
  h1, h2, h3 { color: #F9FAFB; }
  .st-emotion-cache-1y4p8pa { max-width: 100%; }
</style>
""", unsafe_allow_html=True)

# ── Portefeuille en session ───────────────────────────────────────────────────
if "portfolio" not in st.session_state:
    p = Portfolio(initial_cash=10000.0)
    try:
        p.load_from_db(PORTFOLIO_DB_PATH)
    except Exception:
        pass
    st.session_state.portfolio = p

# ── Authentification ──────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align:center;padding-top:60px'>
      <h1 style='font-size:3rem'>📈 Simulateur Place Boursière</h1>
      <p style='color:#9CA3AF;font-size:1.1rem'>Projet Informatique L1 — Plateforme de Paper Trading Quantitatif</p>
    </div>
    """, unsafe_allow_html=True)

    col_center = st.columns([1, 1.2, 1])[1]
    with col_center:
        st.markdown("""
        <div style='background:#1F2937;padding:30px;border-radius:16px;
                    border:1px solid #374151;margin-top:20px'>
          <h3 style='color:#F9FAFB;text-align:center;margin-bottom:20px'>🔑 Connexion</h3>
        """, unsafe_allow_html=True)
        email = st.text_input("Adresse e-mail", placeholder="vous@example.com")
        mdp   = st.text_input("Mot de passe",   type="password", placeholder="••••••••")

        if st.button("Se connecter", type="primary", use_container_width=True):
            if email and len(mdp) >= 4:
                st.session_state.logged_in  = True
                st.session_state.user_email = email
                st.success("✅ Connexion réussie !")
                st.rerun()
            else:
                st.error("Email et mot de passe requis (min. 4 caractères).")
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_email}")
    st.divider()
    st.markdown("**📂 Navigation**")
    st.markdown("""
    > Utilise le menu des **pages** en haut de cette barre latérale pour naviguer.
    - 📊 **Marché** — cours en direct & analyse
    - 💼 **Portefeuille** — ordres & positions
    - 🔬 **Backtesting** — stratégies historiques
    - 🤖 **Bot** — trading automatique
    - 📐 **Options 3D** — Black-Scholes
    """)
    st.divider()

    # Rafraîchissement des données Medallion
    st.markdown("**🗄️ Base de données SQL**")
    if st.button("🔄 Rafraîchir le marché", use_container_width=True):
        with st.spinner("Mise à jour parallèle (1 000 actifs)…"):
            try:
                import data.medallion as med
                res = med.run_full_pipeline_multithreaded(max_workers=20)
                ok  = sum(1 for v in res.values() if v)
                st.success(f"✅ {ok}/{len(res)} actifs mis à jour")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

    st.divider()
    if st.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ── Page d'accueil ────────────────────────────────────────────────────────────
st.title("📈 Simulateur Place Boursière — L1")
st.markdown("""
Bienvenue ! Utilise la barre latérale pour accéder aux différentes sections :

| Page | Description |
|------|-------------|
| 📊 **Marché** | Cours en temps réel, chandeliers, indicateurs techniques |
| 💼 **Portefeuille** | Passer des ordres, suivre tes positions |
| 🔬 **Backtesting** | Tester des stratégies SMA / RSI sur l'historique |
| 🤖 **Bot** | Robot de trading automatique |
| 📐 **Options 3D** | Surface de pricing Black-Scholes |

> **Architecture** : Pipeline Medallion SQL — Bronze → Silver → Gold  
> **1 000 actifs** : S&P 500 + NASDAQ 100 + DAX + CAC40 + FTSE100 + …
""")
