"""
bot.py — Moteur du robot de trading automatique (SMA, RSI et Machine Learning)
=============================================================================

Ce module définit la classe TradingBot qui exécute périodiquement des algorithmes
de trading automatique sur le portefeuille de l'utilisateur connecté.
Il intègre désormais une stratégie prédictive basée sur le Machine Learning
(Random Forest Classifier de scikit-learn).

Relations avec les autres modules :
----------------------------------
- data.data : Récupère les historiques de prix nécessaires pour entraîner les modèles.
- simulation.simulation : Calcule les indicateurs techniques standards (RSI, SMA).
- equities.equities : Exécute les ordres d'achat/vente sur le portefeuille en base de données.
- 4_🤖_Bot.py : Contrôle l'état du bot et affiche la console de logs dans Streamlit.
"""

import time
from datetime import datetime
import pandas as pd
import numpy as np
from equities.equities import Portfolio
import data.data as data
import simulation.simulation as sim

class TradingBot:
    def __init__(self, portfolio: Portfolio, strategy: str = "SMA"):
        self.portfolio = portfolio
        self.strategy = strategy
        self.is_running = False
        self.logs = []

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")

    def run_one_iteration(self, ticker_name: str, period: str = "1mo", interval: str = "1d") -> str:
        """
        Exécute une seule décision de trading basée sur les cours actuels et historiques.
        """
        self.log(f"Évaluation du marché pour {ticker_name} avec la stratégie {self.strategy}...")
        
        try:
            # Récupération historique pour calculer l'indicateur
            df = data.recuperer_historique(ticker_name, period, interval)
            if df.empty or len(df) < 10:
                self.log(f"Données insuffisantes pour {ticker_name}.")
                return "Données insuffisantes."
            
            close_prices = df['Close']
            current_price = close_prices.iloc[-1]
            
            # Évaluation des signaux
            signal = 0  # 0 = Hold, 1 = Buy, -1 = Sell
            
            if self.strategy == "SMA":
                # SMA courte vs SMA longue
                sma_short = sim.calculate_sma(close_prices, 5).iloc[-1]
                sma_long = sim.calculate_sma(close_prices, 15).iloc[-1]
                self.log(f"SMA(5): {sma_short:.2f} | SMA(15): {sma_long:.2f} | Cours: {current_price:.2f}")
                if sma_short > sma_long:
                    signal = 1
                elif sma_short < sma_long:
                    signal = -1
                    
            elif self.strategy == "RSI":
                rsi_val = sim.calculate_rsi(close_prices, 7).iloc[-1]
                self.log(f"RSI(7): {rsi_val:.2f} | Cours: {current_price:.2f}")
                if rsi_val < 35:
                    signal = 1
                elif rsi_val > 65:
                    signal = -1
                    
            elif self.strategy == "ML_RF":
                # Stratégie Machine Learning (Random Forest)
                self.log("Entraînement du modèle Random Forest sur l'historique 1 an...")
                # On utilise un historique plus large pour l'entraînement
                df_ml = data.recuperer_historique(ticker_name, "1y", "1d")
                if len(df_ml) < 40:
                    self.log("Historique 1 an insuffisant pour entraîner le modèle (min 40 jours requis).")
                    return "Données insuffisantes."
                
                close_ml = df_ml['Close']
                returns_1d = close_ml.pct_change()
                returns_3d = close_ml.pct_change(3)
                returns_5d = close_ml.pct_change(5)
                
                # Moyennes mobiles
                sma_5 = sim.calculate_sma(close_ml, 5)
                sma_15 = sim.calculate_sma(close_ml, 15)
                sma_ratio = sma_5 / sma_15
                
                # Indicateurs RSI et Volatilité
                rsi_14 = sim.calculate_rsi(close_ml, 14)
                vol_10 = returns_1d.rolling(10).std()
                
                # Construction de la matrice de features X
                features = pd.DataFrame({
                    "ret1": returns_1d,
                    "ret3": returns_3d,
                    "ret5": returns_5d,
                    "sma_ratio": sma_ratio,
                    "rsi": rsi_14,
                    "vol10": vol_10
                })
                
                # Target : est-ce que le cours est supérieur dans 3 jours (Horizon de 3 jours) ?
                target = (close_ml.shift(-3) > close_ml).astype(int)
                
                # Préparation du dataset
                dataset = features.copy()
                dataset["target"] = target
                dataset = dataset.dropna()
                
                if len(dataset) < 25:
                    self.log("Données nettoyées insuffisantes après retrait des NaNs.")
                    return "Données insuffisantes."
                
                # Séparation des variables
                X_train = dataset.drop(columns=["target"])
                y_train = dataset["target"]
                
                # Dernière ligne pour la prédiction en direct (on remplit les NaNs éventuels par précaution)
                latest_features = features.iloc[[-1]].fillna(method="ffill").fillna(0.0)
                
                # Modèle Random Forest Classifier
                from sklearn.ensemble import RandomForestClassifier
                clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
                clf.fit(X_train, y_train)
                
                # Prédiction et probabilités associées
                pred = clf.predict(latest_features)[0]
                prob = clf.predict_proba(latest_features)[0]
                prob_up = prob[1] * 100
                
                self.log(f"ML RF: Probabilité de hausse à 3j = {prob_up:.1f}%")
                
                # Seuil de décision asymétrique (éviter le bruit)
                if pred == 1 and prob_up > 55.0:
                    signal = 1
                elif pred == 0 or prob_up < 45.0:
                    signal = -1
                else:
                    signal = 0
            
            # Application des ordres
            if signal == 1:
                # Signal d'achat : on achète autant que possible
                cash_dispo = self.portfolio.cash
                if cash_dispo < 10:
                    self.log("Fonds insuffisants pour placer un ordre d'achat.")
                    return "Fonds insuffisants."
                
                prix_avec_comm = current_price * 1.01
                qty_to_buy = int(cash_dispo // prix_avec_comm)
                
                if qty_to_buy > 0:
                    self.log(f"Signal ACHAT généré. Achat de {qty_to_buy} unités de {ticker_name} à {current_price:.2f} €.")
                    msg = self.portfolio.buy(ticker_name, qty_to_buy, current_price)
                    self.log(f"Résultat ordre : {msg}")
                    return msg
                else:
                    self.log("Fonds insuffisants pour acheter 1 unité.")
                    return "Fonds insuffisants pour acheter 1 unité."
                    
            elif signal == -1:
                # Signal de vente : on vend tout ce qu'on détient sur cet actif
                if ticker_name in self.portfolio.positions:
                    qty_to_sell = self.portfolio.positions[ticker_name]["quantity"]
                    self.log(f"Signal VENTE généré. Vente de {qty_to_sell} unités de {ticker_name} à {current_price:.2f} €.")
                    msg = self.portfolio.sell(ticker_name, qty_to_sell, current_price)
                    self.log(f"Résultat ordre : {msg}")
                    return msg
                else:
                    self.log(f"Signal VENTE généré mais aucun actif {ticker_name} détenu.")
                    return "Rien à vendre."
            else:
                self.log("Signal NEUTRE. Aucune transaction effectuée.")
                return "Pas de signal."
                
        except Exception as e:
            msg_err = f"Erreur lors de l'exécution du bot : {e}"
            self.log(msg_err)
            return msg_err
