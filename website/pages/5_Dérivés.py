import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui

set_global_ui()
render_assistant()

import streamlit as st
import pandas as pd
import numpy as np

import greeks.greeks as grk
import visualisation.visualisation as vis
import plotly.graph_objects as go

if not st.session_state.get("logged_in", False):
    st.warning("Connecte-toi depuis la page d'accueil.")
    st.stop()

st.title("Dérivés — Pricing d'Options & Greeks")
st.caption("Modélisation du prix d'une option européenne (Call / Put) selon le modèle Black-Scholes (1973).")

# ── Paramètres ────────────────────────────────────────────────────────────────
st.markdown("### Paramètres du modèle")
col1, col2, col3, col4 = st.columns(4)
with col1:
    S = st.slider("Prix actuel de l'actif S ($)", 10.0, 1000.0, 150.0, step=5.0)
with col2:
    K = st.slider("Strike Price K ($)", 10.0, 1000.0, 150.0, step=5.0)
with col3:
    T = st.slider("Maturité T (années)", 0.1, 5.0, 1.0, step=0.1)
with col4:
    sigma = st.slider("Volatilité σ", 0.05, 1.50, 0.25, step=0.05)

col5, col6 = st.columns(2)
with col5:
    r = st.slider("Taux sans risque r (%)", 0.0, 15.0, 2.0, step=0.25) / 100
with col6:
    opt_type = st.radio("Type d'option", ["Call", "Put"], horizontal=True)

st.divider()

# ── Calcul du prix + Greeks ───────────────────────────────────────────────────
opt_key = opt_type.lower()
try:
    price = grk.black_scholes_pricing(S, K, T, r, sigma, opt_key)
    g = grk.calculate_greeks(S, K, T, r, sigma)

    st.markdown("### Prix théorique & Greeks")

    # Ligne 1 : Prix + Delta + Gamma
    c1, c2, c3 = st.columns(3)
    c1.metric(
        f"Prix {opt_type}",
        f"{price:.6f} $",
        help="Valeur théorique calculée par Black-Scholes."
    )
    c2.metric(
        "Delta (Δ)",
        f"{g['delta_call']:.6f}" if opt_key == "call" else f"{g['delta_put']:.6f}",
        help="Variation du prix de l'option pour +1 $ sur l'actif sous-jacent."
    )
    c3.metric(
        "Gamma (Γ)",
        f"{g['gamma']:.6f}",
        help="Taux de variation du Delta. Mesure la courbure de la position."
    )

    # Ligne 2 : Theta + Vega + Rho
    c4, c5, c6 = st.columns(3)
    c4.metric(
        "Theta (Θ)",
        f"{g['theta_call']:.6f}" if opt_key == "call" else f"{g['theta_put']:.6f}",
        help="Perte de valeur par jour. Toujours négatif pour l'acheteur d'option."
    )
    c5.metric(
        "Vega (ν)",
        f"{g['vega']:.6f}",
        help="Sensibilité du prix à une variation de +1% de volatilité."
    )
    c6.metric(
        "Rho (ρ)",
        f"{g['rho_call']:.6f}" if opt_key == "call" else f"{g['rho_put']:.6f}",
        help="Sensibilité du prix à une variation de +1% du taux sans risque."
    )

    with st.expander("Tableau récapitulatif complet", expanded=False):
        df_greeks = pd.DataFrame({
            "Greek": ["Prix", "Delta (Δ)", "Gamma (Γ)", "Theta (Θ)", "Vega (ν)", "Rho (ρ)"],
            "Valeur": [
                price,
                g['delta_call'] if opt_key == "call" else g['delta_put'],
                g['gamma'],
                g['theta_call'] if opt_key == "call" else g['theta_put'],
                g['vega'],
                g['rho_call'] if opt_key == "call" else g['rho_put'],
            ],
            "Description": [
                "Valeur théorique de l'option",
                "Variation du prix pour +1 $ sur l'actif",
                "Variation du Delta (courbure)",
                "Perte de valeur par jour",
                "Sensibilité à +1% de volatilité",
                "Sensibilité à +1% du taux sans risque",
            ]
        })
        st.dataframe(
            df_greeks.style.format({"Valeur": "{:.8f}"}),
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"Erreur de calcul : {e}")

st.divider()

# ── Onglets ───────────────────────────────────────────────────────────────────
tab_3d, tab_smile, tab_sens = st.tabs(["Surface 3D", "Volatility Smile", "Sensibilité des Greeks"])

