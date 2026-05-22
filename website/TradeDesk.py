"""
web.py — Point d'entrée principal du Simulateur Boursier
=========================================================

Gère : authentification sécurisée (hachage de mot de passe), enregistrement,
sessions multi-utilisateurs et navigation vers les pages Streamlit.

Relations avec les autres modules :
----------------------------------
- data.database : Fournit les connexions aux bases de données SQLite.
- data.security : Hache et vérifie les mots de passe des utilisateurs.
- equities.equities : Initialise et gère le portefeuille propre à chaque utilisateur connecté.
"""

import streamlit as st
import os
import sys
import sqlite3
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from equities.equities import Portfolio
from website.components.ui_config import set_global_ui
from website.components.assistant_sidebar import render_assistant
from data.database import get_portfolio_connection
from data.security import hash_password, verify_password

# ─── Configuration de la page ────────────────────────────────────────────────
st.set_page_config(
    page_title="TradeDesk — Simulateur Boursier",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
set_global_ui()

# ─── CSS Global — Style Revolut ───────────────────────────────────────────────


# ─── Initialisation de l'état de session ─────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_username" not in st.session_state:
    st.session_state.user_username = None
if "show_onboarding" not in st.session_state:
    st.session_state.show_onboarding = False

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE DE CONNEXION / INSCRIPTION
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center; padding-top:64px; padding-bottom:8px;'>
      <div style='display:inline-flex; align-items:center; gap:14px; margin-bottom:18px;'>
        <div style='width:56px; height:56px; background:linear-gradient(135deg,#06B6D4,#2563EB);
                    border-radius:14px; display:flex; align-items:center; justify-content:center;
                    font-size:2rem; box-shadow:0 8px 24px rgba(6,182,212,0.35);'>📈</div>
        <span style='font-family:Inter,sans-serif; font-size:2.2rem; font-weight:800;
                     background:linear-gradient(90deg,#06B6D4,#7C3AED);
                     -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
          TradeDesk
        </span>
      </div>
      <p style='color:#8A94A6; font-size:1.05rem; font-family:Inter,sans-serif; margin:0;'>
        Simulez, analysez et automatisez vos stratégies boursières — sans risque réel.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Formulaire centré avec glassmorphism ──────────────────────────────────
    _, col_form, _ = st.columns([1, 1.25, 1])
    with col_form:
        st.markdown("""
        <div style='background:rgba(17,19,24,0.85); backdrop-filter:blur(20px);
                    border:1px solid #1E2028; border-radius:20px; padding:36px 32px;
                    margin-top:12px; box-shadow:0 24px 60px rgba(0,0,0,0.5);'>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Connexion", "Inscription"])

        # ── Onglet Connexion ──────────────────────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input(
                "Nom d'utilisateur", placeholder="Votre pseudo", key="login_email"
            )
            mdp = st.text_input(
                "Mot de passe", type="password", placeholder="••••••••", key="login_mdp"
            )
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Se connecter", type="primary", use_container_width=True, key="btn_login"):
                if not username or not mdp:
                    st.error("Veuillez remplir tous les champs.")
                else:
                    conn = get_portfolio_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT id, password_hash FROM users WHERE username = %s",
                        (username.strip().lower(),)
                    )
                    row = cursor.fetchone()
                    conn.close()

                    if row and verify_password(row[1], mdp):
                        user_id = row[0]
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.user_username = username.strip()

                        # Chargement du premier portefeuille de l'utilisateur
                        from data.database import get_portfolios, create_portfolio as _cp
                        ptfs = get_portfolios(user_id)
                        if not ptfs:
                            pid = _cp(user_id, "Principal", 10000.0)
                        else:
                            pid = ptfs[0][0]
                        p = Portfolio(initial_cash=10000.0)
                        p.load_from_db(user_id, pid)
                        st.session_state.portfolio = p
                        st.session_state[f"portfolio_{pid}"] = p

                        st.success("✅ Connexion réussie !")
                        st.session_state.show_onboarding = True
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")

        # ── Onglet     tion ────────────────────────────────────────────────
        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            new_username = st.text_input(
                "Nom d'utilisateur", placeholder="Votre pseudo", key="reg_email"
            )
            new_mdp = st.text_input(
                "Mot de passe", type="password",
                placeholder="Minimum 4 caractères", key="reg_mdp"
            )
            new_mdp_c = st.text_input(
                "Confirmer le mot de passe", type="password",
                placeholder="••••••••", key="reg_mdp_c"
            )

            st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
            capital_initial = st.slider(
                "💰 Capital de départ (€)",
                min_value=1_000,
                max_value=1_000_000,
                value=10_000,
                step=1_000,
                key="reg_capital",
                help="Montant fictif avec lequel vous commencerez à trader."
            )
            st.markdown(
                f"<p style='color:#06B6D4; font-weight:600; font-family:Inter,sans-serif;"
                f"margin:4px 0 12px;'>Capital sélectionné : {capital_initial:,.0f} €</p>",
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("Créer mon compte", type="primary", use_container_width=True, key="btn_reg"):
                if not new_username or not new_mdp:
                    st.error("Veuillez remplir tous les champs.")
                elif len(new_username.strip()) < 3:
                    st.error("Le nom d'utilisateur doit faire au moins 3 caractères.")
                elif len(new_mdp) < 4:
                    st.error("Le mot de passe doit faire au moins 4 caractères.")
                elif new_mdp != new_mdp_c:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    conn = get_portfolio_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT id FROM users WHERE username = %s",
                        (new_username.strip().lower(),)
                    )
                    if cursor.fetchone():
                        st.error("Ce nom d'utilisateur est déjà pris.")
                        conn.close()
                    else:
                        pwd_hash = hash_password(new_mdp)
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        cursor.execute(
                            "INSERT INTO users (username, password_hash, created_at) VALUES (%s, %s, %s) RETURNING id",
                            (new_username.strip().lower(), pwd_hash, now_str)
                        )
                        
                        user_id = cursor.fetchone()[0]
                        
                        conn.commit()
                        conn.close()
                        
                        from data.database import create_portfolio as _cp2
                        pid_new = _cp2(user_id, "Principal", float(capital_initial))
                        p = Portfolio(initial_cash=float(capital_initial))
                        p.save_to_db(user_id, pid_new)

                        st.success("🎉 Compte créé avec succès ! Connecte-toi maintenant.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
#  UTILISATEUR CONNECTÉ — Portefeuille en session
# ═══════════════════════════════════════════════════════════════════════════════
if "portfolio" not in st.session_state:
    _uid = st.session_state.user_id
    from data.database import get_portfolios as _gp, create_portfolio as _cp3
    _ptfs = _gp(_uid)
    if not _ptfs:
        _pid = _cp3(_uid, "Principal", 10000.0)
    else:
        _pid = _ptfs[0][0]
    p = Portfolio(initial_cash=10000.0)
    p.load_from_db(_uid, _pid)
    st.session_state.portfolio = p
    st.session_state[f"portfolio_{_pid}"] = p

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo + nom de la plateforme
    st.markdown("""
    <div style='display:flex; align-items:center; gap:10px; padding:6px 0 18px;'>
      <div style='width:36px; height:36px; background:linear-gradient(135deg,#06B6D4,#2563EB);
                  border-radius:9px; display:flex; align-items:center; justify-content:center;
                  font-size:1.2rem;'>📈</div>
      <span style='font-family:Inter,sans-serif; font-size:1.05rem; font-weight:700;
                   background:linear-gradient(90deg,#06B6D4,#7C3AED);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
        TradeDesk
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Identité de l'utilisateur
    email_display = st.session_state.get("user_username") or ""
    st.markdown(f"""
    <div style='background:#111318; border:1px solid #1E2028; border-radius:12px;
                padding:12px 14px; margin-bottom:16px;'>
      <p style='margin:0; font-size:0.75rem; color:#8A94A6; font-family:Inter,sans-serif;'>
        Connecté en tant que
      </p>
      <p style='margin:4px 0 0; font-size:0.9rem; font-weight:600; color:#E8ECF0;
                font-family:Inter,sans-serif; word-break:break-all;'>
        {email_display}
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("""
    <p style='font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em;
              color:#5A6478; font-family:Inter,sans-serif; margin-bottom:10px;'>Navigation</p>
    """, unsafe_allow_html=True)

    nav_items = [
        ("↗", "Marché", "Cours en direct & analyse technique"),
        ("◈", "Portefeuille", "Ordres, positions & options"),
        ("⟳", "Backtesting", "Stratégies historiques"),
        ("◎", "Bot", "Trading automatique & ML"),
        ("∇", "Dérivés", "Pricing Black-Scholes & Greeks"),
        ("◻", "Documentation", "Guides & cours de finance"),
        ("◐", "Paramètres", "Gestion du compte"),
        ("◉", "Assistant", "Questions & conseils"),
    ]
    for icon, name, desc in nav_items:
        st.markdown(f"""
        <div style='background:#111318; border:1px solid #1E2028; border-radius:10px;
                    padding:10px 12px; margin-bottom:8px; cursor:default;'>
          <span style='font-size:1rem;'>{icon}</span>
          <span style='font-family:Inter,sans-serif; font-weight:600; font-size:0.88rem;
                       color:#E8ECF0; margin-left:6px;'>{name}</span>
          <p style='margin:3px 0 0; font-size:0.75rem; color:#5A6478;
                    font-family:Inter,sans-serif;'>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:0.78rem; color:#5A6478; font-family:Inter,sans-serif;
              margin:10px 0 14px;'>
      ↑ Utilise le menu <strong>Pages</strong> en haut de cette barre pour naviguer.
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("Se déconnecter", use_container_width=True, key="btn_logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_username = None
        st.session_state.show_welcome = False
        if "portfolio" in st.session_state:
            del st.session_state.portfolio
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE D'ACCUEIL PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

# ── Message de bienvenue post-login ──────────────────────────────────────────
if st.session_state.get("show_onboarding", False):
    st.session_state.show_onboarding = False

    prenom = (st.session_state.get("user_username") or "Trader").capitalize()
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(6,182,212,0.12),rgba(37,99,235,0.10));
                border:1px solid rgba(6,182,212,0.3); border-radius:18px;
                padding:28px 32px; margin-bottom:32px;'>
      <h2 style='margin:0 0 6px; font-family:Inter,sans-serif; font-size:1.6rem;
                 background:linear-gradient(90deg,#06B6D4,#7C3AED);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
        Bienvenue, {prenom} ! 👋
      </h2>
      <p style='color:#8A94A6; font-family:Inter,sans-serif; margin:0 0 24px;'>
        Voici ce que vous pouvez faire sur TradeDesk :
      </p>
      <div style='display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px;'>
        <div style='background:rgba(6,182,212,0.08); border:1px solid rgba(6,182,212,0.2);
                    border-radius:14px; padding:18px 16px; text-align:center;'>
          <div style='font-size:2rem; margin-bottom:8px;'>📊</div>
          <p style='color:#06B6D4; font-weight:700; font-family:Inter,sans-serif;
                    font-size:0.9rem; margin:0 0 4px;'>Suivre le marché</p>
          <p style='color:#8A94A6; font-family:Inter,sans-serif; font-size:0.78rem; margin:0;'>
            Graphiques en direct, VWAP, indicateurs techniques sur +1 000 actifs.
          </p>
        </div>
        <div style='background:rgba(124,58,237,0.08); border:1px solid rgba(124,58,237,0.2);
                    border-radius:14px; padding:18px 16px; text-align:center;'>
          <div style='font-size:2rem; margin-bottom:8px;'>💼</div>
          <p style='color:#7C3AED; font-weight:700; font-family:Inter,sans-serif;
                    font-size:0.9rem; margin:0 0 4px;'>Gérer votre portefeuille</p>
          <p style='color:#8A94A6; font-family:Inter,sans-serif; font-size:0.78rem; margin:0;'>
            Achetez, vendez, suivez vos positions actions et options en temps réel.
          </p>
        </div>
        <div style='background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.2);
                    border-radius:14px; padding:18px 16px; text-align:center;'>
          <div style='font-size:2rem; margin-bottom:8px;'>🔬</div>
          <p style='color:#22C55E; font-weight:700; font-family:Inter,sans-serif;
                    font-size:0.9rem; margin:0 0 4px;'>Backtester des stratégies</p>
          <p style='color:#8A94A6; font-family:Inter,sans-serif; font-size:0.78rem; margin:0;'>
            Testez vos règles de trading sur des données historiques avant de les appliquer.
          </p>
        </div>
        <div style='background:rgba(251,146,60,0.08); border:1px solid rgba(251,146,60,0.2);
                    border-radius:14px; padding:18px 16px; text-align:center;'>
          <div style='font-size:2rem; margin-bottom:8px;'>🤖</div>
          <p style='color:#FB923C; font-weight:700; font-family:Inter,sans-serif;
                    font-size:0.9rem; margin:0 0 4px;'>Automatiser avec un Bot</p>
          <p style='color:#8A94A6; font-family:Inter,sans-serif; font-size:0.78rem; margin:0;'>
            Laissez un robot passer vos ordres — stratégies SMA, RSI ou apprentissage automatique.
          </p>
        </div>
        <div style='background:rgba(244,63,94,0.08); border:1px solid rgba(244,63,94,0.2);
                    border-radius:14px; padding:18px 16px; text-align:center;'>
          <div style='font-size:2rem; margin-bottom:8px;'>📐</div>
          <p style='color:#F43F5E; font-weight:700; font-family:Inter,sans-serif;
                    font-size:0.9rem; margin:0 0 4px;'>Pricer des options</p>
          <p style='color:#8A94A6; font-family:Inter,sans-serif; font-size:0.78rem; margin:0;'>
            Visualisez la surface de volatilité et le prix d'options européennes en 3D.
          </p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Titre principal ───────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:32px;'>
  <h1 style='font-family:Inter,sans-serif; font-size:2rem; font-weight:800; margin:0 0 6px;
             background:linear-gradient(90deg,#F0F4F8,#8A94A6);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
    TradeDesk — Simulateur Boursier
  </h1>
  <p style='color:#5A6478; font-family:Inter,sans-serif; font-size:1rem; margin:0;'>
    Explorez les marchés financiers en toute sécurité, avec des données réelles.
  </p>
</div>
""", unsafe_allow_html=True)

# ── 5 cards horizontales présentant chaque onglet ────────────────────────────
tabs_info = [
    {
        "icon": "↗",
        "title": "Marché",
        "color_text": "#06B6D4",
        "color_bg": "rgba(6,182,212,0.07)",
        "color_border": "rgba(6,182,212,0.22)",
        "desc": (
            "Consultez les cours en direct sur plus de 1 000 actifs — actions, ETFs et indices. "
            "Affichez les graphiques en chandeliers avec le VWAP, adaptez la période et l'intervalle "
            "et identifiez les tendances en un coup d'œil."
        ),
    },
    {
        "icon": "◈",
        "title": "Portefeuille",
        "color_text": "#7C3AED",
        "color_bg": "rgba(124,58,237,0.07)",
        "color_border": "rgba(124,58,237,0.22)",
        "desc": (
            "Passez des ordres d'achat et de vente sur des actions ou des options européennes "
            "(Call / Put) pricées en temps réel. Suivez vos positions ouvertes, votre "
            "performance globale et consultez l'historique complet de vos transactions."
        ),
    },
    {
        "icon": "⟳",
        "title": "Backtesting",
        "color_text": "#22C55E",
        "color_bg": "rgba(34,197,94,0.07)",
        "color_border": "rgba(34,197,94,0.22)",
        "desc": (
            "Évaluez la rentabilité d'une stratégie sur des données historiques avant de vous "
            "lancer. Comparez SMA, RSI et VWAP en mode comparatif sur la même période."
        ),
    },
    {
        "icon": "◎",
        "title": "Bot de Trading",
        "color_text": "#FB923C",
        "color_bg": "rgba(251,146,60,0.07)",
        "color_border": "rgba(251,146,60,0.22)",
        "desc": (
            "Activez un algorithme qui passe des ordres automatiquement. Choisissez "
            "entre SMA, RSI, VWAP, ou un modèle Machine Learning (Random Forest) "
            "avec optimisation Grid Search."
        ),
    },
    {
        "icon": "∇",
        "title": "Dérivés",
        "color_text": "#F43F5E",
        "color_bg": "rgba(244,63,94,0.07)",
        "color_border": "rgba(244,63,94,0.22)",
        "desc": (
            "Pricez des options européennes avec le modèle Black-Scholes (1973). "
            "Visualisez la surface 3D du prix en fonction du Strike et de la Maturité, "
            "et analysez les Greeks : Delta, Gamma, Vega, Theta, Rho."
        ),
    },
]

for info in tabs_info:
    st.markdown(f"""
    <div style='background:{info["color_bg"]}; border:1px solid {info["color_border"]};
                border-radius:16px; padding:22px 26px; margin-bottom:16px;
                display:flex; align-items:flex-start; gap:20px;'>
      <div style='font-size:2.2rem; flex-shrink:0; margin-top:2px;'>{info["icon"]}</div>
      <div>
        <p style='margin:0 0 6px; font-family:Inter,sans-serif; font-size:1.05rem;
                  font-weight:700; color:{info["color_text"]};'>{info["title"]}</p>
        <p style='margin:0; font-family:Inter,sans-serif; font-size:0.88rem;
                  color:#8A94A6; line-height:1.55;'>{info["desc"]}</p>
      </div>
    </div>
    """, unsafe_allow_html=True)
