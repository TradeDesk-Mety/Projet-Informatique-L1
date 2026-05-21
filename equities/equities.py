"""
equities.py — Gestion du portefeuille de trading (Positions, transactions, PAMP)
=============================================================================

Ce module définit la classe `Portfolio` qui modélise le portefeuille de paper trading.

Relations avec les autres modules :
----------------------------------
- finance.py (C++) : utilisé pour calculer le coût net d'achat, le montant net reçu à la vente,
  les commissions de courtage (1%), et le ROI global.
- database.py : fournit la connexion SQLite pour persister l'état du portefeuille.
- web.py & pages : manipulent l'objet `Portfolio` stocké en session pour exécuter les ordres,
  afficher les positions et sauvegarder l'état de l'utilisateur connecté.
"""

import json
import os
from datetime import datetime
import finance.finance as fin

class Portfolio:
    def __init__(self, initial_cash: float = 10000.0):
        self.cash = float(initial_cash)
        self.positions = {}  # Format: {ticker: {"quantity": int, "avg_price": float}}
        self.transactions = []  # Liste de dictionnaires décrivant les transactions effectuées
        self.initial_cash = float(initial_cash)

    def buy(self, ticker: str, quantity: int, price: float) -> str:
        """
        Achète un actif (action, ETF ou option).
        Calcule le coût total net (brut + commission) avec le moteur C++.
        """
        if quantity <= 0:
            return "La quantité doit être strictement positive."
        if price <= 0:
            return "Le prix doit être strictement positif."

        try:
            # Calcul du coût net d'achat via C++ (brut + commission de 1%)
            total_net = fin.total_net_achat(quantity, price)
            commission = fin.calculer_commission(price, quantity)
        except Exception as e:
            return f"Erreur lors des calculs financiers : {e}"

        if self.cash < total_net:
            return f"Fonds insuffisants. Requis: {total_net:.2f} €, Disponible: {self.cash:.2f} €"

        # Déduction du cash
        self.cash -= total_net

        # Mise à jour des positions
        if ticker in self.positions:
            pos = self.positions[ticker]
            new_qty = pos["quantity"] + quantity
            # Calcul du prix d'achat moyen pondéré (PAMP)
            new_avg = ((pos["quantity"] * pos["avg_price"]) + (quantity * price)) / new_qty
            self.positions[ticker] = {"quantity": new_qty, "avg_price": new_avg}
        else:
            self.positions[ticker] = {"quantity": quantity, "avg_price": price}

        # Enregistrement de la transaction
        trade = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "ACHAT",
            "ticker": ticker,
            "quantity": quantity,
            "price": price,
            "commission": commission,
            "total_net": total_net
        }
        self.transactions.append(trade)
        return "Achat effectué avec succès."

    def sell(self, ticker: str, quantity: int, price: float) -> str:
        """
        Vend un actif (action, ETF ou option).
        Calcule le montant net reçu (brut - commission) avec le moteur C++.
        """
        if quantity <= 0:
            return "La quantité doit être strictement positive."
        if price <= 0:
            return "Le prix doit être strictement positif."

        if ticker not in self.positions or self.positions[ticker]["quantity"] < quantity:
            available = self.positions[ticker]["quantity"] if ticker in self.positions else 0
            return f"Quantité insuffisante en portefeuille. Disponible: {available}."

        try:
            # Calcul du montant net de la vente via C++ (brut - commission de 1%)
            total_net = fin.total_net_vente(quantity, price)
            commission = fin.calculer_commission(price, quantity)
        except Exception as e:
            return f"Erreur lors des calculs financiers : {e}"

        # Ajout au cash
        self.cash += total_net

        # Mise à jour des positions
        self.positions[ticker]["quantity"] -= quantity
        if self.positions[ticker]["quantity"] == 0:
            del self.positions[ticker]

        # Enregistrement de la transaction
        trade = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "VENTE",
            "ticker": ticker,
            "quantity": quantity,
            "price": price,
            "commission": commission,
            "total_net": total_net
        }
        self.transactions.append(trade)
        return "Vente effectuée avec succès."

    def get_portfolio_value(self, current_prices: dict) -> float:
        """
        Calcule la valeur totale actuelle du portefeuille :
        Cash + Somme(quantité * prix_actuel)
        """
        assets_value = 0.0
        for ticker, pos in self.positions.items():
            price = current_prices.get(ticker, pos["avg_price"])
            assets_value += pos["quantity"] * price
        return self.cash + assets_value

    def get_total_performance(self, current_prices: dict) -> float:
        """
        Calcule la performance globale en pourcentage (ROI).
        """
        total_val = self.get_portfolio_value(current_prices)
        if self.initial_cash <= 0:
            return 0.0
        try:
            # Utilisation du moteur C++ pour calculer le ROI %
            return fin.calculer_performance(self.initial_cash, total_val)
        except Exception:
            return ((total_val - self.initial_cash) / self.initial_cash) * 100.0

    def to_dict(self) -> dict:
        return {
            "cash": self.cash,
            "initial_cash": self.initial_cash,
            "positions": self.positions,
            "transactions": self.transactions
        }

    def from_dict(self, data: dict):
        self.cash = float(data.get("cash", 10000.0))
        self.initial_cash = float(data.get("initial_cash", 10000.0))
        self.positions = data.get("positions", {})
        self.transactions = data.get("transactions", [])

    def save_to_db(self, user_id: int = 1, db_path: str = None):
        """Sauvegarde l'état du portefeuille pour un utilisateur spécifique dans SQL."""
        import sqlite3
        if db_path is None:
            from data.database import get_portfolio_connection
            
        conn = get_portfolio_connection()
        try:
            cursor = conn.cursor()
            
            # 1. Sauvegarde du solde cash
            cursor.execute("DELETE FROM portfolio_state WHERE user_id = ?", (user_id,))
            cursor.execute("INSERT INTO portfolio_state (user_id, cash, initial_cash) VALUES (?, ?, ?)", 
                           (user_id, self.cash, self.initial_cash))
            
            # 2. Sauvegarde des positions
            cursor.execute("DELETE FROM portfolio_positions WHERE user_id = ?", (user_id,))
            for ticker, pos in self.positions.items():
                cursor.execute("INSERT INTO portfolio_positions (user_id, asset, quantity, avg_price) VALUES (?, ?, ?, ?)",
                               (user_id, ticker, pos["quantity"], pos["avg_price"]))
                               
            # 3. Sauvegarde de l'historique des transactions
            cursor.execute("DELETE FROM portfolio_transactions WHERE user_id = ?", (user_id,))
            for trade in self.transactions:
                cursor.execute("""
                INSERT INTO portfolio_transactions (user_id, timestamp, type, asset, quantity, price, commission, total_net)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    trade["timestamp"],
                    trade["type"],
                    trade["ticker"],
                    trade["quantity"],
                    trade["price"],
                    trade["commission"],
                    trade["total_net"]
                ))
            conn.commit()
        finally:
            conn.close()

    def load_from_db(self, user_id: int = 1, db_path: str = None):
        """Charge l'état du portefeuille d'un utilisateur spécifique depuis SQL."""
        from data.database import get_portfolio_connection
        
        conn = get_portfolio_connection()
        try:
            cursor = conn.cursor()
            
            # 1. Chargement du cash
            cursor.execute("SELECT cash, initial_cash FROM portfolio_state WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                self.cash = row[0]
                self.initial_cash = row[1]
                
            # 2. Chargement des positions
            cursor.execute("SELECT asset, quantity, avg_price FROM portfolio_positions WHERE user_id = ?", (user_id,))
            self.positions = {}
            for row in cursor.fetchall():
                self.positions[row[0]] = {"quantity": int(row[1]), "avg_price": float(row[2])}
                
            # 3. Chargement des transactions
            cursor.execute("SELECT timestamp, type, asset, quantity, price, commission, total_net FROM portfolio_transactions WHERE user_id = ? ORDER BY id ASC", (user_id,))
            self.transactions = []
            for row in cursor.fetchall():
                self.transactions.append({
                    "timestamp": row[0],
                    "type": row[1],
                    "ticker": row[2],
                    "quantity": int(row[3]),
                    "price": float(row[4]),
                    "commission": float(row[5]),
                    "total_net": float(row[6])
                })
        except Exception as e:
            import warnings
            warnings.warn(f"Erreur chargement portefeuille depuis DB: {e}", RuntimeWarning)
        finally:
            conn.close()

    def save_to_file(self, filepath: str):
        if filepath.endswith(".db"):
            self.save_to_db(1, filepath)
        else:
            with open(filepath, "w") as f:
                json.dump(self.to_dict(), f, indent=4)

    def load_from_file(self, filepath: str):
        if filepath.endswith(".db"):
            self.load_from_db(1, filepath)
        elif os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                self.from_dict(data)
