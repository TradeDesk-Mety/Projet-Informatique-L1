import unittest
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simulation.simulation as sim

class TestSimulationAndBacktesting(unittest.TestCase):
    def setUp(self):
        # Création d'une série temporelle de prix factice de 100 jours
        np.random.seed(42)
        dates = pd.date_range(start="2026-01-01", periods=100)
        # Marche aléatoire simple
        price_changes = np.random.normal(0.001, 0.02, 100)
        prices = 100.0 * np.cumprod(1 + price_changes)
        self.prices = pd.Series(prices, index=dates)

    def test_calculate_sma(self):
        sma_10 = sim.calculate_sma(self.prices, 10)
        self.assertEqual(len(sma_10), 100)
        # Les 9 premiers éléments d'une SMA 10 doivent être NaN
        self.assertTrue(pd.isna(sma_10.iloc[0]))
        self.assertTrue(pd.isna(sma_10.iloc[8]))
        self.assertFalse(pd.isna(sma_10.iloc[9]))
        
        # Test valeur exacte
        expected_avg = self.prices.iloc[0:10].mean()
        self.assertAlmostEqual(sma_10.iloc[9], expected_avg)

    def test_calculate_rsi(self):
        rsi_14 = sim.calculate_rsi(self.prices, 14)
        self.assertEqual(len(rsi_14), 100)
        
        # Les valeurs du RSI doivent être comprises strictement entre 0 et 100
        valid_rsi = rsi_14.dropna()
        self.assertTrue((valid_rsi >= 0).all())
        self.assertTrue((valid_rsi <= 100).all())

    def test_backtest_strategy_sma(self):
        res = sim.backtest_strategy(self.prices, strategy_type="SMA", params={"short_window": 10, "long_window": 30})
        
        # Validation des clés retournées
        self.assertIn("portfolio_history", res)
        self.assertIn("final_value", res)
        self.assertIn("strategy_return", res)
        self.assertIn("benchmark_return", res)
        self.assertIn("max_drawdown", res)
        self.assertIn("trades_count", res)
        
        # Le capital final doit être un nombre positif
        self.assertGreater(res["final_value"], 0.0)

    def test_backtest_strategy_rsi(self):
        res = sim.backtest_strategy(self.prices, strategy_type="RSI", params={"rsi_window": 10, "oversold": 30, "overbought": 70})
        self.assertGreater(res["final_value"], 0.0)
        self.assertIn("max_drawdown", res)

    def test_backtest_insufficient_data(self):
        # Moins de 20 points
        short_prices = self.prices.iloc[0:10]
        res = sim.backtest_strategy(short_prices, strategy_type="SMA")
        self.assertIn("error", res)

if __name__ == '__main__':
    unittest.main()
