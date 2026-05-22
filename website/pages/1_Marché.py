import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
import numpy as np

import data.data as data_mod
import greeks.greeks as grk
import visualisation.visualisation as vis
from datetime import date, timedelta

from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui

set_global_ui()
render_assistant()

if not st.session_state.get("logged_in", False):
    st.warning("Connecte-toi depuis la page d'accueil.")
    st.stop()

st.title("Marché — Analyse des Marchés Financiers")

# ── Devise & taux de change ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def _eurusd():
    try:
        return data_mod.get_eurusd_rate()
    except Exception:
        return 1.08

eurusd_rate = _eurusd()

# ── Sélection actif ───────────────────────────────────────────────────────────
asset_names = list(data_mod.MARKET.keys())
col_sel, col_per, col_int = st.columns([3, 1.5, 1.5])
with col_sel:
    selected = st.selectbox(
        "Actif à analyser", asset_names,
        help="Sélectionnez l'actif boursier que vous souhaitez étudier."
    )
with col_per:
    period = st.selectbox(
        "Période", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2,
        help="L'étendue temporelle totale de l'historique récupéré."
    )
with col_int:
    interval = st.selectbox(
        "Intervalle", ["1m", "5m", "15m", "1h", "1d", "1wk"], index=4,
        help="La durée que représente chaque bougie sur le graphique."
    )

# ── Sélecteur de date personnalisé (affiché quand période = 1d) ───────────────
INTRADAY_INTERVALS = {"1m", "5m", "15m", "1h"}
LONG_PERIODS = {"6mo", "1y", "2y", "5y"}

custom_date = None
use_date_range = False

if period == "1d":
    col_date, col_info = st.columns([2, 3])
    with col_date:
        custom_date = st.date_input(
            "Choisir une journée spécifique",
            value=date.today(),
            max_value=date.today(),
            min_value=date.today() - timedelta(days=60),
            help="Par défaut : aujourd'hui. Choisissez une journée passée pour analyser une séance précise.",
        )
    with col_info:
        is_today = (custom_date == date.today())
        if is_today:
            st.info("📅 Affichage de la **séance d'aujourd'hui** (données en direct).")
        else:
            st.info(f"📅 Affichage de la séance du **{custom_date.strftime('%d/%m/%Y')}**.")
        if custom_date.weekday() >= 5:
            st.warning("Week-end sélectionné — les marchés boursiers sont fermés, les données peuvent être vides.")
    use_date_range = True

# Devise de l'actif
is_usd = data_mod.is_usd_asset(selected)
currency_label = "USD" if is_usd else "EUR"
currency_note = f"— coté en **{currency_label}**"
if is_usd:
    currency_note += f" (1 EUR ≈ {eurusd_rate:.4f} USD)"

st.caption(f"Actif sélectionné : **{selected}** {currency_note}")

if interval in INTRADAY_INTERVALS and period in LONG_PERIODS:
    st.warning(
        f"La combinaison **{period} / {interval}** dépasse la limite yfinance pour les données intraday "
        f"(max ~60 jours pour 1h, ~7 jours pour 1m/5m/15m). Réduisez la période ou augmentez l'intervalle."
    )


