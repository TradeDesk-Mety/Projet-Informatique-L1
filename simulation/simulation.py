import pandas as pd
import numpy as np

def calculate_sma(prices: pd.Series, window: int) -> pd.Series:
    """Calcule la moyenne mobile simple (SMA)."""
    return prices.rolling(window=window).mean()

def calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Calcule l'indicateur RSI (Relative Strength Index)."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / (loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def backtest_strategy(prices: pd.Series, strategy_type: str = "SMA", params: dict = None, df_ohlcv: pd.DataFrame = None) -> dict:
    """
    Simule un backtesting historique d'une stratégie sur une série temporelle de prix.

    Paramètres
    ----------
    prices       : Série temporelle des prix de clôture (Close).
    strategy_type: "SMA", "RSI" ou "VWAP".
    params       : Dictionnaire de paramètres spécifiques à la stratégie.
    df_ohlcv     : DataFrame OHLCV complet (requis pour la stratégie VWAP).

    Capital initial : 10 000 € | Commission : 1% par transaction.
    """
    if len(prices) < 20:
        return {"error": "Pas assez de données pour le backtest (minimum 20 points de données requis)."}
        
    initial_cash = 10000.0
    cash = initial_cash
    position = 0.0  # Quantité d'actifs détenue
    commission_rate = 0.01  # 1% commission
    
    portfolio_values = []
    dates = prices.index
    
    # Calcul des indicateurs
    if strategy_type == "SMA":
        short_w = params.get("short_window", 20) if params else 20
        long_w = params.get("long_window", 50) if params else 50
        short_sma = calculate_sma(prices, short_w)
        long_sma = calculate_sma(prices, long_w)
        
        # Signaux: 1 = achat, -1 = vente, 0 = rien
        signals = np.zeros(len(prices))
        # Achat quand SMA courte > SMA longue
        signals[short_sma > long_sma] = 1
        # Vente quand SMA courte < SMA longue
        signals[short_sma < long_sma] = -1
        
    elif strategy_type == "RSI":
        rsi_w = params.get("rsi_window", 14) if params else 14
        oversold = params.get("oversold", 30) if params else 30
        overbought = params.get("overbought", 70) if params else 70
        rsi = calculate_rsi(prices, rsi_w)
        
        signals = np.zeros(len(prices))
        # Achat quand RSI descend sous le seuil de survente
        signals[rsi < oversold] = 1
        # Vente quand RSI monte au-dessus du seuil de surachat
        signals[rsi > overbought] = -1

    elif strategy_type == "VWAP":
        # =====================================================================
        # STRATÉGIE VWAP en backtesting
        # =====================================================================
        # On calcule un VWAP glissant sur une fenêtre paramétrable (défaut 20 jours).
        # Achat si le cours est > 1.5% sous le VWAP, vente si > 1.5% au-dessus.
        # =====================================================================
        vwap_window = params.get("vwap_window", 20) if params else 20
        threshold   = params.get("threshold", 1.5) if params else 1.5  # en %

        if df_ohlcv is not None and "High" in df_ohlcv.columns and "Volume" in df_ohlcv.columns:
            typical_price = (df_ohlcv["High"] + df_ohlcv["Low"] + df_ohlcv["Close"]) / 3
            cum_tp_vol = (typical_price * df_ohlcv["Volume"]).rolling(vwap_window).sum()
            cum_vol    = df_ohlcv["Volume"].rolling(vwap_window).sum()
            vwap       = cum_tp_vol / cum_vol
        else:
            # Fallback : VWAP approximé par la SMA(vwap_window) si pas de données OHLCV
            vwap = calculate_sma(prices, vwap_window)

        signals = np.zeros(len(prices))
        lower_band = vwap * (1 - threshold / 100)
        upper_band = vwap * (1 + threshold / 100)

        for i in range(len(prices)):
            if pd.isna(vwap.iloc[i]):
                continue
            if prices.iloc[i] < lower_band.iloc[i]:
                signals[i] = 1   # Sous-évalué : achat
            elif prices.iloc[i] > upper_band.iloc[i]:
                signals[i] = -1  # Surévalué : vente
    else:
        # Par défaut : Buy & Hold
        signals = np.ones(len(prices))
        signals[0] = 1 # Acheter au début et garder
        
    trades_count = 0
    total_commission = 0.0
    
    # Simulation jour après jour
    for i in range(len(prices)):
        price = prices.iloc[i]
        signal = signals[i]
        
        # Vérification achat
        if signal == 1 and position == 0.0:
            # On achète tout ce qu'on peut avec notre cash
            brut_val = cash / (1 + commission_rate)
            commission = cash - brut_val
            position = brut_val / price
            cash = 0.0
            total_commission += commission
            trades_count += 1
            
        # Vérification vente
        elif signal == -1 and position > 0.0:
            # On vend tout
            brut_val = position * price
            commission = brut_val * commission_rate
            cash = brut_val - commission
            position = 0.0
            total_commission += commission
            trades_count += 1
            
        # Valeur actuelle du portefeuille (cash + valeur des actifs)
        current_value = cash + (position * price)
        portfolio_values.append(current_value)
        
    # Création du DataFrame de historique de portefeuille
    portfolio_history = pd.Series(portfolio_values, index=dates)
    
    # Statistiques de performance
    final_value = portfolio_values[-1]
    strategy_return = ((final_value - initial_cash) / initial_cash) * 100
    
    # Rendement passif (Buy & Hold) pour comparer
    buy_hold_qty = initial_cash / (1 + commission_rate) / prices.iloc[0]
    bh_comm = initial_cash - (initial_cash / (1 + commission_rate))
    bh_final = (buy_hold_qty * prices.iloc[-1])
    bh_return = ((bh_final - initial_cash) / initial_cash) * 100
    
    # Calcul du Drawdown Maximum
    roll_max = portfolio_history.cummax()
    drawdown = (portfolio_history - roll_max) / roll_max
    max_drawdown = drawdown.min() * 100
    
    return {
        "dates":               dates,
        "prices":              prices.tolist(),
        "signals":             signals.tolist(),
        "portfolio_history":   portfolio_history.tolist(),
        "equity_curve":        portfolio_history.tolist(),   # alias utilisé par le mode Comparatif
        "benchmark_curve":     [                             # alias utilisé par le mode Comparatif
            (initial_cash / (1 + commission_rate) / prices.iloc[0]) * p
            for p in prices.tolist()
        ],
        "portfolio_history_bh": [
            (initial_cash / (1 + commission_rate) / prices.iloc[0]) * p
            for p in prices.tolist()
        ],
        "final_value":         final_value,
        "strategy_return":     strategy_return,
        "benchmark_return":    bh_return,
        "trades_count":        trades_count,
        "total_commission":    total_commission,
        "max_drawdown":        max_drawdown,
    }

