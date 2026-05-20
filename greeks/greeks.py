import numpy as np
import pandas as pd
from scipy.stats import norm

def black_scholes_pricing(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """
    Calcule le prix d'une option européenne via la formule de Black-Scholes.
    S: Prix actuel du sous-jacent
    K: Prix d'exercice (Strike)
    T: Temps restant jusqu'à l'échéance (en années)
    r: Taux d'intérêt sans risque (ex: 0.02 pour 2%)
    sigma: Volatilité sous-jacente (ex: 0.20 pour 20%)
    option_type: "call" ou "put"
    """
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return 0.0
        
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type.lower() == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
    return float(price)

def calculate_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> dict:
    """
    Calcule les principales grecques (Delta, Gamma, Vega, Theta) pour une option.
    """
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0}
        
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    pdf_d1 = norm.pdf(d1)

    # Delta
    delta_call =  norm.cdf(d1)
    delta_put  =  norm.cdf(d1) - 1.0

    # Gamma & Vega (identiques call/put)
    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    vega  = S * np.sqrt(T) * pdf_d1

    # Theta
    term1      = -(S * pdf_d1 * sigma) / (2 * np.sqrt(T))
    theta_call =  term1 - r * K * np.exp(-r * T) * norm.cdf( d2)
    theta_put  =  term1 + r * K * np.exp(-r * T) * norm.cdf(-d2)

    # Rho
    rho_call =  K * T * np.exp(-r * T) * norm.cdf( d2)
    rho_put  = -K * T * np.exp(-r * T) * norm.cdf(-d2)

    # Rétrocompatibilité : delta/theta = version call par défaut
    is_put = option_type.lower() == "put"
    return {
        "delta":       float(delta_put  if is_put else delta_call),
        "delta_call":  float(delta_call),
        "delta_put":   float(delta_put),
        "gamma":       float(gamma),
        "vega":        float(vega),
        "theta":       float(theta_put  if is_put else theta_call),
        "theta_call":  float(theta_call),
        "theta_put":   float(theta_put),
        "rho_call":    float(rho_call),
        "rho_put":     float(rho_put),
    }

def calculate_historical_volatility(prices: pd.Series, is_crypto: bool = False) -> float:
    """
    Calcule la volatilité historique annualisée de l'actif.
    prices: Série de prix de clôture historiques
    is_crypto: Si vrai, utilise 365 jours de trading pour l'annualisation, sinon 252.
    """
    if len(prices) < 2:
        return 0.0
    
    # Calcul des rendements journaliers logarithmiques ou simples
    returns = prices.pct_change().dropna()
    
    # Écart-type journalier des rendements
    daily_vol = returns.std()
    
    # Annualisation
    days = 365.0 if is_crypto else 252.0
    ann_vol = daily_vol * np.sqrt(days)
    
    return float(ann_vol)

def calculate_beta(asset_prices: pd.Series, market_prices: pd.Series) -> float:
    """
    Calcule le bêta de l'actif par rapport à un indice de référence.
    """
    if len(asset_prices) < 5 or len(market_prices) < 5:
        return 1.0
        
    # Copie des séries et suppression des timezones pour éviter le bug d'alignement pandas
    s_asset = asset_prices.copy()
    if hasattr(s_asset.index, "tz") and s_asset.index.tz is not None:
        s_asset.index = s_asset.index.tz_localize(None)
        
    s_market = market_prices.copy()
    if hasattr(s_market.index, "tz") and s_market.index.tz is not None:
        s_market.index = s_market.index.tz_localize(None)
        
    # Alignement des données sur les mêmes dates
    df = pd.DataFrame({"asset": s_asset, "market": s_market}).dropna()
    if len(df) < 5:
        return 1.0
        
    # Rendements journaliers
    df_ret = df.pct_change().dropna()
    if len(df_ret) < 5:
        return 1.0
        
    covariance = df_ret["asset"].cov(df_ret["market"])
    market_variance = df_ret["market"].var()
    
    if market_variance == 0:
        return 1.0
        
    beta = covariance / market_variance
    return float(beta)

def calculate_sharpe_ratio(prices: pd.Series, risk_free_rate: float = 0.02, is_crypto: bool = False) -> float:
    """
    Calcule le ratio de Sharpe historique de l'actif.
    """
    if len(prices) < 5:
        return 0.0
        
    returns = prices.pct_change().dropna()
    if len(returns) == 0:
        return 0.0
        
    days = 365.0 if is_crypto else 252.0
    
    # Rendement journalier moyen annualisé
    mean_return = returns.mean() * days
    
    # Volatilité annualisée
    vol = returns.std() * np.sqrt(days)
    
    if vol == 0:
        return 0.0
        
    sharpe = (mean_return - risk_free_rate) / vol
    return float(sharpe)
