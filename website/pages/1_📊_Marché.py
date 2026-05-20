"""
1_📊_Marché.py — Page Marché : cours en direct + analyse technique avancée
"""
import streamlit as st
import pandas as pd
import os, sys, time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import data.data as data_mod
import greeks.greeks as grk
import visualisation.visualisation as vis

# ── Guard : doit être connecté ────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

st.title("📊 Marché — Cours & Analyse Technique")

# ── Sélection actif ───────────────────────────────────────────────────────────
asset_names  = list(data_mod.MARKET.keys())
col_sel, col_per, col_int = st.columns([3, 1.5, 1.5])
with col_sel:
    selected = st.selectbox("Actif à analyser", asset_names)
with col_per:
    period   = st.selectbox("Période", ["1d","5d","1mo","3mo","6mo","1y","2y","5y"], index=2)
with col_int:
    interval = st.selectbox("Intervalle", ["1m","5m","15m","1h","1d","1wk"], index=4)

st.divider()

# ── Onglets ───────────────────────────────────────────────────────────────────
tab_rt, tab_hist, tab_stats, tab_dist, tab_corr = st.tabs([
    "⚡ Temps Réel", "📈 Historique", "📐 Statistiques", "📉 Rendements", "🔗 Corrélation"
])

# ─────────────────────── TAB 1 : TEMPS RÉEL ──────────────────────────────────
with tab_rt:
    st.subheader(f"⚡ Cours en direct — {selected}")
    st.caption("Données intraday 1 minute — rafraîchi toutes les 30 secondes")

    placeholder_price  = st.empty()
    placeholder_chart  = st.empty()
    placeholder_gauge  = st.empty()

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

        with placeholder_price.container():
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Cours actuel",  f"{price_rt:.2f}",   f"{delta:+.2f} ({delta_pct:+.2f}%)")
            c2.metric("Ouverture",     f"{open_price:.2f}")
            c3.metric("Plus haut (J)", f"{df_rt['High'].max():.2f}")
            c4.metric("Plus bas (J)",  f"{df_rt['Low'].min():.2f}")

        with placeholder_chart.container():
            st.plotly_chart(vis.plot_realtime(df_rt, selected, price_rt), use_container_width=True)

        # RSI sur données intraday
        delta_s = df_rt["Close"].diff()
        gain_s  = delta_s.clip(lower=0).rolling(14).mean()
        loss_s  = (-delta_s.clip(upper=0)).rolling(14).mean()
        rs_s    = gain_s / loss_s.replace(0, float("nan"))
        rsi_rt  = float((100 - 100 / (1 + rs_s)).iloc[-1])
        with placeholder_gauge.container():
            st.plotly_chart(vis.plot_rsi_gauge(rsi_rt, selected), use_container_width=True)
    else:
        st.warning("Données intraday indisponibles. Marché peut-être fermé.")

    if st.button("🔄 Rafraîchir maintenant", key="rt_refresh"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────── TAB 2 : HISTORIQUE ──────────────────────────────────
with tab_hist:
    st.subheader(f"📈 Historique — {selected} ({period} / {interval})")
    try:
        df_hist = data_mod.recuperer_historique(selected, period, interval)
        st.plotly_chart(vis.plot_candlestick(df_hist, selected), use_container_width=True)
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")

# ─────────────────────── TAB 3 : STATISTIQUES ────────────────────────────────
with tab_stats:
    st.subheader(f"📐 Statistiques — {selected}")
    try:
        df_s   = data_mod.recuperer_historique(selected, "1y", "1d")
        close  = df_s["Close"]
        is_cry = "USD" in data_mod.MARKET.get(selected, "")
        vol    = grk.calculate_historical_volatility(close, is_crypto=is_cry)
        sharpe = grk.calculate_sharpe_ratio(close,          is_crypto=is_cry)

        spy_df = data_mod.recuperer_historique("S&P 500 ETF (Tradable)", "1y", "1d")
        beta   = grk.calculate_beta(close, spy_df["Close"])

        rets   = close.pct_change().dropna()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Volatilité ann.",    f"{vol*100:.2f} %")
        c2.metric("Ratio de Sharpe",    f"{sharpe:.2f}")
        c3.metric("Bêta (vs S&P 500)",  f"{beta:.2f}")
        c4.metric("Rendement 1 an",     f"{((close.iloc[-1]/close.iloc[0])-1)*100:.2f} %")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Max",      f"{close.max():.2f}")
        c6.metric("Min",      f"{close.min():.2f}")
        c7.metric("Skewness", f"{rets.skew():.2f}")
        c8.metric("Kurtosis", f"{rets.kurtosis():.2f}")

        # Tableau des données
        st.dataframe(df_s.tail(30).style.format("{:.2f}"), use_container_width=True)
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────── TAB 4 : DISTRIBUTION ────────────────────────────────
with tab_dist:
    st.subheader(f"📉 Distribution des Rendements — {selected}")
    try:
        df_d  = data_mod.recuperer_historique(selected, "1y", "1d")
        st.plotly_chart(vis.plot_returns_distribution(df_d["Close"], selected), use_container_width=True)
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────── TAB 5 : CORRÉLATION ─────────────────────────────────
with tab_corr:
    st.subheader("🔗 Matrice de Corrélation")
    default_assets = ["Apple Inc.", "Microsoft", "Nvidia", "Amazon", "Tesla, Inc.",
                      "Alphabet Inc. (Class A)", "Meta Platforms", "JPMorgan Chase", "Berkshire Hathaway"]
    valid_assets   = [a for a in default_assets if a in data_mod.MARKET]
    corr_assets    = st.multiselect("Actifs à comparer", asset_names, default=valid_assets[:6])

    if len(corr_assets) < 2:
        st.info("Sélectionne au moins 2 actifs.")
    else:
        with st.spinner("Chargement des données…"):
            prices_dict = {}
            for a in corr_assets:
                try:
                    df_c = data_mod.recuperer_historique(a, "1y", "1d")
                    prices_dict[a] = df_c["Close"]
                except Exception:
                    pass
        if len(prices_dict) >= 2:
            st.plotly_chart(vis.plot_correlation_heatmap(prices_dict), use_container_width=True)
