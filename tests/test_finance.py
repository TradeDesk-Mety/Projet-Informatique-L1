import unittest
import os
import sys

# Ajout du chemin du projet pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import finance.finance as fin

class TestFinanceEngine(unittest.TestCase):
    def test_total_brut(self):
        # Test calcul brut standard
        self.assertAlmostEqual(fin.total_brut(10, 150.0), 1500.0)
        self.assertAlmostEqual(fin.total_brut(1, 45.5), 45.5)
        
        # Test cas d'erreurs (doit lever ValueError)
        with self.assertRaises(ValueError):
            fin.total_brut(-5, 100.0)
        with self.assertRaises(ValueError):
            fin.total_brut(10, -50.0)

    def test_calculer_commission(self):
        # Commission de 1%
        self.assertAlmostEqual(fin.calculer_commission(100.0, 10), 10.0) # 100 * 10 * 0.01 = 10
        self.assertAlmostEqual(fin.calculer_commission(50.0, 1), 0.5)    # 50 * 1 * 0.01 = 0.5

        # Test cas d'erreurs
        with self.assertRaises(ValueError):
            fin.calculer_commission(-100.0, 10)

    def test_total_net_achat(self):
        # Net achat = brut + commission = 10 * 150 + 15 = 1515.0
        self.assertAlmostEqual(fin.total_net_achat(10, 150.0), 1515.0)

    def test_total_net_vente(self):
        # Net vente = brut - commission = 10 * 150 - 15 = 1485.0
        self.assertAlmostEqual(fin.total_net_vente(10, 150.0), 1485.0)

    def test_calculer_performance(self):
        # ROI % = ((120 - 100) / 100) * 100 = 20.0 %
        self.assertAlmostEqual(fin.calculer_performance(100.0, 120.0), 20.0)
        # Performance négative
        self.assertAlmostEqual(fin.calculer_performance(100.0, 80.0), -20.0)

        # Test division par zéro / prix achat invalide
        with self.assertRaises(ValueError):
            fin.calculer_performance(0.0, 100.0)

if __name__ == '__main__':
    unittest.main()
