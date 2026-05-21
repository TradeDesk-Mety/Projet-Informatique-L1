import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui

set_global_ui()
render_assistant()

import streamlit as st
import pandas as pd

import data.data as data_mod
import finance.finance as fin
from greeks.greeks import calculate_historical_volatility

if not st.session_state.get("logged_in", False):
    st.warning("Connecte-toi depuis la page d'accueil.")
    st.stop()

p = st.session_state.portfolio
user_id = st.session_state.user_id


def save():
    p.save_to_db(user_id)


st.title("Portefeuille & Ordres")
st.caption("Centralisez vos liquidités, surveillez vos positions et passez des ordres sur le marché.")

# ─── Collecte des sous-jacents détenus ───────────────────────────────────────
held_underlyings = set()
for pos_ticker in p.positions.keys():
    base = pos_ticker.split("_")[0] if "_" in pos_ticker else pos_ticker
    held_underlyings.add(base)

selected_trade_asset = st.session_state.get(
    "selected_trade_asset", list(data_mod.MARKET.keys())[0]
)
assets_to_fetch = held_underlyings.union({selected_trade_asset})
assets_to_fetch.add("S&P 500 ETF (Tradable)")


@st.cache_data(ttl=10)
def get_prices(assets):
    prices = {}
    for name in assets:
        try:
            prices[name] = data_mod.recuperer_prix_actuel(name, "1d")
        except Exception:
            prices[name] = 0.0
    return prices


with st.spinner("Récupération des cours en direct..."):
    mkt = get_prices(frozenset(assets_to_fetch))


def get_current_portfolio_value_and_prices():
    current_prices = {}
    for t, info in p.positions.items():
        if "_" in t:
            try:
                parts = t.split("_")
                if len(parts) == 4:
                    underlying, opt_type, strike_str, expiry_str = parts
                    strike = float(strike_str)
                    months = float(expiry_str.replace("M", ""))
                    T = months / 12.0
                    underlying_price = mkt.get(underlying, info["avg_price"])
                    hist_df = data_mod.recuperer_historique(underlying, "3mo", "1d")
                    vol = calculate_historical_volatility(hist_df["Close"]) if not hist_df.empty else 0.25
                    current_prices[t] = fin.pricing_option_bs(
                        S=underlying_price, K=strike, T=T, r=0.02,
                        sigma=vol, option_type=opt_type.lower(),
                    )
                else:
                    current_prices[t] = info["avg_price"]
            except Exception:
                current_prices[t] = info["avg_price"]
        else:
            current_prices[t] = mkt.get(t, info["avg_price"])

    val = p.cash
    for t, info in p.positions.items():
        val += info["quantity"] * current_prices.get(t, info["avg_price"])
    return val, current_prices


total_value, real_prices = get_current_portfolio_value_and_prices()
perf = p.get_total_performance(real_prices)
valeur_actions = total_value - p.cash

# ─── Métriques principales ────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Valeur Totale", f"{total_value:,.2f} €")
c2.metric("Liquidités (Cash)", f"{p.cash:,.2f} €")
c3.metric("Valeur des Positions", f"{valeur_actions:,.2f} €")
c4.metric("Performance (ROI)", f"{perf:+.2f} %", delta=f"{total_value - p.initial_cash:+.2f} €")

st.divider()

