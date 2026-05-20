"""
visualisation.py — Bibliothèque de graphiques enrichis pour le Simulateur Boursier L1
Graphiques disponibles :
  - Candlestick + SMA + RSI + Volume (graphique principal multi-panneaux)
  - Heatmap de corrélation entre actifs
  - Jauge de sentiment (RSI)
  - Distribution des rendements (histogramme)
  - Évolution portefeuille vs benchmark (backtesting)
  - Surface 3D Black-Scholes (options)
  - Scatter Risk/Return
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from greeks.greeks import black_scholes_pricing


# ─────────────────────────────────────────────
#  GRAPHIQUE PRINCIPAL : Candlestick + indicateurs
# ─────────────────────────────────────────────
def plot_candlestick(df: pd.DataFrame, ticker_name: str, show_volume: bool = True) -> go.Figure:
    """
    Graphique principal multi-panneaux :
      - Panneau 1 (70%) : Chandeliers + SMA20 + SMA50 + Bollinger Bands
      - Panneau 2 (15%) : Volume coloré (vert/rouge)
      - Panneau 3 (15%) : RSI(14) avec zones surachat/survente
    """
    rows = 3 if show_volume else 1
    row_heights = [0.65, 0.18, 0.17] if show_volume else [1.0]
    subplot_titles = ([ticker_name, "Volume", "RSI (14)"] if show_volume else [ticker_name])

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=row_heights,
        subplot_titles=subplot_titles,
    )

    # — Chandeliers
    colors_up   = "#26A69A"
    colors_down = "#EF5350"
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        increasing_line_color=colors_up,
        decreasing_line_color=colors_down,
        name="Prix",
    ), row=1, col=1)

    # — SMA 20 & 50
    sma20 = df["Close"].rolling(20).mean()
    sma50 = df["Close"].rolling(50).mean()
    fig.add_trace(go.Scatter(x=df.index, y=sma20, line=dict(color="#FFA726", width=1.5), name="SMA 20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=sma50, line=dict(color="#42A5F5", width=1.5), name="SMA 50"), row=1, col=1)

    # — Bandes de Bollinger (SMA20 ± 2σ)
    std20 = df["Close"].rolling(20).std()
    bb_up = sma20 + 2 * std20
    bb_dn = sma20 - 2 * std20
    fig.add_trace(go.Scatter(x=df.index, y=bb_up, line=dict(color="rgba(200,200,200,0.3)", width=1, dash="dot"), name="BB +2σ"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=bb_dn, line=dict(color="rgba(200,200,200,0.3)", width=1, dash="dot"),
                             fill="tonexty", fillcolor="rgba(200,200,200,0.07)", name="BB -2σ"), row=1, col=1)

    if show_volume and "Volume" in df.columns:
        # — Volume coloré
        vol_colors = [colors_up if c >= o else colors_down
                      for c, o in zip(df["Close"], df["Open"])]
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=vol_colors, name="Volume", opacity=0.7), row=2, col=1)

        # — RSI(14)
        delta = df["Close"].diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, np.nan)
        rsi   = 100 - 100 / (1 + rs)

        fig.add_trace(go.Scatter(x=df.index, y=rsi, line=dict(color="#CE93D8", width=1.5), name="RSI 14"), row=3, col=1)
        fig.add_hline(y=70, line=dict(color=colors_down, dash="dash", width=1), row=3, col=1)
        fig.add_hline(y=30, line=dict(color=colors_up,   dash="dash", width=1), row=3, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor=colors_down, opacity=0.07, line_width=0, row=3, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor=colors_up,   opacity=0.07, line_width=0, row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.02, x=0),
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=40, b=10),
        height=600,
    )
    fig.update_yaxes(gridcolor="#1F2937")
    fig.update_xaxes(gridcolor="#1F2937")
    return fig


# ─────────────────────────────────────────────
#  COURS EN TEMPS RÉEL (1 min intraday)
# ─────────────────────────────────────────────
def plot_realtime(df: pd.DataFrame, ticker_name: str, current_price: float) -> go.Figure:
    """
    Graphique intraday en ligne pour l'affichage temps réel.
    Affiche le cours de la journée + VWAP.
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.04,
                        subplot_titles=[f"{ticker_name} — Temps réel (1 min)", "Volume"])

    close = df["Close"]
    first = close.iloc[0] if len(close) > 0 else current_price
    color = "#26A69A" if current_price >= first else "#EF5350"

    fig.add_trace(go.Scatter(
        x=df.index, y=close,
        fill="tozeroy", fillcolor=f"rgba({('38,166,154' if color=='#26A69A' else '239,83,80')},0.15)",
        line=dict(color=color, width=2),
        name="Cours",
    ), row=1, col=1)

    # VWAP
    if "Volume" in df.columns and df["Volume"].sum() > 0:
        vwap = (close * df["Volume"]).cumsum() / df["Volume"].cumsum()
        fig.add_trace(go.Scatter(x=df.index, y=vwap, line=dict(color="#FFA726", width=1.5, dash="dot"), name="VWAP"), row=1, col=1)

        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=color, opacity=0.6, name="Volume"), row=2, col=1)

    # Ligne de cours actuel
    fig.add_hline(y=current_price, line=dict(color=color, dash="dash", width=1), row=1, col=1)

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
        hovermode="x unified", margin=dict(l=10, r=10, t=40, b=10), height=450,
        xaxis_rangeslider_visible=False,
    )
    return fig


