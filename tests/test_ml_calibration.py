import unittest
import numpy as np
import pandas as pd
from finance import finance as fin
from simulation import simulation as sim

class TestMLGridSearch(unittest.TestCase):
    
    def setUp(self):
        # Générer un historique factice (tendance haussière légère + bruit)
        np.random.seed(42)
        prices = [100.0]
        for _ in range(99):
            # +0.1% de hausse moyenne par jour avec un bruit normal
            prices.append(prices[-1] * (1.0 + np.random.normal(0.001, 0.01)))
        self.prices_list = prices
        self.prices_series = pd.Series(prices)
        
    def test_grid_search_sma_cpp(self):
        """Vérifie que l'optmisation SMA trouve des paramètres valides (5<=S<=20 et 21<=L<=60)"""
        best_short, best_long, ret = fin.grid_search_sma(self.prices_list)
        self.assertTrue(5 <= best_short <= 20, "SMA courte hors limites")
        self.assertTrue(21 <= best_long <= 60, "SMA longue hors limites")
        self.assertIsInstance(ret, float, "Le retour doit être un flottant")
        
    def test_grid_search_rsi_cpp(self):
        """Vérifie que l'optimisation RSI trouve des paramètres valides"""
        best_w, best_os, best_ob, ret = fin.grid_search_rsi(self.prices_list)
        self.assertTrue(5 <= best_w <= 21, "Fenêtre RSI hors limites")
        self.assertTrue(20 <= best_os <= 40, "Seuil de survente hors limites")
        self.assertTrue(60 <= best_ob <= 80, "Seuil de surachat hors limites")
        self.assertIsInstance(ret, float, "Le retour doit être un flottant")

    def test_ml_features_creation(self):
        """Vérifie que la matrice de caractéristiques (Features) pour le ML se forme correctement"""
        close_ml = self.prices_series
        returns_1d = close_ml.pct_change()
        
        # Test avec des valeurs renvoyées par le Grid Search
        best_short = 5
        best_long = 21
        best_rsi_w = 14
        
        sma_short_opt = sim.calculate_sma(close_ml, best_short)
        sma_long_opt = sim.calculate_sma(close_ml, best_long)
        sma_ratio = sma_short_opt / sma_long_opt
        rsi_opt = sim.calculate_rsi(close_ml, best_rsi_w)
        vol_10 = returns_1d.rolling(10).std()
        
        features = pd.DataFrame({
            "sma_ratio": sma_ratio,
            "rsi": rsi_opt,
            "vol10": vol_10
        })
        
        # Vérification qu'après suppression des NaNs, le dataframe est valide
        features = features.dropna()
        self.assertGreater(len(features), 0, "Les features ne doivent pas être vides après dropna")
        self.assertEqual(len(features.columns), 3, "Il doit y avoir 3 colonnes")

if __name__ == '__main__':
    unittest.main()
