import unittest
import os
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import data.medallion as med
import data.database as db


class TestMedallionPipeline(unittest.TestCase):
    def setUp(self):
        # Actif de test (doit correspondre à une clé de MARKET)
        self.asset = "Apple Inc."
        self.benchmark = "S&P 500 ETF (Tradable)"

    def test_medallion_pipeline_flow(self):
        """Test du pipeline complet Bronze → Silver → Gold avec les 4 bases séparées."""

        # 1. Test de la couche Bronze
        res_bronze = med.run_bronze_layer(self.asset, period="1mo", interval="1d")
        self.assertIn("bronze_prices", res_bronze)

        # Vérification dans bronze.db
        conn_bronze = db.get_bronze_connection()
        try:
            df_bronze = pd.read_sql_query(
                "SELECT * FROM bronze_prices WHERE asset = ?",
                conn_bronze,
                params=(self.asset,)
            )
            self.assertGreater(len(df_bronze), 5)
        finally:
            conn_bronze.close()

        # 2. Test de la couche Silver
        res_silver = med.run_silver_layer(self.asset)
        self.assertIn("silver_prices", res_silver)

        # Vérification dans silver.db
        conn_silver = db.get_silver_connection()
        try:
            df_silver = pd.read_sql_query(
                "SELECT * FROM silver_prices WHERE asset = ?",
                conn_silver,
                params=(self.asset,)
            )
            self.assertIn("daily_return", df_silver.columns)
            self.assertIn("sma_20", df_silver.columns)
            self.assertIn("rsi_14", df_silver.columns)
        finally:
            conn_silver.close()

        # 3. Test de la couche Gold
        res_gold = med.run_gold_layer(self.asset, self.benchmark)
        self.assertIn("gold_kpis", res_gold)

        # Vérification via get_gold_kpis (lit dans gold.db)
        kpis = med.get_gold_kpis(self.asset)
        self.assertEqual(kpis["asset"], self.asset)
        self.assertIn("annualized_volatility", kpis)
        self.assertIn("sharpe_ratio", kpis)
        self.assertIn("beta_vs_market", kpis)


if __name__ == '__main__':
    unittest.main()
