import unittest
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import greeks.greeks as grk

class TestGreeksAndMath(unittest.TestCase):
    def test_black_scholes_pricing(self):
        # Paramètres standards : S=100, K=100, T=1, r=5%, sigma=20%
        # Valeur théorique connue approximative : Call ~ 10.45, Put ~ 5.57
        call_price = grk.black_scholes_pricing(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type="call")
        put_price = grk.black_scholes_pricing(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type="put")
        
        self.assertGreater(call_price, 10.0)
        self.assertLess(call_price, 11.0)
        self.assertGreater(put_price, 5.0)
        self.assertLess(put_price, 6.0)

        # Propriétés de base
        # Un Strike très élevé (K=200 pour S=100) rend le Call presque sans valeur
        otm_call = grk.black_scholes_pricing(S=100.0, K=200.0, T=0.5, r=0.02, sigma=0.20, option_type="call")
        self.assertLess(otm_call, 1.0)

    def test_calculate_greeks(self):
        S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
        
        greeks_call = grk.calculate_greeks(S, K, T, r, sigma, "call")
        greeks_put = grk.calculate_greeks(S, K, T, r, sigma, "put")

        # Delta Call doit être entre 0 et 1 (environ 0.63 ici)
        self.assertGreater(greeks_call["delta"], 0.0)
        self.assertLess(greeks_call["delta"], 1.0)
        
        # Delta Put doit être entre -1 et 0 (environ -0.37 ici)
        self.assertGreater(greeks_put["delta"], -1.0)
        self.assertLess(greeks_put["delta"], 0.0)

        # Gamma, Vega doivent être strictement positifs
        self.assertGreater(greeks_call["gamma"], 0.0)
        self.assertGreater(greeks_call["vega"], 0.0)
        self.assertEqual(greeks_call["gamma"], greeks_put["gamma"])
        self.assertEqual(greeks_call["vega"], greeks_put["vega"])

    def test_calculate_historical_volatility(self):
        # Cas prix constant -> Volatilité nulle
        prices_const = pd.Series([100.0, 100.0, 100.0, 100.0, 100.0])
        self.assertEqual(grk.calculate_historical_volatility(prices_const), 0.0)

        # Cas prix fluctuants
        prices = pd.Series([100.0, 102.0, 101.0, 103.0, 102.0])
        vol = grk.calculate_historical_volatility(prices)
        self.assertGreater(vol, 0.0)

    def test_calculate_beta(self):
        # Actif identique au marché -> Bêta = 1.0 (longueur 10 pour passer les seuils statistiques)
        prices = pd.Series([100.0, 101.0, 102.0, 101.0, 103.0, 104.0, 103.0, 105.0, 106.0, 107.0])
        beta = grk.calculate_beta(prices, prices)
        self.assertAlmostEqual(beta, 1.0)

        # Actif inversement corrélé au marché -> Bêta négatif
        market = pd.Series([100.0, 102.0, 100.0, 103.0, 102.0, 104.0, 102.0, 105.0, 104.0, 106.0])
        asset = pd.Series([100.0, 98.0, 100.0, 97.0, 98.0, 96.0, 98.0, 95.0, 96.0, 94.0])
        beta_neg = grk.calculate_beta(asset, market)
        self.assertLess(beta_neg, 0.0)

    def test_calculate_sharpe_ratio(self):
        # Prix constants -> Sharpe 0 (volatilité 0)
        prices_const = pd.Series([100.0] * 10)
        self.assertEqual(grk.calculate_sharpe_ratio(prices_const), 0.0)
        
        # Rendement positif
        prices = pd.Series([100.0, 101.0, 102.0, 103.0, 104.0, 105.0])
        self.assertIsNotNone(grk.calculate_sharpe_ratio(prices))

if __name__ == '__main__':
    unittest.main()
