"""
4_🤖_Bot.py — Bot de trading automatique
"""
import streamlit as st
import os, sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import data.data as data_mod
from bot.bot import TradingBot
from data.database import PORTFOLIO_DB_PATH

if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

p = st.session_state.portfolio

def save():
    p.save_to_db(PORTFOLIO_DB_PATH)

st.title("🤖 Bot de Trading Automatique")
st.caption("Le bot analyse les indicateurs et exécute des ordres sur ton portefeuille simulé.")

# ── Configuration ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    bot_asset = st.selectbox("Actif à trader", list(data_mod.MARKET.keys()))
with col2:
    bot_strat = st.selectbox("Stratégie", ["SMA", "RSI"])

# ── Description de la stratégie ───────────────────────────────────────────────
if bot_strat == "SMA":
    st.info("**SMA** : Croisement de moyennes mobiles. Achat quand SMA(5) > SMA(15), vente sinon.")
else:
    st.info("**RSI** : Force relative. Achat si RSI < 35 (survente), vente si RSI > 65 (surachat).")

st.divider()

# ── État du bot ───────────────────────────────────────────────────────────────
if "bot_active" not in st.session_state:
    st.session_state.bot_active = False
if "bot_logs"   not in st.session_state:
    st.session_state.bot_logs   = []

status_col, btn1, btn2 = st.columns([2, 1, 1])
with status_col:
    status = "🟢 ACTIF" if st.session_state.bot_active else "🔴 ARRÊTÉ"
    st.markdown(f"**État du bot :** {status}")
with btn1:
    if st.button("▶️ Démarrer", type="primary", use_container_width=True):
        st.session_state.bot_active = True
        st.session_state.bot_logs.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Bot démarré sur {bot_asset} ({bot_strat})"
        )
with btn2:
    if st.button("⏹ Arrêter", use_container_width=True):
        st.session_state.bot_active = False
        st.session_state.bot_logs.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Bot arrêté."
        )

# ── Exécution d'une itération ─────────────────────────────────────────────────
if st.session_state.bot_active:
    with st.spinner("🧠 Analyse du marché en cours…"):
        my_bot       = TradingBot(p, bot_strat)
        my_bot.logs  = st.session_state.bot_logs
        result       = my_bot.run_one_iteration(bot_asset, "1mo", "1d")
        st.session_state.bot_logs = my_bot.logs
        save()

    if "Achat" in result or "ACHAT" in result:
        st.success(f"✅ {result}")
    elif "Vente" in result or "vendu" in result.lower():
        st.warning(f"📤 {result}")
    else:
        st.info(f"📊 {result}")

    if st.button("🔁 Exécuter une nouvelle itération"):
        st.rerun()

# ── Console de logs ───────────────────────────────────────────────────────────
st.divider()
st.subheader("📋 Console de trading")
col_log, col_clr = st.columns([5, 1])
with col_clr:
    if st.button("🗑️ Vider", use_container_width=True):
        st.session_state.bot_logs = []
        st.rerun()

logs_text = "\n".join(reversed(st.session_state.bot_logs[-50:]))
st.text_area("Logs", logs_text, height=300, label_visibility="collapsed")
