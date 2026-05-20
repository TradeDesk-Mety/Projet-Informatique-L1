import time
from datetime import datetime
import pandas as pd
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
            
            # Application des ordres
            if signal == 1:
                # Signal d'achat : on achète autant que possible
                cash_dispo = self.portfolio.cash
                if cash_dispo < 10:
                    self.log("Fonds insuffisants pour placer un ordre d'achat.")
                    return "Fonds insuffisants."
                
                # Nombre d'actions arrondi qu'on peut acheter (en enlevant 1% de commission estimée)
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
