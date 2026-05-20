import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

import data.data as data_mod
import simulation.simulation as sim
from equities.equities import Portfolio
from data.database import PORTFOLIO_DB_PATH

from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui

# ── Garde d'authentification ──────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

p = st.session_state.portfolio
user_id = st.session_state.user_id

def save():
    """Sauvegarde le portefeuille de l'utilisateur actuel dans SQLite."""
    p.save_to_db(user_id, PORTFOLIO_DB_PATH)

def add_log(message: str):
    """Ajoute une entrée horodatée à la console de logs."""
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.bot_logs.append(f"[{ts}] {message}")

# ── Initialisation de la session ──────────────────────────────────────────────
if "bot_logs" not in st.session_state:
    st.session_state.bot_logs = []
if "bot_analysis" not in st.session_state:
    st.session_state.bot_analysis = None   # résultats de la dernière analyse
if "bot_order_done" not in st.session_state:
    st.session_state.bot_order_done = False

# ── En-tête ───────────────────────────────────────────────────────────────────
st.title("🤖 Bot de Trading Automatique")
st.caption(
    "Choisis un actif et une stratégie, clique sur **Analyser** pour obtenir un rapport complet, "
    "puis autorise ou non l'exécution de l'ordre."
)

# ── Configuration ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    bot_asset = st.selectbox("Actif à trader", list(data_mod.MARKET.keys()), key="bot_asset_sel")
with col2:
    bot_strat_label = st.selectbox(
        "Stratégie",
        [
            "SMA (Moyennes Mobiles)",
            "RSI (Indicateur de force relative)",
            "Machine Learning (Random Forest)",
        ],
        key="bot_strat_sel",
    )

# Mappage label → code interne
if "SMA" in bot_strat_label:
    bot_strat = "SMA"
    st.info(
        "**SMA** : Achat si SMA(5) > SMA(15) (tendance haussière), "
        "vente si SMA(5) < SMA(15) (tendance baissière)."
    )
elif "RSI" in bot_strat_label:
    bot_strat = "RSI"
    st.info("**RSI** : Achat si RSI < 35 (zone de survente), vente si RSI > 65 (zone de surachat).")
else:
    bot_strat = "ML_RF"
    st.info(
        "**Machine Learning (Random Forest)** : Modèle prédictif entraîné en direct sur 1 an "
        "d'historique journalier. Il analyse les rendements, les moyennes mobiles, le RSI et la "
        "volatilité glissante pour anticiper la tendance à 3 jours."
    )

st.divider()

