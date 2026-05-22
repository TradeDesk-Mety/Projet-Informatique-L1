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
from data.database import (
    get_portfolio_connection, create_portfolio, get_portfolios,
    rename_portfolio, delete_portfolio,
)
from equities.equities import Portfolio

if not st.session_state.get("logged_in", False):
    st.warning("Connecte-toi depuis la page d'accueil.")
    st.stop()

user_id = st.session_state.user_id

# ─── Taux EUR/USD ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def _get_eurusd():
    try:
        return data_mod.get_eurusd_rate()
    except Exception:
        return 1.08

eurusd = _get_eurusd()

# ─── Multi-portefeuilles : initialisation ─────────────────────────────────────
def _load_portfolios():
    return get_portfolios(user_id)

def _ensure_default_portfolio():
    """Crée un portefeuille par défaut si l'utilisateur n'en a aucun."""
    rows = _load_portfolios()
    if not rows:
        pid = create_portfolio(user_id, "Principal", 10000.0)
        return pid, "Principal"
    return rows[0][0], rows[0][1]

portfolios = _load_portfolios()
if not portfolios:
    _ensure_default_portfolio()
    portfolios = _load_portfolios()

# Sélecteur de portefeuille dans la sidebar
portfolio_options = {f"{r[1]} (#{r[0]})": r[0] for r in portfolios}
portfolio_names_list = list(portfolio_options.keys())

if "active_portfolio_label" not in st.session_state:
    st.session_state.active_portfolio_label = portfolio_names_list[0]

with st.sidebar:
    st.markdown("#### Portefeuilles")
    chosen_label = st.selectbox(
        "Actif",
        portfolio_names_list,
        index=portfolio_names_list.index(st.session_state.active_portfolio_label)
        if st.session_state.active_portfolio_label in portfolio_names_list else 0,
        key="portfolio_selector",
    )
    st.session_state.active_portfolio_label = chosen_label
    active_portfolio_id = portfolio_options[chosen_label]
    active_portfolio_name = portfolios[[r[0] for r in portfolios].index(active_portfolio_id)][1]

    st.caption(f"Portefeuille : **{active_portfolio_name}**")

    if st.button("➕ Nouveau portefeuille", use_container_width=True):
        st.session_state["show_new_portfolio_form"] = True

    if st.session_state.get("show_new_portfolio_form", False):
        with st.form("new_ptf_form"):
            new_name = st.text_input("Nom", placeholder="ex : Tech Growth")
            new_cash = st.number_input("Capital initial (€)", min_value=100.0, value=10000.0, step=500.0)
            created = st.form_submit_button("Créer")
        if created:
            if new_name.strip():
                pid = create_portfolio(user_id, new_name.strip(), new_cash)
                new_p = Portfolio(new_cash)
                new_p.save_to_db(user_id, pid)
                st.session_state["show_new_portfolio_form"] = False
                st.success(f"Portefeuille « {new_name.strip()} » créé !")
                st.rerun()
            else:
                st.error("Entrez un nom.")

# ─── Chargement du portefeuille actif ────────────────────────────────────────
p_key = f"portfolio_{active_portfolio_id}"
if p_key not in st.session_state:
    p_obj = Portfolio(10000.0)
    p_obj.load_from_db(user_id, active_portfolio_id)
    st.session_state[p_key] = p_obj

p = st.session_state[p_key]

# Compatibilité : session_state.portfolio pointe toujours sur le portefeuille actif
st.session_state.portfolio = p


def save():
    p.save_to_db(user_id, active_portfolio_id)


st.title("Portefeuille & Ordres")
st.caption(f"Portefeuille : **{active_portfolio_name}** — Centralisez vos liquidités, surveillez vos positions et passez des ordres.")

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


def to_eur(asset_name: str, price_raw: float) -> float:
    """Convertit un prix brut en EUR si l'actif est coté en USD."""
    if data_mod.is_usd_asset(asset_name) and eurusd > 0:
        return price_raw / eurusd
    return price_raw