with tab_3d:
    with st.spinner("Génération de la surface 3D…"):
        fig_3d = vis.plot_3d_option_surface(S, r, sigma, opt_key)
    st.plotly_chart(fig_3d, use_container_width=True)
    st.markdown("""
**Lecture de la surface :**
- **Axe X — Strike Price K** : plus K est faible par rapport à S, plus le Call a de valeur intrinsèque.
- **Axe Y — Maturité T** : une option lointaine vaut plus car la valeur temps est plus grande.
- **Axe Z — Prix de l'option** : somme de la valeur intrinsèque + valeur temps.
""")

with tab_smile:
    st.subheader("Volatility Smile")
    st.caption("Prix de l'option en fonction du Strike, pour différentes volatilités implicites.")

    strikes_smile = np.linspace(S * 0.7, S * 1.3, 50)
    vols_smile = [0.15, 0.20, 0.25, 0.35, 0.50]
    fig_smile = go.Figure()
    palette = ["#42A5F5", "#26A69A", "#FFA726", "#EF5350", "#CE93D8"]

    for vol_s, col_s in zip(vols_smile, palette):
        prices_smile = [grk.black_scholes_pricing(S, k, T, r, vol_s, opt_key) for k in strikes_smile]
        fig_smile.add_trace(go.Scatter(
            x=strikes_smile, y=prices_smile,
            name=f"σ = {vol_s:.0%}",
            line=dict(color=col_s, width=2),
        ))

    fig_smile.add_vline(x=S, line=dict(color="white", dash="dash", width=1),
                        annotation_text="ATM (S)", annotation_position="top right")
    fig_smile.update_layout(
        title=f"Prix du {opt_type} en fonction du Strike K",
        xaxis_title="Strike K ($)", yaxis_title="Prix de l'option ($)",
        template="plotly_dark", paper_bgcolor="#0E1117",
        hovermode="x unified", height=420,
    )
    st.plotly_chart(fig_smile, use_container_width=True)

with tab_sens:
    st.subheader("Sensibilité des Greeks au prix de l'actif")
    S_range = np.linspace(max(1, S * 0.5), S * 1.5, 100)

    deltas, gammas, thetas, vegas = [], [], [], []
    for s_i in S_range:
        g_i = grk.calculate_greeks(s_i, K, T, r, sigma)
        deltas.append(g_i["delta_call"] if opt_key == "call" else g_i["delta_put"])
        gammas.append(g_i["gamma"])
        thetas.append(g_i["theta_call"] if opt_key == "call" else g_i["theta_put"])
        vegas.append(g_i["vega"])

    fig_gr = go.Figure()
    fig_gr.add_trace(go.Scatter(x=S_range, y=deltas, name="Delta (Δ)", line=dict(color="#42A5F5", width=2)))
    fig_gr.add_trace(go.Scatter(x=S_range, y=gammas, name="Gamma (Γ)", line=dict(color="#26A69A", width=2)))
    fig_gr.add_trace(go.Scatter(x=S_range, y=[v / 100 for v in vegas], name="Vega/100 (ν)", line=dict(color="#FFA726", width=2)))
    fig_gr.add_trace(go.Scatter(x=S_range, y=thetas, name="Theta (Θ)", line=dict(color="#EF5350", width=2, dash="dot")))
    fig_gr.add_vline(x=S, line=dict(color="white", dash="dash", width=1), annotation_text=f"S = {S}")
    fig_gr.add_vline(x=K, line=dict(color="#CE93D8", dash="dot", width=1), annotation_text=f"K = {K}")
    fig_gr.update_layout(
        title=f"Greeks en fonction du prix de l'actif S ({opt_type})",
        xaxis_title="Prix de l'actif S ($)", yaxis_title="Valeur du Greek",
        template="plotly_dark", paper_bgcolor="#0E1117",
        hovermode="x unified", height=420,
    )
    st.plotly_chart(fig_gr, use_container_width=True)

    st.markdown("""
**Rappel des Greeks :**
| Greek | Signification |
|-------|--------------|
| **Δ Delta** | Variation du prix de l'option pour +1 $ sur l'actif |
| **Γ Gamma** | Variation du Delta (courbure de la position) |
| **ν Vega** | Sensibilité à la volatilité (+1%) |
| **Θ Theta** | Perte de valeur par jour écoulé |
| **ρ Rho** | Sensibilité au taux sans risque (+1%) |
""")