# ── Bouton Analyser ───────────────────────────────────────────────────────────
if st.button("🔍 Analyser", type="primary", use_container_width=True):
    st.session_state.bot_order_done = False
    st.session_state.bot_analysis = None

    with st.spinner("🧠 Analyse en cours… Récupération des données de marché."):
        try:
            hist_p = "1y" if bot_strat == "ML_RF" else "1mo"
            df = data_mod.recuperer_historique(bot_asset, hist_p, "1d")

            if df.empty or len(df) < 10:
                st.error("❌ Données de marché insuffisantes pour analyser cet actif.")
                add_log(f"Analyse échouée : données insuffisantes pour {bot_asset}.")
                st.stop()

            close = df["Close"]
            current_price = float(close.iloc[-1])

            # ── Calcul de la volatilité annualisée ────────────────────────────
            returns = close.pct_change().dropna()
            volatility = float(returns.std() * np.sqrt(252) * 100)  # en %

            # ── Calcul des indicateurs selon la stratégie ─────────────────────
            signal = 0        # 0 = NEUTRE, 1 = ACHAT, -1 = VENTE
            indicators = {}
            ml_prob_up = None

            if bot_strat == "SMA":
                sma5  = float(sim.calculate_sma(close, 5).iloc[-1])
                sma15 = float(sim.calculate_sma(close, 15).iloc[-1])
                indicators["SMA(5)"]  = f"{sma5:.2f} €"
                indicators["SMA(15)"] = f"{sma15:.2f} €"
                if sma5 > sma15:
                    signal = 1
                elif sma5 < sma15:
                    signal = -1

            elif bot_strat == "RSI":
                rsi_val = float(sim.calculate_rsi(close, 7).iloc[-1])
                indicators["RSI(7)"] = f"{rsi_val:.1f}"
                if rsi_val < 35:
                    signal = 1
                elif rsi_val > 65:
                    signal = -1

            elif bot_strat == "ML_RF":
                # Features identiques à celles de TradingBot
                ret1  = close.pct_change()
                ret3  = close.pct_change(3)
                ret5  = close.pct_change(5)
                sma5s = sim.calculate_sma(close, 5)
                sma15s = sim.calculate_sma(close, 15)
                sma_ratio = sma5s / sma15s
                rsi14  = sim.calculate_rsi(close, 14)
                vol10  = ret1.rolling(10).std()

                features = pd.DataFrame({
                    "ret1": ret1, "ret3": ret3, "ret5": ret5,
                    "sma_ratio": sma_ratio, "rsi": rsi14, "vol10": vol10,
                })
                target = (close.shift(-3) > close).astype(int)
                dataset = features.copy()
                dataset["target"] = target
                dataset = dataset.dropna()

                if len(dataset) < 25:
                    st.error("❌ Historique insuffisant pour entraîner le modèle.")
                    add_log("ML : historique insuffisant.")
                    st.stop()

                X_train = dataset.drop(columns=["target"])
                y_train = dataset["target"]
                latest  = features.iloc[[-1]].ffill().fillna(0.0)

                clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
                clf.fit(X_train, y_train)

                pred = clf.predict(latest)[0]
                prob = clf.predict_proba(latest)[0]
                ml_prob_up = float(prob[1] * 100)

                indicators["Probabilité de hausse (3j)"] = f"{ml_prob_up:.1f} %"
                indicators["SMA(5)"]  = f"{float(sma5s.iloc[-1]):.2f} €"
                indicators["RSI(14)"] = f"{float(rsi14.iloc[-1]):.1f}"

                if pred == 1 and ml_prob_up > 55.0:
                    signal = 1
                elif pred == 0 or ml_prob_up < 45.0:
                    signal = -1
                else:
                    signal = 0

                        # ── Calcul de l'action proposée ─────────────────────────
            if signal == 1:
                explanation = (
                    f"🍯 **Analyse du Bot** : J'ai détecté une **opportunité d'achat forte** sur {bot_asset}. "
                    f"Les indicateurs de la stratégie **{bot_strat_label}** sont tous au vert. "
                    f"Cependant, la volatilité historique s'élève à **{volatility:.1f}%**, ce qui implique un risque de fluctuation modéré à court terme. "
                    f"Je te conseille d'investir de façon responsable en acceptant la possibilité que le marché fluctue de ce pourcentage."
                )
            elif signal == -1:
                explanation = (
                    f"⚠️ **Analyse du Bot** : Mes algorithmes pointent vers un **repli imminent** sur {bot_asset}. "
                    f"Il est temps de se désengager partiellement ou totalement pour sécuriser tes profits ou limiter la casse, car la volatilité de **{volatility:.1f}%** "
                    f"pourrait amplifier cette tendance baissière."
                )
            else:
                explanation = (
                    f"⏸️ **Analyse du Bot** : Le marché de {bot_asset} est actuellement **neutre**. "
                    f"Je ne détecte aucune tendance directionnelle fiable sur la base des indicateurs de {bot_strat_label}. "
                    f"Mieux vaut conserver tes liquidités pour le moment."
                )

            # Sauvegarde dans la session
            st.session_state.bot_analysis = {
                "asset": bot_asset,
                "strat": bot_strat,
                "signal": signal,
                "current_price": current_price,
                "volatility": volatility,
                "indicators": indicators,
                "proposed": proposed,
                "explanation": explanation,
            }
            add_log(
                f"Analyse {bot_strat} sur {bot_asset} : signal="
                + {1: "ACHAT", -1: "VENTE", 0: "NEUTRE"}[signal]
            )

        except Exception as e:
            st.error(f"❌ Erreur lors de l'analyse : {e}")
            add_log(f"Erreur analyse : {e}")

# ── Affichage du rapport ───────────────────────────────────────────────────────
analysis = st.session_state.get("bot_analysis")

