"""
2_💼_Portefeuille.py — Ordres de trading, positions, historique (Actions, ETFs et Options)
========================================================================================
Corrections :
  - applymap → .map() (pandas ≥ 2.1)
  - Vente : selectbox filtré sur les positions existantes uniquement
  - Suppression des mentions internes (moteur C++, BS C++) des tableaux
  - Noms de colonnes français dans l'historique
  - premium initialisé à 0.0 avant le bloc conditionnel
"""

import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import data.data as data_mod
import finance.finance as fin
from data.database import PORTFOLIO_DB_PATH
from greeks.greeks import calculate_historical_volatility

if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

p = st.session_state.portfolio
user_id = st.session_state.user_id


def save():
    p.save_to_db(user_id, PORTFOLIO_DB_PATH)


st.title("💼 Portefeuille — Paper Trading")

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


# ─── Récupération des prix ────────────────────────────────────────────────────
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


# ─── Valeur du portefeuille ───────────────────────────────────────────────────
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
                    if not hist_df.empty:
                        vol = calculate_historical_volatility(hist_df["Close"])
                    else:
                        vol = 0.25
                    current_prices[t] = fin.pricing_option_bs(
                        S=underlying_price,
                        K=strike,
                        T=T,
                        r=0.02,
                        sigma=vol,
                        option_type=opt_type.lower(),
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


val, real_prices = get_current_portfolio_value_and_prices()
perf = p.get_total_performance(real_prices)
delta = val - p.initial_cash

# ─── Métriques principales ────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("💵 Liquidités", f"{p.cash:,.2f} €")
c2.metric("📦 Valeur totale", f"{val:,.2f} €", f"{delta:+,.2f} €")
c3.metric("📈 Performance", f"{perf:.2f} %", f"{perf:+.2f} %")
c4.metric("💼 Capital initial", f"{p.initial_cash:,.2f} €")

st.divider()

# ─── Onglets ──────────────────────────────────────────────────────────────────
tab_order, tab_pos, tab_hist_tx = st.tabs(
    ["📥 Passer un ordre", "📊 Positions", "📜 Historique"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Passer un ordre
# ══════════════════════════════════════════════════════════════════════════════
with tab_order:
    st.subheader("Passer un ordre financier")
    col_l, col_r = st.columns([1.2, 1])

    with col_l:
        trade_type = st.radio(
            "Type d'opération", ["Achat 🟢", "Vente 🔴"], horizontal=True
        )
        inst_type = st.selectbox(
            "Type d'instrument", ["Action / ETF", "Option (Call / Put)"]
        )

        is_buy = "Achat" in trade_type

        # ── Sélection de l'actif (différente selon Achat / Vente) ─────────────
        if is_buy:
            # Achat : toute la liste du marché
            try:
                default_idx = list(data_mod.MARKET.keys()).index(selected_trade_asset)
            except ValueError:
                default_idx = 0

            trade_asset = st.selectbox(
                "Actif sous-jacent",
                list(data_mod.MARKET.keys()),
                index=default_idx,
                key="buy_asset_select",
            )
            if trade_asset != selected_trade_asset:
                st.session_state.selected_trade_asset = trade_asset
                st.rerun()

        else:
            # Vente : uniquement les positions existantes
            owned_tickers = list(p.positions.keys())
            if not owned_tickers:
                st.info("Aucune position à vendre.")
                st.stop()

            # Pour les Actions/ETF, filtrer les non-options ; pour options, inversement
            if inst_type == "Action / ETF":
                sell_choices = [t for t in owned_tickers if "_" not in t]
            else:
                sell_choices = [t for t in owned_tickers if "_" in t]

            if not sell_choices:
                st.info(
                    "Aucune position de ce type à vendre. Changez le type d'instrument."
                )
                st.stop()

            trade_asset_raw = st.selectbox(
                "Actif à vendre",
                sell_choices,
                key="sell_asset_select",
            )
            # Pour les options, le sous-jacent est la première partie du ticker
            trade_asset = (
                trade_asset_raw.split("_")[0] if "_" in trade_asset_raw else trade_asset_raw
            )

        qty = st.number_input("Quantité", min_value=1, step=1, value=10)

        cur_p = mkt.get(trade_asset, 0.0)

        # ── Initialisation de premium (évite NameError si Action/ETF + Confirmer) ──
        premium = 0.0

        # ── Bloc spécifique au type d'instrument ──────────────────────────────
        if inst_type == "Option (Call / Put)":
            opt_type_label = st.selectbox(
                "Type d'Option",
                ["Call (Achat de hausse)", "Put (Achat de baisse)"],
            )
            opt_kind = "call" if "Call" in opt_type_label else "put"
            strike = st.number_input(
                "Strike (Prix d'exercice)",
                min_value=1.0,
                value=round(cur_p, 1) if cur_p > 1.0 else 100.0,
                step=0.5,
            )
            expiry_months = st.selectbox(
                "Échéance / Maturité",
                [1, 3, 6, 12],
                format_func=lambda x: f"{x} mois",
            )
            with st.spinner("Calcul de la volatilité historique..."):
                hist_df = data_mod.recuperer_historique(trade_asset, "3mo", "1d")
                if not hist_df.empty:
                    vol = calculate_historical_volatility(hist_df["Close"])
                else:
                    vol = 0.25
            T = expiry_months / 12.0
            r = 0.02
            premium = fin.pricing_option_bs(
                S=cur_p, K=strike, T=T, r=r, sigma=vol, option_type=opt_kind
            )

            # En mode vente, le ticker est déjà complet (trade_asset_raw)
            if is_buy:
                trade_ticker = f"{trade_asset}_{opt_kind.upper()}_{strike:.1f}_{expiry_months}M"
            else:
                trade_ticker = trade_asset_raw  # ticker existant tel quel

            st.info(
                f"Volatilité historique estimée de {trade_asset} : **{vol*100:.1f}%**"
            )
            try:
                brut = fin.total_brut(qty, premium)
                comm = fin.calculer_commission(premium, qty)
                total = (
                    fin.total_net_achat(qty, premium)
                    if is_buy
                    else fin.total_net_vente(qty, premium)
                )
            except Exception:
                brut = comm = total = 0.0

            st.markdown(
                f"""
| Paramètre | Valeur |
|-----------|--------|
| Contrat | **{trade_ticker}** |
| Prime d'option | **{premium:.2f} €** |
| Montant brut | {brut:.2f} € |
| Commission (1 %) | {comm:.2f} € |
| **Montant net** | **{total:.2f} €** |
"""
            )

        else:
            # Action / ETF
            trade_ticker = trade_asset if is_buy else trade_asset_raw
            try:
                brut = fin.total_brut(qty, cur_p)
                comm = fin.calculer_commission(cur_p, qty)
                total = (
                    fin.total_net_achat(qty, cur_p)
                    if is_buy
                    else fin.total_net_vente(qty, cur_p)
                )
            except Exception:
                brut = comm = total = 0.0

            st.markdown(
                f"""
| Paramètre | Valeur |
|-----------|--------|
| Cours actuel | **{cur_p:.2f} €** |
| Montant brut | {brut:.2f} € |
| Commission (1 %) | {comm:.2f} € |
| **Montant net** | **{total:.2f} €** |
"""
            )

        if is_buy:
            price_to_use = premium if inst_type == "Option (Call / Put)" else cur_p
            can_afford = (
                int(p.cash // (price_to_use * 1.01)) if price_to_use > 0 else 0
            )
            st.info(
                f"Capacité maximale d'achat : **{can_afford} unités** avec tes liquidités actuelles."
            )

    # ── Aperçu et confirmation ────────────────────────────────────────────────
    with col_r:
        st.markdown("#### Aperçu de l'ordre")
        action_label = "🟢 ACHETER" if is_buy else "🔴 VENDRE"
        badge_style = (
            "background: #2563EB; color: white;"
            if inst_type == "Option (Call / Put)"
            else "background: #059669; color: white;"
        )
        # Nom affiché proprement (sans mention interne)
        display_ticker = trade_ticker if is_buy else (trade_asset_raw if not is_buy else trade_ticker)

        st.markdown(
            f"""
<div style='background:#1F2937;padding:20px;border-radius:12px;border:1px solid #374151;'>
  <div style='text-align:center;margin-bottom:10px;'>
     <span style='padding:4px 10px;border-radius:20px;font-size:0.8rem;{badge_style}'>{inst_type.upper()}</span>
  </div>
  <h3 style='color:#F9FAFB;text-align:center;margin-top:5px'>{action_label}</h3>
  <p style='font-size:1.2rem;text-align:center;color:#9CA3AF'>{qty} × {display_ticker}</p>
  <p style='font-size:1.6rem;text-align:center;color:#{"26A69A" if is_buy else "EF5350"};font-weight:bold'>
    {total:.2f} €
  </p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("")
        if st.button(
            f"{action_label} — Confirmer", type="primary", use_container_width=True
        ):
            price_to_use = premium if inst_type == "Option (Call / Put)" else cur_p
            if is_buy:
                msg = p.buy(trade_ticker, qty, price_to_use)
            else:
                msg = p.sell(trade_ticker, qty, price_to_use)

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
        st.info("Aucune position ouverte. Place ton premier ordre !")
    else:
        rows = []
        for t, info in p.positions.items():
            cur = real_prices.get(t, info["avg_price"])
            pnl = (cur - info["avg_price"]) * info["quantity"]
            roi = (
                ((cur - info["avg_price"]) / info["avg_price"]) * 100
                if info["avg_price"] > 0
                else 0
            )
            asset_type = "🔴 Option" if "_" in t else "🟢 Action/ETF"
            # Affichage du ticker sans suffixes internes éventuels
            display_name = t
            rows.append(
                {
                    "Type": asset_type,
                    "Actif": display_name,
                    "Quantité": info["quantity"],
                    "Px moyen (€)": round(info["avg_price"], 2),
                    "Px actuel (€)": round(cur, 2),
                    "Valeur (€)": round(info["quantity"] * cur, 2),
                    "G/P (€)": round(pnl, 2),
                    "ROI (%)": round(roi, 2),
                }
            )
        df_pos = pd.DataFrame(rows)

        def color_pnl(val):
            if isinstance(val, str):
                return ""
            color = "#26A69A" if val >= 0 else "#EF5350"
            return f"color: {color}"

        # Correction : .map() à la place de .applymap() (pandas ≥ 2.1)
        styled = df_pos.style.map(color_pnl, subset=["G/P (€)", "ROI (%)"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        import plotly.express as px

        fig_pie = px.pie(
            df_pos,
            names="Actif",
            values="Valeur (€)",
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

        # Renommage des colonnes en noms français lisibles
        # Les clés correspondent aux noms réels dans les transactions SQLite
        rename_map = {
            "timestamp": "Date & Heure",
            "type": "Type",
            "ticker": "Actif",
            "quantity": "Quantité",
            "price": "Prix unitaire (€)",
            "commission": "Commission (€)",
            "total_net": "Montant net (€)",
        }
        # On ne renomme que les colonnes effectivement présentes
        existing_rename = {k: v for k, v in rename_map.items() if k in df_tx.columns}
        df_tx = df_tx.rename(columns=existing_rename)

        st.dataframe(df_tx, use_container_width=True, hide_index=True)

        csv = df_tx.to_csv(index=False).encode("utf-8")
        st.download_button(
            "💾 Télécharger CSV", csv, "transactions.csv", "text/csv"
        )