def load_df(asset, p, iv, date_override=None):
    """Charge l'historique selon la période ou une date précise."""
    if date_override is not None:
        start_str = date_override.strftime("%Y-%m-%d")
        end_str = (date_override + timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            return data_mod.recuperer_historique_date(asset, start_str, end_str, iv)
        except Exception:
            return pd.DataFrame()
    return data_mod.recuperer_historique(asset, p, iv)

st.divider()

# ── Onglets de navigation ─────────────────────────────────────────────────────
tab_rt, tab_hist, tab_vvol, tab_stats, tab_dist, tab_corr = st.tabs([
    "Temps Réel", "Historique", "Volatilité & Volume",
    "Statistiques", "Rendements", "Corrélation"
])

# ─────────────────────── TAB 1 : TEMPS RÉEL ──────────────────────────────────
with tab_rt:
    is_intraday = interval in INTRADAY_INTERVALS
    label_period = f"{period} / {interval}"
    if is_intraday:
        st.subheader(f"Cours en direct — {selected}")
        st.caption(f"Données {label_period} — rafraîchies automatiquement")
    else:
        st.subheader(f"Cours — {selected} ({label_period})")
        st.caption("Données historiques selon la période et l'intervalle sélectionnés")

    col_scale, _ = st.columns([3, 1])
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
    def fetch_realtime(name, p, iv, date_str=None):
        try:
            if date_str:
                end_str = (date.fromisoformat(date_str) + timedelta(days=1)).strftime("%Y-%m-%d")
                df = data_mod.recuperer_historique_date(name, date_str, end_str, iv)
            else:
                df = data_mod.recuperer_historique(name, p, iv, force_download=True)
            price = float(df["Close"].iloc[-1]) if not df.empty else None
            return df, price
        except Exception:
            return pd.DataFrame(), None

    _date_str = custom_date.strftime("%Y-%m-%d") if use_date_range and custom_date else None
    df_rt, price_rt = fetch_realtime(selected, period, interval, _date_str)

    if price_rt is not None and not df_rt.empty:
        open_price = float(df_rt["Open"].iloc[0])
        delta = price_rt - open_price
        delta_pct = (delta / open_price) * 100

        label_open = "Cours d'ouverture" if not is_intraday else "Ouverture (J)"
        label_high = f"Plus haut ({period})"
        label_low = f"Plus bas ({period})"

        sym = "USD" if is_usd else "EUR"
        def fmt(v):
            if is_usd:
                eur_val = v / eurusd_rate
                return f"{v:.2f} {sym}  ({eur_val:.2f} €)"
            return f"{v:.2f} €"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cours actuel", fmt(price_rt), f"{delta:+.2f} ({delta_pct:+.2f}%)")
        c2.metric(label_open, fmt(open_price))
        c3.metric(label_high, fmt(df_rt['High'].max()))
        c4.metric(label_low, fmt(df_rt['Low'].min()))

        st.plotly_chart(
            vis.plot_realtime(df_rt, selected, price_rt, y_scale_mode=y_mode),
            use_container_width=True
        )

        # RSI — nécessite min 15 bougies
        close_rt = df_rt["Close"].dropna()
        if len(close_rt) >= 15:
            try:
                delta_s = close_rt.diff()
                gain_s = delta_s.clip(lower=0).rolling(14).mean()
                loss_s = (-delta_s.clip(upper=0)).rolling(14).mean()
                rs_s = gain_s / loss_s.replace(0, np.nan)
                rsi_series = 100 - 100 / (1 + rs_s)
                rsi_last = rsi_series.dropna().iloc[-1]
                if np.isfinite(rsi_last):
                    st.plotly_chart(
                        vis.plot_rsi_gauge(float(rsi_last), selected),
                        use_container_width=True
                    )
            except Exception:
                pass
    else:
        st.warning(
            "Données indisponibles pour cette combinaison période/intervalle. "
            "Le marché est peut-être fermé, ou la combinaison dépasse les limites yfinance."
        )

    if st.button("Rafraîchir maintenant", key="rt_refresh"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────── TAB 2 : HISTORIQUE ──────────────────────────────────
with tab_hist:
    st.subheader(f"Historique — {selected} ({period} / {interval})")
    st.info(
        "Le graphique est 100 % interactif : molette pour zoomer, rectangle pour cibler "
        "une zone, double-clic pour réinitialiser l'échelle."
    )
    try:
        df_hist = load_df(selected, period, interval, custom_date if use_date_range else None)
        if df_hist.empty:
            st.warning("Aucune donnée disponible pour cette combinaison période/intervalle.")
        else:
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
    st.subheader(f"Volatilité et Volumes — {selected} ({period} / {interval})")
    try:
        df_vv = load_df(selected, period, interval, custom_date if use_date_range else None)
        if not df_vv.empty and len(df_vv) > 20:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.plotly_chart(
                    vis.plot_rolling_volatility(df_vv["Close"], selected),
                    use_container_width=True
                )
            with col_v2:
                if "Volume" in df_vv.columns and df_vv["Volume"].sum() > 0:
                    st.plotly_chart(
                        vis.plot_volume_breakout(df_vv, selected),
                        use_container_width=True
                    )
                else:
                    st.info("Volume non disponible pour cet actif.")
        else:
            st.info(
                f"Données insuffisantes pour la période **{period} / {interval}** "
                f"({len(df_vv) if not df_vv.empty else 0} bougies — 20 minimum requis). "
                "Essayez une période plus longue ou un intervalle plus grand."
            )
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────── TAB 4 : STATISTIQUES ────────────────────────────────
with tab_stats:
    st.subheader(f"Statistiques & Ratios de Risque — {selected} ({period} / {interval})")
    try:
        df_s = load_df(selected, period, interval, custom_date if use_date_range else None)
        if df_s.empty or len(df_s) < 20:
            st.warning(
                f"Données insuffisantes pour la période **{period} / {interval}** "
                f"({len(df_s) if not df_s.empty else 0} bougies — 20 minimum requis)."
            )
        else:
            close = df_s["Close"]
            is_cry = "USD" in data_mod.MARKET.get(selected, "")
            vol = grk.calculate_historical_volatility(close, is_crypto=is_cry)
            sharpe = grk.calculate_sharpe_ratio(close, is_crypto=is_cry)

            beta = 0.0
            try:
                spy_df = data_mod.recuperer_historique("S&P 500 ETF (Tradable)", period, interval)
                if not spy_df.empty:
                    beta = grk.calculate_beta(close, spy_df["Close"])
            except Exception:
                beta = float("nan")

            rets = close.pct_change().dropna()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Volatilité ann.", f"{vol*100:.2f} %",
                      help="Amplitude de la variation des rendements annualisée.")
            c2.metric("Ratio de Sharpe", f"{sharpe:.2f}",
                      help="> 1.0 = bonne rentabilité ajustée au risque.")
            c3.metric("Bêta (vs S&P 500)", f"{beta:.2f}" if np.isfinite(beta) else "N/A",
                      help="β > 1 = plus risqué que le marché. β < 1 = plus défensif.")
            c4.metric("Rendement période", f"{((close.iloc[-1]/close.iloc[0])-1)*100:.2f} %",
                      help="Croissance brute sur la période sélectionnée.")

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Max période", f"{close.max():.2f}")
            c6.metric("Min période", f"{close.min():.2f}")
            c7.metric("Skewness", f"{rets.skew():.2f}",
                      help="Asymétrie des rendements. Négatif = risque de krach soudain.")
            c8.metric("Kurtosis", f"{rets.kurtosis():.2f}",
                      help="> 3 = chocs extrêmes fréquents.")

            st.markdown("#### Données récentes")
            cols_show = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df_s.columns]
            df_display = df_s[cols_show].tail(30).copy()
            df_display.columns = [c.capitalize() for c in df_display.columns]
            st.dataframe(
                df_display.style.format("{:.2f}", subset=[c for c in df_display.columns if c != "Volume"]),
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────── TAB 5 : DISTRIBUTION ────────────────────────────────
with tab_dist:
    st.subheader(f"Distribution des Rendements — {selected} ({period} / {interval})")
    try:
        df_d = load_df(selected, period, interval, custom_date if use_date_range else None)
        if df_d.empty or len(df_d) < 20:
            st.warning(
                f"Données insuffisantes pour la période **{period} / {interval}** "
                f"(20 bougies minimum requis)."
            )
        else:
            st.plotly_chart(
                vis.plot_returns_distribution(df_d["Close"], selected),
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Erreur : {e}")

# ─────────────────────── TAB 6 : CORRÉLATION ─────────────────────────────────
with tab_corr:
    st.subheader("Matrice de Corrélation entre Rendements")
    default_assets = [
        "Apple Inc.", "Microsoft", "Nvidia", "Amazon", "Tesla, Inc.",
        "Alphabet Inc. (Class A)", "Meta Platforms", "JPMorgan Chase", "Berkshire Hathaway"
    ]
    valid_assets = [a for a in default_assets if a in data_mod.MARKET]
    corr_assets = st.multiselect("Actifs à comparer", asset_names, default=valid_assets[:6])

    if len(corr_assets) < 2:
        st.info("Sélectionnez au moins 2 actifs pour calculer la corrélation.")
    else:
        with st.spinner("Chargement des données…"):
            prices_dict = {}
            for a in corr_assets:
                try:
                    df_c = load_df(a, period, interval, custom_date if use_date_range else None)
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