def monte_carlo_simulation(prices: pd.Series, days_to_simulate: int = 30, num_simulations: int = 100) -> dict:
    """
    Exécute une simulation de Monte-Carlo basée sur le Mouvement Brownien Géométrique (GBM).
    
    L'idée est de générer plusieurs scénarios (chemins) possibles pour le prix futur
    en se basant sur la dérive (drift) historique et la volatilité historique.
    """
    if len(prices) < 2:
        return {"error": "Pas assez de données pour la simulation de Monte-Carlo."}
        
    # Calcul des rendements journaliers historiques
    returns = prices.pct_change().dropna()
    
    # Calcul de la dérive (drift) et de la volatilité
    mu = returns.mean()
    sigma = returns.std()
    
    # Drift (dérive théorique du mouvement brownien géométrique)
    drift = mu - (0.5 * sigma**2)
    
    # Prix de départ pour la simulation
    last_price = prices.iloc[-1]
    
    # Matrice pour stocker tous les chemins simulés
    # Lignes = jours simulés, Colonnes = numéro de simulation
    simulated_paths = np.zeros((days_to_simulate, num_simulations))
    
    for i in range(num_simulations):
        # Génération des chocs aléatoires (Z ~ N(0, 1))
        Z = np.random.normal(0, 1, days_to_simulate)
        
        # Calcul des rendements simulés : e^(drift + sigma * Z)
        daily_returns_simulated = np.exp(drift + sigma * Z)
        
        # Construction du chemin de prix en cascade
        price_path = np.zeros(days_to_simulate)
        price_path[0] = last_price * daily_returns_simulated[0]
        for t in range(1, days_to_simulate):
            price_path[t] = price_path[t-1] * daily_returns_simulated[t]
            
        simulated_paths[:, i] = price_path
        
    # On calcule la trajectoire moyenne de tous les scénarios
    mean_path = simulated_paths.mean(axis=1)
    
    return {
        "last_price": last_price,
        "days_to_simulate": days_to_simulate,
        "num_simulations": num_simulations,
        "mean_path": mean_path.tolist(),
        "paths": simulated_paths.tolist()
    }
