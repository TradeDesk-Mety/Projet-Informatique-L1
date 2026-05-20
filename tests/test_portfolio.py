import unittest
import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from equities.equities import Portfolio

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        # Création d'un portefeuille frais pour chaque test
        self.portfolio = Portfolio(initial_cash=10000.0)

    def test_initial_state(self):
        self.assertEqual(self.portfolio.cash, 10000.0)
        self.assertEqual(self.portfolio.initial_cash, 10000.0)
        self.assertEqual(len(self.portfolio.positions), 0)
        self.assertEqual(len(self.portfolio.transactions), 0)

    def test_buy_successful(self):
        # Achat de 10 actions à 100€
        # Coût net = 1000€ + 1% comm (10€) = 1010.0€
        msg = self.portfolio.buy("AAPL", 10, 100.0)
        self.assertIn("succès", msg.lower())
        self.assertEqual(self.portfolio.cash, 8990.0)
        self.assertIn("AAPL", self.portfolio.positions)
        self.assertEqual(self.portfolio.positions["AAPL"]["quantity"], 10)
        self.assertEqual(self.portfolio.positions["AAPL"]["avg_price"], 100.0)
        self.assertEqual(len(self.portfolio.transactions), 1)

    def test_buy_insufficient_funds(self):
        # Tentative d'acheter pour plus de 10 000€
        msg = self.portfolio.buy("AMZN", 100, 200.0) # coût ~20200€
        self.assertIn("insuffisants", msg.lower())
        self.assertEqual(self.portfolio.cash, 10000.0)
        self.assertNotIn("AMZN", self.portfolio.positions)

    def test_average_purchase_price(self):
        # Premier achat : 10 actions à 100€ (coût net 1010€)
        self.portfolio.buy("AAPL", 10, 100.0)
        # Second achat : 10 actions à 120€ (coût net 1212€)
        self.portfolio.buy("AAPL", 10, 120.0)
        
        # Total d'actions = 20
        # Prix moyen pondéré d'achat (PAMP) = (10*100 + 10*120)/20 = 110.0€
        self.assertEqual(self.portfolio.positions["AAPL"]["quantity"], 20)
        self.assertAlmostEqual(self.portfolio.positions["AAPL"]["avg_price"], 110.0)

    def test_sell_successful(self):
        # Acheter d'abord
        self.portfolio.buy("AAPL", 10, 100.0) # cash = 8990.0€
        
        # Vendre 5 actions à 150€
        # Brut = 750€, commission 1% = 7.5€, Net = 742.5€
        msg = self.portfolio.sell("AAPL", 5, 150.0)
        self.assertIn("succès", msg.lower())
        self.assertEqual(self.portfolio.cash, 8990.0 + 742.5)
        self.assertEqual(self.portfolio.positions["AAPL"]["quantity"], 5)

        # Vendre le reste
        self.portfolio.sell("AAPL", 5, 150.0)
        self.assertNotIn("AAPL", self.portfolio.positions)

    def test_sell_insufficient_holdings(self):
        self.portfolio.buy("AAPL", 5, 100.0)
        msg = self.portfolio.sell("AAPL", 10, 120.0) # Vendre plus que disponible
        self.assertIn("insuffisante", msg.lower())
        self.assertEqual(self.portfolio.positions["AAPL"]["quantity"], 5)

    def test_portfolio_valuation_and_performance(self):
        self.portfolio.buy("AAPL", 10, 100.0) # Cash restant = 8990€
        
        # Si le cours monte à 150€, valeur des actifs = 1500€
        # Valeur totale = 8990€ + 1500€ = 10490€
        current_prices = {"AAPL": 150.0}
        self.assertEqual(self.portfolio.get_portfolio_value(current_prices), 10490.0)
        
        # ROI % = ((10490 - 10000)/10000)*100 = 4.90%
        self.assertAlmostEqual(self.portfolio.get_total_performance(current_prices), 4.90)

    def test_save_and_load(self):
        self.portfolio.buy("AAPL", 5, 100.0)
        
        # Utilisation d'un fichier temporaire pour tester la persistance
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name
            
        try:
            self.portfolio.save_to_file(tmp_path)
            
            # Charger dans un nouveau portefeuille
            loaded_portfolio = Portfolio(initial_cash=10000.0)
            loaded_portfolio.load_from_file(tmp_path)
            
            self.assertEqual(loaded_portfolio.cash, self.portfolio.cash)
            self.assertEqual(loaded_portfolio.positions["AAPL"]["quantity"], 5)
            self.assertEqual(len(loaded_portfolio.transactions), 1)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == '__main__':
    unittest.main()
