import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from website.components.ui_config import set_global_ui

set_global_ui()

import streamlit as st
import random
import re
import difflib

if not st.session_state.get("logged_in", False):
    st.warning("Connecte-toi depuis la page d'accueil.")
    st.stop()

st.title("Assistant TradeDesk")
st.caption("Posez vos questions sur la finance, les graphiques ou votre portefeuille.")

# ── Base de connaissances (importée du module) ─────────────────────────────────
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from website.components.assistant_sidebar import generate_response, KNOWLEDGE_BASE, ALL_TOPICS
except ImportError:
    KNOWLEDGE_BASE = {}
    ALL_TOPICS = []
    def generate_response(q, p):
        return "Assistant temporairement indisponible."

# ── Interface chat ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Bonjour ! Je suis l'assistant TradeDesk.\n\n"
            "Je peux vous aider à :\n"
            "- **Expliquer** un concept financier : *'C'est quoi le VWAP ?'*, *'Explique le Sharpe'*\n"
            "- **Naviguer** dans l'application : *'Comment utiliser le Bot ?'*\n"
            "- **Consulter** votre portefeuille : *'Mon solde ?'*, *'Combien j'ai ?'*\n"
            "- **Calculer** : *'100 × 1.05'*, *'5% de 2000'*\n"
            "- **Conseiller** : *'Quelle action acheter ?'*"
        )
    })

# Affichage de l'historique
chat_container = st.container(height=520)
for message in st.session_state.messages:
    with chat_container.chat_message(message["role"]):
        st.markdown(message["content"])

# Saisie utilisateur
if user_input := st.chat_input("Posez une question sur la finance ou votre portefeuille..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with chat_container.chat_message("user"):
        st.markdown(user_input)

    portfolio = st.session_state.get("portfolio")
    if portfolio is None:
        response = "Connecte-toi d'abord pour accéder aux fonctionnalités personnalisées."
    else:
        response = generate_response(user_input, portfolio)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with chat_container.chat_message("assistant"):
        st.markdown(response)

# Suggestions rapides
st.markdown("---")
st.markdown("**Suggestions rapides :**")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
suggestions = [
    ("Mon portefeuille", "Mon portefeuille"),
    ("C'est quoi le RSI ?", "rsi"),
    ("Comment utiliser le Bot ?", "bot"),
    ("Quelle action acheter ?", "conseil"),
]
for i, (label, query) in enumerate(suggestions):
    col = [col_s1, col_s2, col_s3, col_s4][i]
    with col:
        if st.button(label, use_container_width=True, key=f"sugg_{i}"):
            st.session_state.messages.append({"role": "user", "content": label})
            portfolio = st.session_state.get("portfolio")
            response = generate_response(label, portfolio) if portfolio else "Connecte-toi pour utiliser cette fonctionnalité."
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Effacer la conversation
if st.session_state.messages:
    if st.button("Effacer la conversation", use_container_width=False):
        st.session_state.messages = []
        st.rerun()
