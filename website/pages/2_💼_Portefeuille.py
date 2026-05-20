"""
2_💼_Portefeuille.py — Ordres de trading, positions, historique
"""
import streamlit as st
import pandas as pd
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import data.data as data_mod
import finance.finance as fin
from data.database import PORTFOLIO_DB_PATH

if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

p = st.session_state.portfolio

def save():
    p.save_to_db(PORTFOLIO_DB_PATH)

st.title("💼 Portefeuille — Paper Trading")

# ── Prix actuels (cache 60 s) ─────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_prices():
    prices = {}
    for name in data_mod.MARKET:
        try:
            prices[name] = data_mod.recuperer_prix_actuel(name, "1d")
        except Exception:
            prices[name] = 0.0
    return prices

with st.spinner("Récupération des cours…"):
    mkt = get_prices()

# ── Métriques globales ────────────────────────────────────────────────────────
val   = p.get_portfolio_value(mkt)
perf  = p.get_total_performance(mkt)
delta = val - p.initial_cash

c1, c2, c3, c4 = st.columns(4)
c1.metric("💵 Liquidités",        f"{p.cash:,.2f} €")
c2.metric("📦 Valeur totale",     f"{val:,.2f} €",     f"{delta:+,.2f} €")
c3.metric("📈 Performance",       f"{perf:.2f} %",     f"{perf:+.2f} %")
c4.metric("💼 Capital initial",   f"{p.initial_cash:,.2f} €")

st.divider()

# ── Onglets ───────────────────────────────────────────────────────────────────
tab_order, tab_pos, tab_hist_tx = st.tabs(["📥 Passer un ordre", "📊 Positions", "📜 Historique"])

# ─────────────────────── TAB 1 : ORDRE ───────────────────────────────────────
with tab_order:
    st.subheader("Passer un ordre financier")
    col_l, col_r = st.columns([1, 1])

    with col_l:
        trade_type  = st.radio("Type d'opération", ["Achat 🟢", "Vente 🔴"], horizontal=True)
        trade_asset = st.selectbox("Actif", list(data_mod.MARKET.keys()))
        qty         = st.number_input("Quantité", min_value=1, step=1, value=10)

        cur_p = mkt.get(trade_asset, 0.0)
        is_buy = "Achat" in trade_type

        try:
            brut   = fin.total_brut(qty, cur_p)
            comm   = fin.calculer_commission(cur_p, qty)
            total  = fin.total_net_achat(qty, cur_p) if is_buy else fin.total_net_vente(qty, cur_p)
        except Exception:
            brut = comm = total = 0.0

        st.markdown(f"""
        | Paramètre | Valeur |
        |-----------|--------|
        | Cours actuel | **{cur_p:.2f} €/$** |
        | Montant brut | {brut:.2f} € |
        | Commission (1%) | {comm:.2f} € *(moteur C++)* |
        | **Montant net** | **{total:.2f} €** |
        """)

        if is_buy:
            can_afford = int(p.cash // (cur_p * 1.01)) if cur_p > 0 else 0
            st.info(f"Capacité maximale d'achat : **{can_afford} actions** avec tes liquidités actuelles.")

    with col_r:
        st.markdown("#### Aperçu de l'ordre")
        action_label = "🟢 ACHETER" if is_buy else "🔴 VENDRE"
        st.markdown(f"""
        <div style='background:#1F2937;padding:20px;border-radius:12px;border:1px solid #374151;'>
          <h3 style='color:#F9FAFB;text-align:center'>{action_label}</h3>
          <p style='font-size:1.3rem;text-align:center;color:#9CA3AF'>{qty} × {trade_asset}</p>
          <p style='font-size:1.6rem;text-align:center;color:#{"26A69A" if is_buy else "EF5350"};font-weight:bold'>
            {total:.2f} €
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        if st.button(f"{action_label} — Confirmer", type="primary", use_container_width=True):
            msg = p.buy(trade_asset, qty, cur_p) if is_buy else p.sell(trade_asset, qty, cur_p)
            if "succès" in msg.lower() or "vendu" in msg.lower():
                st.success(msg)
                save()
                st.rerun()
            else:
                st.error(msg)

# ─────────────────────── TAB 2 : POSITIONS ────────────────────────────────────
with tab_pos:
    st.subheader("Positions en cours")
    if not p.positions:
        st.info("Aucune position ouverte. Place ton premier ordre !")
    else:
        rows = []
        for t, info in p.positions.items():
            cur  = mkt.get(t, info["avg_price"])
            pnl  = (cur - info["avg_price"]) * info["quantity"]
            roi  = ((cur - info["avg_price"]) / info["avg_price"]) * 100 if info["avg_price"] > 0 else 0
            rows.append({
                "Actif":           t,
                "Quantité":        info["quantity"],
                "Px moyen (€)":    round(info["avg_price"], 2),
                "Px actuel (€)":   round(cur,               2),
                "Valeur (€)":      round(info["quantity"] * cur, 2),
                "G/P (€)":         round(pnl, 2),
                "ROI (%)":         round(roi, 2),
            })
        df_pos = pd.DataFrame(rows)

        # Colorier Gain/Perte
        def color_pnl(val):
            color = "#26A69A" if val >= 0 else "#EF5350"
            return f"color: {color}"

        styled = df_pos.style.applymap(color_pnl, subset=["G/P (€)", "ROI (%)"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # Pie chart répartition
        import plotly.express as px
        fig_pie = px.pie(
            df_pos, names="Actif", values="Valeur (€)",
            title="Répartition du portefeuille",
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Teal,
        )
        fig_pie.update_layout(paper_bgcolor="#0E1117", height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

# ─────────────────────── TAB 3 : HISTORIQUE TX ────────────────────────────────
with tab_hist_tx:
    st.subheader("Historique des Transactions")
    if not p.transactions:
        st.info("Aucune transaction enregistrée.")
    else:
        df_tx = pd.DataFrame(p.transactions)
        st.dataframe(df_tx, use_container_width=True, hide_index=True)
        csv = df_tx.to_csv(index=False).encode("utf-8")
        st.download_button("💾 Télécharger CSV", csv, "transactions.csv", "text/csv")