# ─────────────────────────────────────────────
#  HEATMAP DE CORRÉLATION
# ─────────────────────────────────────────────
def plot_correlation_heatmap(prices_dict: dict) -> go.Figure:
    """
    Heatmap de corrélation entre les rendements journaliers de plusieurs actifs.
    prices_dict : {nom_actif: pd.Series de prix de clôture}
    """
    returns_df = pd.DataFrame({k: v.pct_change() for k, v in prices_dict.items()}).dropna()
    corr = returns_df.corr()

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        zmin=-1, zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        hovertemplate="Corrélation %{x} / %{y} : %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        title="Matrice de Corrélation des Rendements",
        template="plotly_dark", paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
        margin=dict(l=10, r=10, t=50, b=10), height=500,
    )
    return fig


# ─────────────────────────────────────────────
#  DISTRIBUTION DES RENDEMENTS
# ─────────────────────────────────────────────
def plot_returns_distribution(close: pd.Series, ticker_name: str) -> go.Figure:
    """Histogramme des rendements journaliers + courbe normale théorique."""
    returns = close.pct_change().dropna() * 100
    mean, std = returns.mean(), returns.std()

    x_range = np.linspace(returns.min(), returns.max(), 300)
    normal_pdf = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_range - mean) / std) ** 2)
    # Mise à l'échelle pour superposition
    bin_width = (returns.max() - returns.min()) / 40
    normal_pdf_scaled = normal_pdf * len(returns) * bin_width

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=returns, nbinsx=40,
        marker_color="#42A5F5", opacity=0.75, name="Rendements réels",
        marker_line=dict(color="#0E1117", width=0.5)
    ))
    fig.add_trace(go.Scatter(
        x=x_range, y=normal_pdf_scaled,
        line=dict(color="#FFA726", width=2), name="Distribution Normale"
    ))
    fig.add_vline(x=mean, line=dict(color="#26A69A", dash="dash"), annotation_text=f"μ={mean:.2f}%")
    fig.add_vline(x=mean - std, line=dict(color="#EF5350", dash="dot", width=1), annotation_text=f"-1σ")
    fig.add_vline(x=mean + std, line=dict(color="#EF5350", dash="dot", width=1), annotation_text=f"+1σ")

    fig.update_layout(
        title=f"Distribution des Rendements Journaliers — {ticker_name}",
        xaxis_title="Rendement (%)", yaxis_title="Fréquence",
        template="plotly_dark", paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
        bargap=0.05, hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10), height=400,
    )
    return fig


# ─────────────────────────────────────────────
#  SCATTER RISQUE / RENDEMENT
# ─────────────────────────────────────────────
def plot_risk_return(data_dict: dict) -> go.Figure:
    """
    Nuage de points Rendement Annualisé vs Volatilité Annualisée.
    data_dict : {nom: {"return": float, "volatility": float}}
    """
    names  = list(data_dict.keys())
    rets   = [data_dict[n]["return"]     for n in names]
    vols   = [data_dict[n]["volatility"] for n in names]
    sharpe = [r / v if v > 0 else 0 for r, v in zip(rets, vols)]

    fig = go.Figure(go.Scatter(
        x=vols, y=rets,
        mode="markers+text",
        text=names,
        textposition="top center",
        marker=dict(
            size=12, color=sharpe, colorscale="RdYlGn",
            colorbar=dict(title="Sharpe"), showscale=True,
            line=dict(color="#0E1117", width=1)
        ),
        hovertemplate="<b>%{text}</b><br>Volatilité: %{x:.1f}%<br>Rendement: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title="Carte Risque / Rendement",
        xaxis_title="Volatilité annualisée (%)",
        yaxis_title="Rendement annualisé (%)",
        template="plotly_dark", paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
        margin=dict(l=10, r=10, t=50, b=10), height=450,
    )
    return fig


# ─────────────────────────────────────────────
#  BACKTESTING : Évolution du portefeuille
# ─────────────────────────────────────────────
def plot_backtest_performance(backtest_results: dict, strategy_name: str) -> go.Figure:
    """Graphique de comparaison stratégie vs Buy & Hold avec drawdown."""
    dates             = backtest_results["dates"]
    strategy_history  = backtest_results["portfolio_history"]
    bh_history        = backtest_results.get("portfolio_history_bh", None)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.70, 0.30], vertical_spacing=0.05,
                        subplot_titles=["Évolution du Portefeuille", "Drawdown (%)"])

    fig.add_trace(go.Scatter(
        x=dates, y=strategy_history,
        line=dict(color="#26A69A", width=2), name=f"Stratégie {strategy_name}",
        fill="tozeroy", fillcolor="rgba(38,166,154,0.08)",
    ), row=1, col=1)

    if bh_history is not None:
        fig.add_trace(go.Scatter(
            x=dates, y=bh_history,
            line=dict(color="#FFA726", width=1.5, dash="dot"), name="Buy & Hold passif",
        ), row=1, col=1)

    # Drawdown
    portfolio_series = pd.Series(strategy_history)
    rolling_max = portfolio_series.cummax()
    drawdown = ((portfolio_series - rolling_max) / rolling_max) * 100
    fig.add_trace(go.Scatter(
        x=dates, y=drawdown,
        fill="tozeroy", fillcolor="rgba(239,83,80,0.2)",
        line=dict(color="#EF5350", width=1), name="Drawdown",
    ), row=2, col=1)

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
        hovermode="x unified", margin=dict(l=10, r=10, t=40, b=10), height=550,
    )
    return fig


