"""
1_📊_Marché.py — Page Marché : cours en direct + analyse technique et quantitative
==============================================================================

Cette page affiche les cours de la bourse en temps réel ou historique et permet de faire :
1. Un suivi intraday temps réel 1 min avec VWAP et jauge de force relative (RSI).
2. Des graphiques en chandeliers japonais avec indicateurs (Moyennes Mobiles, Bandes de Bollinger, RSI).
3. Une analyse de la volatilité historique glissante et des anomalies de volumes (pics de volume).
4. Des statistiques descriptives complètes sur l'actif (Sharpe, Bêta vs S&P 500, Skewness, Kurtosis).
5. L'étude de la distribution empirique des rendements journaliers.
6. L'étude de la corrélation historique des rendements d'un panier d'actifs.

Relations avec les autres modules :
----------------------------------
- data.data : gère l'extraction des données depuis Yahoo Finance et les met en cache.
- greeks.greeks : calcule les indicateurs quantitatifs (volatilité, ratio de Sharpe, Bêta).
- visualisation.visualisation : génère les graphiques interactifs en Plotly.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
import numpy as np

import data.data as data_mod
import greeks.greeks as grk
import visualisation.visualisation as vis

from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui

set_global_ui()
render_assistant()

# ── Guard : doit être connecté ────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

st.title("📊 Marché — Cours & Analyse Technique")

# ── Sélection actif ───────────────────────────────────────────────────────────
asset_names  = list(data_mod.MARKET.keys())
col_sel, col_per, col_int = st.columns([3, 1.5, 1.5])
with col_sel:
    selected = st.selectbox(
        "Actif à analyser", asset_names,
        help="Sélectionnez l'actif boursier que vous souhaitez étudier."
    )
with col_per:
    period   = st.selectbox(
        "Période", ["1d","5d","1mo","3mo","6mo","1y","2y","5y"], index=2,
        help="L'étendue temporelle totale de l'historique récupéré."
    )
with col_int:
    interval = st.selectbox(
        "Intervalle", ["1m","5m","15m","1h","1d","1wk"], index=4,
        help="La durée que représente chaque bougie sur le graphique."
    )

st.divider()

# ── Onglets de navigation ─────────────────────────────────────────────────────
tab_rt, tab_hist, tab_vvol, tab_stats, tab_dist, tab_corr = st.tabs([
    "⚡ Temps Réel", "📈 Historique", "📊 Volatilité & Volume",
    "📐 Statistiques", "📉 Rendements", "🔗 Corrélation"
])

# ─────────────────────── TAB 1 : TEMPS RÉEL ──────────────────────────────────
with tab_rt:
    st.subheader(f"⚡ Cours en direct — {selected}")
    st.caption("Données intraday 1 minute — rafraîchi toutes les 30 secondes")

    col_scale, col_empty = st.columns([3, 1])
    with col_scale:
        scale_mode = st.radio(
            "Échelle de l'axe Y",
            ["Automatique", "Zoom serré (Min/Max)", "Logarithmique"],
            horizontal=True,
            key=f"scale_{selected}"
        )
        y_mode = "Auto"
        if "Zoom" in scale_mode:
            y_mode = "Zoom serré"
        elif "Log" in scale_mode:
            y_mode = "Logarithmique"

    @st.cache_data(ttl=30)
    def fetch_intraday(name):
        try:
            df = data_mod.recuperer_historique(name, "1d", "1m", force_download=True)
            price = float(df["Close"].iloc[-1]) if not df.empty else None
            return df, price
        except Exception:
            return pd.DataFrame(), None

    df_rt, price_rt = fetch_intraday(selected)

    if price_rt is not None and not df_rt.empty:
        open_price = float(df_rt["Open"].iloc[0])
        delta      = price_rt - open_price
        delta_pct  = (delta / open_price) * 100

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cours actuel",  f"{price_rt:.2f}",   f"{delta:+.2f} ({delta_pct:+.2f}%)")
        c2.metric("Ouverture",     f"{open_price:.2f}")
        c3.metric("Plus haut (J)", f"{df_rt['High'].max():.2f}")
        c4.metric("Plus bas (J)",  f"{df_rt['Low'].min():.2f}")

        st.plotly_chart(
            vis.plot_realtime(df_rt, selected, price_rt, y_scale_mode=y_mode),
            use_container_width=True
        )

        # RSI intraday — nécessite min 15 bougies pour être significatif
        close_rt = df_rt["Close"].dropna()
        if len(close_rt) >= 15:
            try:
                delta_s = close_rt.diff()
                gain_s  = delta_s.clip(lower=0).rolling(14).mean()
                loss_s  = (-delta_s.clip(upper=0)).rolling(14).mean()
                rs_s    = gain_s / loss_s.replace(0, np.nan)
                rsi_series = 100 - 100 / (1 + rs_s)
                rsi_last = rsi_series.dropna().iloc[-1]
                if np.isfinite(rsi_last):
                    st.plotly_chart(
                        vis.plot_rsi_gauge(float(rsi_last), selected),
                        use_container_width=True
                    )
            except Exception:
                pass  # Jauge RSI non critique, on la saute silencieusement
    else:
        st.warning(
            "Données intraday indisponibles. "
            "Le marché correspondant à cet actif est probablement fermé actuellement."
        )

    if st.button("🔄 Rafraîchir maintenant", key="rt_refresh"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────── TAB 2 : HISTORIQUE ──────────────────────────────────
with tab_hist:
    st.subheader(f"📈 Historique — {selected} ({period} / {interval})")
    st.info(
        "💡 Astuce : Le graphique est 100% interactif. "
        "Utilisez la molette pour zoomer, tracez un rectangle pour cibler une zone, "
        "ou double-cliquez pour réinitialiser l'échelle."
    )
    try:
        df_hist = data_mod.recuperer_historique(selected, period, interval)
        if df_hist.empty:
            st.warning("Aucune donnée disponible pour cette combinaison période/intervalle.")
        else:
            # Vérification : yfinance renvoie parfois moins de données que SMA50 requiert
            if len(df_hist) < 20:
                st.warning(
                    f"Historique court ({len(df_hist)} bougies). "
                    "Certains indicateurs (SMA50, Bollinger) peuvent être incomplets."
                )
            st.plotly_chart(
                vis.plot_candlestick(df_hist, selected),
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")

# ─────────────────────── TAB 3 : VOLATILITÉ & VOLUME ─────────────────────────
with tab_vvol:
    st.subheader(f"📊 Analyse Quantitative : Volatilité et Volumes — {selected}")
    try:
        df_vv = data_mod.recuperer_historique(selected, "1y", "1d")
        if not df_vv.empty and len(df_vv) > 20:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.plotly_chart(
                    vis.plot_rolling_volatility(df_vv["Close"], selected),
                    use_container_width=True
                )
            with col_v2:
                # Vérifie que le Volume est non-nul avant de tracer les breakouts
                if "Volume" in df_vv.columns and df_vv["Volume"].sum() > 0:
                    st.plotly_chart(
                        vis.plot_volume_breakout(df_vv, selected),
                        use_container_width=True
                    )
                else:
                    st.info("Volume non disponible pour cet actif (certains ETFs/indices ne publient pas le volume).")
        else:
            st.info(
                "Données historiques insuffisantes pour tracer la volatilité glissante "
                "et les breakouts de volume (20 jours d'historique requis)."
            )
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────── TAB 4 : STATISTIQUES ────────────────────────────────
with tab_stats:
    st.subheader(f"📐 Statistiques & Ratio de Risque — {selected}")
    try:
        df_s   = data_mod.recuperer_historique(selected, "1y", "1d")
        if df_s.empty or len(df_s) < 20:
            st.warning("Données insuffisantes pour le calcul des statistiques (minimum 20 jours requis).")
        else:
            close  = df_s["Close"]
            is_cry = "USD" in data_mod.MARKET.get(selected, "")
            vol    = grk.calculate_historical_volatility(close, is_crypto=is_cry)
            sharpe = grk.calculate_sharpe_ratio(close, is_crypto=is_cry)

            # Bêta : gestion de l'erreur si SPY non dispo
            beta = 0.0
            try:
                spy_df = data_mod.recuperer_historique("S&P 500 ETF (Tradable)", "1y", "1d")
                if not spy_df.empty:
                    beta = grk.calculate_beta(close, spy_df["Close"])
            except Exception:
                beta = float("nan")

            rets = close.pct_change().dropna()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Volatilité ann.", f"{vol*100:.2f} %",
                      help="Risque statistique : amplitude de la variation des rendements sur l'année.")
            c2.metric("Ratio de Sharpe", f"{sharpe:.2f}",
                      help="Plus il est élevé (>1.0), plus la rentabilité est bonne par rapport au risque pris.")
            c3.metric("Bêta (vs S&P 500)", f"{beta:.2f}" if np.isfinite(beta) else "N/A",
                      help="Si Bêta > 1, l'actif est plus réactif et risqué que le marché. Si < 1, il est plus défensif.")
            c4.metric("Rendement 1 an", f"{((close.iloc[-1]/close.iloc[0])-1)*100:.2f} %",
                      help="Croissance brute de l'actif depuis la première donnée de l'année glissante.")

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Max 1 An",  f"{close.max():.2f}")
            c6.metric("Min 1 An",  f"{close.min():.2f}")
            c7.metric("Skewness",  f"{rets.skew():.2f}",
                      help="Asymétrie des rendements. Négatif indique un risque de krach soudain.")
            c8.metric("Kurtosis",  f"{rets.kurtosis():.2f}",
                      help="Mesure des extrêmes. > 3 = l'actif connaît régulièrement des chocs hors-norme.")

            st.markdown("#### 📋 Données historiques récentes")
            # Sélection des colonnes clés uniquement + format propre
            cols_show = [c for c in ["Open","High","Low","Close","Volume"] if c in df_s.columns]
            df_display = df_s[cols_show].tail(30).copy()
            df_display.columns = [c.capitalize() for c in df_display.columns]
            st.dataframe(df_display.style.format("{:.2f}", subset=[c for c in df_display.columns if c != "Volume"]),
                         use_container_width=True)
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────── TAB 5 : DISTRIBUTION ────────────────────────────────
with tab_dist:
    st.subheader(f"📉 Distribution des Rendements — {selected}")
    try:
        df_d = data_mod.recuperer_historique(selected, "1y", "1d")
        if df_d.empty or len(df_d) < 20:
            st.warning("Données insuffisantes pour tracer la distribution des rendements.")
        else:
            st.plotly_chart(
                vis.plot_returns_distribution(df_d["Close"], selected),
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────── TAB 6 : CORRÉLATION ─────────────────────────────────
with tab_corr:
    st.subheader("🔗 Matrice de Corrélation entre Rendements")
    default_assets = [
        "Apple Inc.", "Microsoft", "Nvidia", "Amazon", "Tesla, Inc.",
        "Alphabet Inc. (Class A)", "Meta Platforms", "JPMorgan Chase", "Berkshire Hathaway"
    ]
    valid_assets = [a for a in default_assets if a in data_mod.MARKET]
    corr_assets  = st.multiselect("Actifs à comparer", asset_names, default=valid_assets[:6])

    if len(corr_assets) < 2:
        st.info("Sélectionne au moins 2 actifs pour calculer la corrélation.")
    else:
        with st.spinner("Chargement des données…"):
            prices_dict = {}
            for a in corr_assets:
                try:
                    df_c = data_mod.recuperer_historique(a, "1y", "1d")
                    if not df_c.empty:
                        prices_dict[a] = df_c["Close"]
                except Exception:
                    pass
        if len(prices_dict) >= 2:
            st.plotly_chart(
                vis.plot_correlation_heatmap(prices_dict),
                use_container_width=True
            )
        else:
            st.warning("Impossible de charger les données pour au moins 2 actifs.")