# ─── Onglets ──────────────────────────────────────────────────────────────────
tab_order, tab_pos, tab_hist_tx = st.tabs(
    ["Passer un ordre", "Positions", "Historique"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Passer un ordre
# ══════════════════════════════════════════════════════════════════════════════
with tab_order:
    st.subheader("Passer un ordre financier")
    col_l, col_r = st.columns([1.2, 1])

    with col_l:
        trade_type = st.radio("Type d'opération", ["Achat", "Vente"], horizontal=True)
        inst_type = st.selectbox("Type d'instrument", ["Action / ETF", "Option (Call / Put)"])
        is_buy = trade_type == "Achat"

        if is_buy:
            trade_asset = st.selectbox(
                "Actif sous-jacent",
                list(data_mod.MARKET.keys()),
                key="selected_trade_asset",
            )
        else:
            owned_tickers = list(p.positions.keys())
            if not owned_tickers:
                st.info("Aucune position à vendre.")
                trade_asset = None
                trade_ticker = None
                cur_p = 0.0
                premium = 0.0
                brut = comm = total = 0.0
            else:
                if inst_type == "Action / ETF":
                    sell_choices = [t for t in owned_tickers if "_" not in t]
                else:
                    sell_choices = [t for t in owned_tickers if "_" in t]

                if not sell_choices:
                    st.info("Aucune position de ce type à vendre. Changez le type d'instrument.")
                    trade_asset = None
                    trade_ticker = None
                    cur_p = 0.0
                    premium = 0.0
                    brut = comm = total = 0.0
                else:
                    trade_asset_raw = st.selectbox(
                        "Actif à vendre", sell_choices, key="selected_sell_asset"
                    )
                    trade_asset = trade_asset_raw.split("_")[0] if "_" in trade_asset_raw else trade_asset_raw
                    trade_ticker = trade_asset_raw
                    cur_p = mkt.get(trade_asset, 0.0)
                    premium = 0.0
                    brut = comm = total = 0.0

        if is_buy or (not is_buy and trade_asset is not None):
            qty = st.number_input("Quantité", min_value=1, step=1, value=10)
            if is_buy:
                cur_p = mkt.get(trade_asset, 0.0)
            premium = 0.0

            if inst_type == "Option (Call / Put)":
                opt_type_label = st.selectbox(
                    "Type d'Option", ["Call (Achat de hausse)", "Put (Achat de baisse)"]
                )
                opt_kind = "call" if "Call" in opt_type_label else "put"
                strike = st.number_input(
                    "Strike (Prix d'exercice)",
                    min_value=1.0,
                    value=round(cur_p, 1) if cur_p > 1.0 else 100.0,
                    step=0.5,
                )
                expiry_months = st.selectbox(
                    "Échéance / Maturité", [1, 3, 6, 12], format_func=lambda x: f"{x} mois"
                )
                with st.spinner("Calcul de la volatilité historique..."):
                    hist_df = data_mod.recuperer_historique(trade_asset, "3mo", "1d")
                    vol = calculate_historical_volatility(hist_df["Close"]) if not hist_df.empty else 0.25
                T = expiry_months / 12.0
                r = 0.02
                premium = fin.pricing_option_bs(S=cur_p, K=strike, T=T, r=r, sigma=vol, option_type=opt_kind)

                if is_buy:
                    trade_ticker = f"{trade_asset}_{opt_kind.upper()}_{strike:.1f}_{expiry_months}M"

                st.info(f"Volatilité historique estimée de {trade_asset} : **{vol*100:.1f}%**")
                try:
                    brut = fin.total_brut(qty, premium)
                    comm = fin.calculer_commission(premium, qty)
                    total = fin.total_net_achat(qty, premium) if is_buy else fin.total_net_vente(qty, premium)
                except Exception:
                    brut = comm = total = 0.0

                st.markdown(f"""
| Paramètre | Valeur |
|-----------|--------|
| Contrat | **{trade_ticker}** |
| Prime d'option | **{premium:.4f} €** |
| Montant brut | {brut:.4f} € |
| Commission (1 %) | {comm:.4f} € |
| **Montant net** | **{total:.4f} €** |
""")

            else:
                if is_buy:
                    trade_ticker = trade_asset
                try:
                    brut = fin.total_brut(qty, cur_p)
                    comm = fin.calculer_commission(cur_p, qty)
                    total = fin.total_net_achat(qty, cur_p) if is_buy else fin.total_net_vente(qty, cur_p)
                except Exception:
                    brut = comm = total = 0.0

                st.markdown(f"""
| Paramètre | Valeur |
|-----------|--------|
| Cours actuel | **{cur_p:.4f} €** |
| Montant brut | {brut:.4f} € |
| Commission (1 %) | {comm:.4f} € |
| **Montant net** | **{total:.4f} €** |
""")

            if is_buy:
                price_to_use = premium if inst_type == "Option (Call / Put)" else cur_p
                can_afford = int(p.cash // (price_to_use * 1.01)) if price_to_use > 0 else 0
                st.info(f"Capacité maximale d'achat : **{can_afford} unités** avec tes liquidités actuelles.")

    with col_r:
        if trade_asset is not None:
            st.markdown("#### Aperçu de l'ordre")
            action_label = "ACHETER" if is_buy else "VENDRE"
            badge_color = "#2563EB" if inst_type == "Option (Call / Put)" else "#059669"
            montant_color = "26A69A" if is_buy else "EF5350"

            st.markdown(
                f"""
<div style='background:#1F2937;padding:20px;border-radius:12px;border:1px solid #374151;'>
  <div style='text-align:center;margin-bottom:10px;'>
    <span style='padding:4px 12px;border-radius:20px;font-size:0.8rem;
                 background:{badge_color};color:white;'>{inst_type.upper()}</span>
  </div>
  <h3 style='color:#F9FAFB;text-align:center;margin-top:5px'>{action_label}</h3>
  <p style='font-size:1.1rem;text-align:center;color:#9CA3AF;word-break:break-all;'>{qty} × {trade_ticker}</p>
  <p style='font-size:1.6rem;text-align:center;color:#{montant_color};font-weight:bold'>
    {total:.4f} €
  </p>
</div>
""",
                unsafe_allow_html=True,
            )

            st.markdown("")
            if st.button(f"{action_label} — Confirmer", type="primary", use_container_width=True):
                price_to_use = premium if inst_type == "Option (Call / Put)" else cur_p
                msg = p.buy(trade_ticker, qty, price_to_use) if is_buy else p.sell(trade_ticker, qty, price_to_use)
                if "succès" in msg.lower() or "vendu" in msg.lower():
                    st.success(msg)
                    save()
                    st.rerun()
                else:
                    st.error(msg)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Positions
# ══════════════════════════════════════════════════════════════════════════════
with tab_pos:
    st.subheader("Positions en cours")
    if not p.positions:
        st.info("Aucune position ouverte. Placez votre premier ordre dans l'onglet 'Passer un ordre'.")
    else:
        rows = []
        for t, info in p.positions.items():
            cur = real_prices.get(t, info["avg_price"])
            pnl = (cur - info["avg_price"]) * info["quantity"]
            roi = ((cur - info["avg_price"]) / info["avg_price"]) * 100 if info["avg_price"] > 0 else 0
            asset_type = "Option" if "_" in t else "Action/ETF"
            rows.append({
                "Type": asset_type,
                "Actif": t,
                "Quantité": info["quantity"],
                "Prix moyen (€)": info["avg_price"],
                "Prix actuel (€)": cur,
                "Valeur totale (€)": info["quantity"] * cur,
                "G/P (€)": pnl,
                "ROI (%)": roi,
            })
        df_pos = pd.DataFrame(rows)

        def color_pnl(val):
            if isinstance(val, (int, float)):
                return f"color: {'#26A69A' if val >= 0 else '#EF5350'}"
            return ""

        styled = df_pos.style.map(color_pnl, subset=["G/P (€)", "ROI (%)"])
        st.dataframe(
            styled,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Actif": st.column_config.TextColumn(width="large"),
                "Quantité": st.column_config.NumberColumn(format="%d"),
                "Prix moyen (€)": st.column_config.NumberColumn(format="%.4f €"),
                "Prix actuel (€)": st.column_config.NumberColumn(format="%.4f €"),
                "Valeur totale (€)": st.column_config.NumberColumn(format="%.2f €"),
                "G/P (€)": st.column_config.NumberColumn(format="%.2f €"),
                "ROI (%)": st.column_config.NumberColumn(format="%.2f %%"),
            },
        )

        import plotly.express as px
        fig_pie = px.pie(
            df_pos,
            names="Actif",
            values="Valeur totale (€)",
            title="Répartition du portefeuille",
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Teal,
        )
        fig_pie.update_layout(paper_bgcolor="#0E1117", height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Historique des transactions
# ══════════════════════════════════════════════════════════════════════════════
with tab_hist_tx:
    st.subheader("Historique des Transactions")
    if not p.transactions:
        st.info("Aucune transaction enregistrée.")
    else:
        df_tx = pd.DataFrame(p.transactions)
        rename_map = {
            "timestamp": "Date & Heure",
            "type": "Type",
            "ticker": "Actif",
            "asset": "Actif",
            "quantity": "Quantité",
            "price": "Prix unitaire (€)",
            "commission": "Commission (€)",
            "total_net": "Montant net (€)",
        }
        existing_rename = {k: v for k, v in rename_map.items() if k in df_tx.columns}
        df_tx = df_tx.rename(columns=existing_rename)

        st.dataframe(
            df_tx,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Actif": st.column_config.TextColumn(width="large"),
                "Prix unitaire (€)": st.column_config.NumberColumn(format="%.4f €"),
                "Commission (€)": st.column_config.NumberColumn(format="%.4f €"),
                "Montant net (€)": st.column_config.NumberColumn(format="%.4f €"),
            },
        )

        csv = df_tx.to_csv(index=False).encode("utf-8")
        st.download_button("Télécharger CSV", csv, "transactions.csv", "text/csv")