# ─────────────────────────────────────────────
#  3D : Surface Black-Scholes
# ─────────────────────────────────────────────
def plot_3d_option_surface(S: float, r: float, sigma: float, option_type: str = "call") -> go.Figure:
    """Surface 3D : prix option = f(Strike K, Maturité T)."""
    strikes    = np.linspace(S * 0.7, S * 1.3, 35)
    maturities = np.linspace(0.05, 3.0, 35)
    K_grid, T_grid = np.meshgrid(strikes, maturities)
    Z_grid = np.zeros(K_grid.shape)

    for i in range(len(maturities)):
        for j in range(len(strikes)):
            Z_grid[i, j] = black_scholes_pricing(S=S, K=strikes[j], T=maturities[i],
                                                  r=r, sigma=sigma, option_type=option_type)

    colorscale = "Viridis" if option_type == "call" else "Plasma"
    fig = go.Figure(data=[go.Surface(
        x=K_grid, y=T_grid, z=Z_grid,
        colorscale=colorscale, colorbar=dict(title="Prix (€/$)"),
        contours=dict(z=dict(show=True, usecolormap=True, project_z=True)),
    )])
    fig.update_layout(
        title=f"Surface de Pricing — Option {option_type.upper()} (Black-Scholes 1973)",
        scene=dict(
            xaxis=dict(title="Strike K", backgroundcolor="#0E1117", gridcolor="#1F2937"),
            yaxis=dict(title="Maturité T (années)", backgroundcolor="#0E1117", gridcolor="#1F2937"),
            zaxis=dict(title="Prix de l'option", backgroundcolor="#0E1117", gridcolor="#1F2937"),
            bgcolor="#0E1117",
            camera=dict(eye=dict(x=1.5, y=-1.5, z=0.8))
        ),
        paper_bgcolor="#0E1117",
        template="plotly_dark",
        margin=dict(l=0, r=0, t=50, b=0),
        width=850, height=620,
    )
    return fig


# ─────────────────────────────────────────────
#  JAUGE RSI
# ─────────────────────────────────────────────
def plot_rsi_gauge(rsi_value: float, ticker_name: str) -> go.Figure:
    """Jauge demi-cercle affichant la valeur RSI actuelle."""
    if rsi_value < 30:
        color, label = "#26A69A", "SURVENTE (Potentiel achat)"
    elif rsi_value > 70:
        color, label = "#EF5350", "SURACHAT (Potentiel vente)"
    else:
        color, label = "#FFA726", "NEUTRE"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rsi_value,
        title={"text": f"RSI(14) — {ticker_name}<br><span style='font-size:0.8em;color:{color}'>{label}</span>",
               "font": {"size": 16}},
        delta={"reference": 50},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "white"},
            "bar": {"color": color},
            "bgcolor": "#1F2937",
            "borderwidth": 2,
            "bordercolor": "#374151",
            "steps": [
                {"range": [0,  30], "color": "rgba(38,166,154,0.2)"},
                {"range": [30, 70], "color": "rgba(255,167,38,0.1)"},
                {"range": [70, 100],"color": "rgba(239,83,80,0.2)"},
            ],
            "threshold": {"line": {"color": "white", "width": 2}, "thickness": 0.8, "value": rsi_value},
        }
    ))
    fig.update_layout(
        paper_bgcolor="#0E1117", font=dict(color="white"),
        margin=dict(l=20, r=20, t=60, b=20), height=280,
    )
    return fig