if analysis and analysis["asset"] == bot_asset and analysis["strat"] == bot_strat:
    signal    = analysis["signal"]
    price     = analysis["current_price"]
    vol       = analysis["volatility"]
    indicators = analysis["indicators"]
    proposed  = analysis["proposed"]

    SIGNAL_LABELS = {1: "✅ ACHAT", -1: "📤 VENTE", 0: "➖ NEUTRE"}
    SIGNAL_COLORS = {1: "🟢", -1: "🔴", 0: "🟡"}

    with st.expander(
        f"📊 Rapport d'analyse — {bot_asset} ({bot_strat_label})", expanded=True
    ):
        # Signal principal et Explication Narrative du Bot
        st.markdown(
            f"### Signal détecté : {SIGNAL_COLORS[signal]} **{SIGNAL_LABELS[signal]}**"
        )
        st.info(analysis["explanation"])

        # Indicateurs
        st.markdown("#### 📐 Indicateurs techniques")
        ind_cols = st.columns(len(indicators) if indicators else 1)
        for i, (k, v) in enumerate(indicators.items()):
            ind_cols[i].metric(k, v)

        # Cours & volatilité
        st.markdown("#### 💹 Cours & Risque")
        c1, c2 = st.columns(2)
        c1.metric("Cours actuel", f"{price:.2f} €")
        c2.metric(
            "Volatilité annualisée",
            f"{vol:.1f} %",
            help="Calculée sur les rendements journaliers annualisés (√252). Représente le risque historique de l'actif.",
        )

        # Action proposée
        st.markdown("#### 📋 Action proposée")
        if signal == 1 and proposed and proposed["qty"] > 0:
            st.success(
                f"**Acheter {proposed['qty']} unité(s)** de **{bot_asset}** "
                f"à **{proposed['prix']:.2f} €** — Montant total estimé : **{proposed['montant']:,.2f} €** "
                f"(commission 1% incluse)"
            )
        elif signal == -1 and proposed and proposed["qty"] > 0:
            st.warning(
                f"**Vendre {proposed['qty']} unité(s)** de **{bot_asset}** "
                f"à **{proposed['prix']:.2f} €** — Montant estimé : **{proposed['montant']:,.2f} €**"
            )
        elif signal == -1 and proposed and proposed["qty"] == 0:
            st.warning("Signal VENTE détecté, mais tu ne détiens aucune position sur cet actif.")
        else:
            st.info("Aucune transaction conseillée. Le marché est en phase neutre pour cet actif.")

    # ── Boutons d'autorisation ─────────────────────────────────────────────────
    if not st.session_state.bot_order_done:
        if signal == 1 and proposed and proposed["qty"] > 0:
            if st.button(
                f"✅ Autoriser l'achat de {proposed['qty']} unité(s) de {bot_asset}",
                type="primary",
                use_container_width=True,
            ):
                try:
                    msg = p.buy(bot_asset, proposed["qty"], proposed["prix"])
                    save()
                    add_log(f"Ordre ACHAT autorisé par l'utilisateur → {msg}")
                    st.session_state.bot_order_done = True
                    st.session_state.bot_analysis = None
                    st.success(f"✅ Ordre exécuté : {msg}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de l'exécution de l'ordre : {e}")
                    add_log(f"Erreur ordre achat : {e}")

        elif signal == -1 and proposed and proposed["qty"] > 0:
            if st.button(
                f"📤 Autoriser la vente de {proposed['qty']} unité(s) de {bot_asset}",
                type="primary",
                use_container_width=True,
            ):
                try:
                    msg = p.sell(bot_asset, proposed["qty"], proposed["prix"])
                    save()
                    add_log(f"Ordre VENTE autorisé par l'utilisateur → {msg}")
                    st.session_state.bot_order_done = True
                    st.session_state.bot_analysis = None
                    st.success(f"📤 Ordre exécuté : {msg}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de l'exécution de l'ordre : {e}")
                    add_log(f"Erreur ordre vente : {e}")

        elif signal == 0:
            st.info(
                "ℹ️ Signal NEUTRE — Aucune action n'est nécessaire pour le moment. "
                "Relance une analyse plus tard pour détecter un nouveau signal."
            )

    else:
        st.success("✅ Ordre déjà exécuté pour cette analyse. Lance une nouvelle analyse pour continuer.")

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
