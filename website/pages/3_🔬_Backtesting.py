"""
3_🔬_Backtesting.py — Stratégies techniques & backtesting historique
"""
import streamlit as st
import pandas as pd
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import data.data as data_mod
import simulation.simulation as sim
import visualisation.visualisation as vis

if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

st.title("🔬 Backtesting — Stratégies Techniques")
st.caption("Teste tes stratégies de trading sur des données historiques réelles.")

# ── Paramètres ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 1.5, 1.5])
with col1:
    asset = st.selectbox("Actif à tester", list(data_mod.MARKET.keys()))
with col2:
    strat = st.selectbox("Stratégie", ["SMA (Moyennes Mobiles)", "RSI (Force Relative)"])
with col3:
    period_bt = st.selectbox("Période", ["6mo","1y","2y","5y","max"], index=1)

strat_key = "SMA" if "SMA" in strat else "RSI"

# ── Paramètres de la stratégie ────────────────────────────────────────────────
st.markdown("#### ⚙️ Paramètres")
params = {}
col_p1, col_p2, col_p3 = st.columns(3)
if strat_key == "SMA":
    with col_p1:
        params["short_window"] = st.slider("MM Courte (jours)", 5, 50, 20)
    with col_p2:
        params["long_window"]  = st.slider("MM Longue (jours)", 20, 200, 50)
    with col_p3:
        capital_init = st.number_input("Capital initial (€)", 1000, 100000, 10000, step=500)
else:
    with col_p1:
        params["rsi_window"]  = st.slider("Fenêtre RSI", 5, 30, 14)
    with col_p2:
        params["oversold"]    = st.slider("Seuil survente (achat)", 10, 45, 30)
    with col_p3:
        params["overbought"]  = st.slider("Seuil surachat (vente)", 55, 90, 70)
    capital_init = st.number_input("Capital initial (€)", 1000, 100000, 10000, step=500)

st.divider()
run_bt = st.button("▶️ Lancer le Backtest", type="primary", use_container_width=False)

if run_bt:
    with st.spinner("Simulation en cours…"):
        try:
            df_bt   = data_mod.recuperer_historique(asset, period_bt, "1d")
            prices  = df_bt["Close"]
            res     = sim.backtest_strategy(prices, strat_key, params)

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
                    import plotly.graph_objects as go
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
                    fig_s.update_layout(template="plotly_dark", paper_bgcolor="#0E1117",
                                        title=f"Signaux {strat_key} — {asset}", height=400)
                    st.plotly_chart(fig_s, use_container_width=True)

        except Exception as e:
            st.error(f"Erreur : {e}")
