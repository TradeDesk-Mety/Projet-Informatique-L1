import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import data.data as data_mod
import simulation.simulation as sim
import visualisation.visualisation as vis

from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui

if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

set_global_ui()
render_assistant()

st.title("Backtesting — Stratégies Techniques")
st.caption("Teste tes stratégies de trading sur des données historiques réelles.")

# ── Paramètres ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 1.5, 1.5])
with col1:
    asset = st.selectbox("Actif à tester", list(data_mod.MARKET.keys()))
with col2:
    strat = st.selectbox("Stratégie", ["SMA (Moyennes Mobiles)", "RSI (Force Relative)", "Comparatif (SMA vs RSI)"])
with col3:
    period_bt = st.selectbox("Période", ["6mo","1y","2y","5y","max"], index=1)

strat_key = "SMA" if "SMA" in strat else ("CMP" if "Comparatif" in strat else "RSI")

# ── Paramètres de la stratégie ────────────────────────────────────────────────
capital_init = st.number_input("Capital initial (€)", 1000, 100000, 10000, step=500, key="capital_init_bt")

params = {}
col_p1, col_p2, col_p3 = st.columns(3)
if strat_key == "SMA":
    with col_p1:
        params["short_window"] = st.slider("MM Courte (jours)", 5, 50, 20)
    with col_p2:
        params["long_window"]  = st.slider("MM Longue (jours)", 20, 200, 50)
elif strat_key == "RSI":
    with col_p1:
        params["rsi_window"]  = st.slider("Fenêtre RSI", 5, 30, 14)
    with col_p2:
        params["oversold"]    = st.slider("Seuil survente (achat)", 10, 45, 30)
    with col_p3:
        params["overbought"]  = st.slider("Seuil surachat (vente)", 55, 90, 70)
else:  # Comparatif
    st.info("Mode Comparatif : SMA(20/50) vs RSI(14/30/70) lancés simultanément sur la même période.")

st.divider()
run_bt = st.button("▶️ Lancer le Backtest", type="primary", use_container_width=False)

if run_bt:
    with st.spinner("Simulation en cours…"):
        try:
            df_bt   = data_mod.recuperer_historique(asset, period_bt, "1d")
            prices  = df_bt["Close"]

            if "Comparatif" in strat:
                # Execution de SMA
                params_sma = {"short_window": 20, "long_window": 50, "initial_cash": capital_init}
                res_sma = sim.backtest_strategy(prices, "SMA", params_sma)
                # Execution de RSI
                params_rsi = {"rsi_window": 14, "oversold": 30, "overbought": 70, "initial_cash": capital_init}
                res_rsi = sim.backtest_strategy(prices, "RSI", params_rsi)
                
                if "error" in res_sma or "error" in res_rsi:
                    st.error("Erreur de simulation sur l'une des stratégies.")
                else:
                    st.success("Comparatif généré avec succès !")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Rendement Buy & Hold", f"{res_sma['benchmark_return']:.2f} %")
                    c2.metric("Rendement SMA (20/50)", f"{res_sma['strategy_return']:.2f} %", delta=f"{res_sma['strategy_return'] - res_sma['benchmark_return']:+.2f} %")
                    c3.metric("Rendement RSI (14/30/70)", f"{res_rsi['strategy_return']:.2f} %", delta=f"{res_rsi['strategy_return'] - res_rsi['benchmark_return']:+.2f} %")
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=res_sma["dates"], y=res_sma["equity_curve"], mode='lines', name='SMA', line=dict(color='#00A8E8')))
                    fig.add_trace(go.Scatter(x=res_rsi["dates"], y=res_rsi["equity_curve"], mode='lines', name='RSI', line=dict(color='#7C3AED')))
                    fig.add_trace(go.Scatter(x=res_sma["dates"], y=res_sma["benchmark_curve"], mode='lines', name='Buy & Hold', line=dict(color='#C0C0C0', dash='dash')))
                    fig.update_layout(title="Comparaison des Capitaux (Equity Curves)", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)

            else:
                res = sim.backtest_strategy(prices, strat_key, params)

                if "error" in res:
                    st.error(res["error"])
                else:
                    # ── Métriques ──────────────────────────────────────────────
                    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                    col_m1.metric("Valeur finale",       f"{res['final_value']:,.2f} €")
                    col_m2.metric("Rendement stratégie", f"{res['strategy_return']:.2f} %")
                    col_m3.metric("Buy & Hold",          f"{res['benchmark_return']:.2f} %")
                    col_m4.metric("Max Drawdown",        f"{res['max_drawdown']:.2f} %")
                    col_m5.metric("Ordres passés",       f"{res['trades_count']}")

                    alpha = res["strategy_return"] - res["benchmark_return"]
                    st.markdown(f"**Alpha vs Buy & Hold** : `{alpha:+.2f} %` | "
                                f"**Commissions payées (1%)** : `{res['total_commission']:.2f} €`")

                    # ── Graphique performance ──────────────────────────────────
                    st.plotly_chart(vis.plot_backtest_performance(res, f"{strat_key} / {asset}"),
                                    use_container_width=True)

                    # ── Signaux sur le graphique des prix ─────────────────────
                    if "signals" in res and "dates" in res:
                        df_sig = pd.DataFrame({"date": res["dates"], "price": res["prices"],
                                               "signal": res.get("signals", [0]*len(res["dates"]))})
                        buys  = df_sig[df_sig["signal"] == 1]
                        sells = df_sig[df_sig["signal"] == -1]

                        fig_s = go.Figure()
                        fig_s.add_trace(go.Scatter(x=df_sig["date"], y=df_sig["price"],
                                                   line=dict(color="#42A5F5"), name="Prix"))
                        fig_s.add_trace(go.Scatter(x=buys["date"],  y=buys["price"],
                                                   mode="markers", marker=dict(color="#26A69A", size=10, symbol="triangle-up"),
                                                   name="Signal Achat"))
                        fig_s.add_trace(go.Scatter(x=sells["date"], y=sells["price"],
                                                   mode="markers", marker=dict(color="#EF5350", size=10, symbol="triangle-down"),
                                                   name="Signal Vente"))
                        fig_s.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                            title=f"Signaux {strat_key} — {asset}", height=400)
                        st.plotly_chart(fig_s, use_container_width=True)

        except Exception as e:
            st.error(f"Erreur : {e}")