def price_eur(asset_name: str) -> float:
    """Retourne le cours actuel en EUR."""
    return to_eur(asset_name, mkt.get(asset_name, 0.0))


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
                    underlying_raw = mkt.get(underlying, info["avg_price"] * eurusd if data_mod.is_usd_asset(underlying) else info["avg_price"])
                    hist_df = data_mod.recuperer_historique(underlying, "3mo", "1d")
                    vol = calculate_historical_volatility(hist_df["Close"]) if not hist_df.empty else 0.25
                    opt_eur = fin.pricing_option_bs(
                        S=underlying_raw, K=strike, T=T, r=0.02,
                        sigma=vol, option_type=opt_type.lower(),
                    )
                    current_prices[t] = opt_eur
                else:
                    current_prices[t] = info["avg_price"]
            except Exception:
                current_prices[t] = info["avg_price"]
        else:
            raw = mkt.get(t, info["avg_price"])
            current_prices[t] = to_eur(t, raw)

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

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Passer un ordre
# ════════════════════════════════════════════════════════════════════════════
with tab_order:
    st.subheader("Passer un ordre financier")
    col_l, col_r = st.columns([1.2, 1])

    with col_l:
        trade_type = st.radio("Type d'opération", ["Achat", "Vente"], horizontal=True)
        inst_type = st.selectbox(
            "Type d'instrument",
            ["Action / ETF", "Cryptomonnaie", "Option (Call / Put)"]
        )
        is_buy = trade_type == "Achat"

        # ── Listes filtrées selon le type d'instrument ──────────────────────
        all_assets = list(data_mod.MARKET.keys())
        crypto_assets = sorted(data_mod.CRYPTO_ASSETS)
        stock_etf_assets = [a for a in all_assets if a not in data_mod.CRYPTO_ASSETS]

        if inst_type == "Cryptomonnaie":
            buy_candidates = crypto_assets
        else:
            buy_candidates = stock_etf_assets

        if is_buy:
            trade_asset = st.selectbox(
                "Actif sous-jacent",
                buy_candidates,
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
                if inst_type == "Option (Call / Put)":
                    sell_choices = [t for t in owned_tickers if "_" in t]
                elif inst_type == "Cryptomonnaie":
                    sell_choices = [t for t in owned_tickers if t in data_mod.CRYPTO_ASSETS]
                else:
                    sell_choices = [t for t in owned_tickers if "_" not in t and t not in data_mod.CRYPTO_ASSETS]

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
                    cur_p = price_eur(trade_asset)
                    premium = 0.0
                    brut = comm = total = 0.0

        if is_buy or (not is_buy and trade_asset is not None):
            qty_step = 0.001 if inst_type == "Cryptomonnaie" else 1
            qty_min = 0.001 if inst_type == "Cryptomonnaie" else 1
            qty = st.number_input(
                "Quantité", min_value=qty_min, step=qty_step,
                value=float(1) if inst_type != "Cryptomonnaie" else 0.1,
                format="%.3f" if inst_type == "Cryptomonnaie" else "%.0f",
            )
            if is_buy:
                raw_price = mkt.get(trade_asset, 0.0)
                cur_p = to_eur(trade_asset, raw_price)
            premium = 0.0

            # ── Note de conversion si actif USD ────────────────────────────
            if is_buy and data_mod.is_usd_asset(trade_asset):
                raw_usd = mkt.get(trade_asset, 0.0)
                st.caption(
                    f"Prix en USD : **{raw_usd:.4f} $** → EUR : **{cur_p:.4f} €** "
                    f"(taux EUR/USD : {eurusd:.4f})"
                )

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
                premium = fin.pricing_option_bs(
                    S=raw_price if is_buy else cur_p * eurusd,
                    K=strike, T=T, r=r, sigma=vol, option_type=opt_kind
                )
                premium_eur = to_eur(trade_asset, premium) if is_buy else premium

                if is_buy:
                    trade_ticker = f"{trade_asset}_{opt_kind.upper()}_{strike:.1f}_{expiry_months}M"

                st.info(f"Volatilité historique estimée de {trade_asset} : **{vol*100:.1f}%**")
                try:
                    brut = fin.total_brut(qty, premium_eur)
                    comm = fin.calculer_commission(premium_eur, qty)
                    total = fin.total_net_achat(qty, premium_eur) if is_buy else fin.total_net_vente(qty, premium_eur)
                except Exception:
                    brut = comm = total = 0.0

                st.markdown(f"""
| Paramètre | Valeur |
|-----------|--------|
| Contrat | **{trade_ticker}** |
| Prime d'option | **{premium_eur:.4f} €** |
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
                price_to_use_check = (premium_eur if inst_type == "Option (Call / Put)" else cur_p)
                can_afford = int(p.cash // (price_to_use_check * 1.01)) if price_to_use_check > 0 else 0
                st.info(f"Capacité maximale d'achat : **{can_afford} unités** avec tes liquidités actuelles.")

    with col_r:
        if trade_asset is not None:
            st.markdown("#### Aperçu de l'ordre")
            action_label = "ACHETER" if is_buy else "VENDRE"
            if inst_type == "Cryptomonnaie":
                badge_color = "#F59E0B"
            elif inst_type == "Option (Call / Put)":
                badge_color = "#2563EB"
            else:
                badge_color = "#059669"
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
                if inst_type == "Option (Call / Put)":
                    price_to_use = premium_eur
                else:
                    price_to_use = cur_p
                msg = p.buy(trade_ticker, qty, price_to_use) if is_buy else p.sell(trade_ticker, qty, price_to_use)
                if "succès" in msg.lower() or "vendu" in msg.lower():
                    st.success(msg)
                    save()
                    st.rerun()
                else:
                    st.error(msg)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Positions
# ════════════════════════════════════════════════════════════════════════════
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
            if "_" in t:
                asset_type = "Option"
            elif t in data_mod.CRYPTO_ASSETS:
                asset_type = "Crypto"
            else:
                asset_type = "Action/ETF"
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
                "Quantité": st.column_config.NumberColumn(format="%.4f"),
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

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Historique des transactions
# ════════════════════════════════════════════════════════════════════════════
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
