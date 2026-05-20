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

def backtest_strategy(prices: pd.Series, strategy_type: str = "SMA", params: dict = None) -> dict:
    """
    Simule un backtesting historique d'une stratégie sur une série temporelle de prix.
    Initial cash: 10,000 EUR
    Commission: 1% par transaction (achat/vente)
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
