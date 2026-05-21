import os
import pandas as pd
import numpy as np
import data.data as data_loader
import data.database as db
import greeks.greeks as grk
import simulation.simulation as sim

def run_bronze_layer(asset_name: str, period: str = "1y", interval: str = "1d") -> str:
    """
    Couche Bronze : Récupère les données financières brutes de yfinance
    et les stocke dans la table 'bronze_prices' de la base de données SQL.
    """
    df_raw = data_loader.recuperer_historique(asset_name, period, interval, force_download=True)
    if df_raw.empty:
        raise ValueError(f"Aucune donnée récupérée pour {asset_name}")
    
    # Préparation des données
    df_db = df_raw.copy()
    df_db.index = df_db.index.strftime("%Y-%m-%d %H:%M:%S")
    df_db.index.name = "date"
    df_db = df_db.reset_index()
    df_db["asset"] = asset_name
    
    # Sélectionner et renommer uniquement les colonnes du schéma
    df_db = df_db[["asset", "date", "Open", "High", "Low", "Close", "Volume"]]
    df_db.columns = [c.lower() for c in df_db.columns]
    
    conn = db.get_bronze_connection()
    try:
        cursor = conn.cursor()
        # Nettoyer l'ancien historique (%s au lieu de ?)
        cursor.execute("DELETE FROM bronze_prices WHERE asset = %s", (asset_name,))
        
        # Insertion optimisée pour PostgreSQL (remplace to_sql qui pose problème)
        values = [tuple(x) for x in df_db.to_numpy()]
        insert_query = """
            INSERT INTO bronze_prices (asset, date, open, high, low, close, volume) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (asset, date) DO NOTHING
        """
        cursor.executemany(insert_query, values)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
        
    return f"DB bronze: bronze_prices ({asset_name})"

def run_silver_layer(asset_name: str) -> str:
    """
    Couche Silver : Charge les données brutes SQL de la table 'bronze_prices',
    nettoie les valeurs manquantes, calcule les rendements journaliers,
    ajoute les indicateurs techniques (SMA, RSI) et les sauvegarde dans 'silver_prices'.
    """
    conn_bronze = db.get_bronze_connection()
    try:
        # Chargement depuis PostgreSQL (%s au lieu de ?)
        df = pd.read_sql_query(
            "SELECT * FROM bronze_prices WHERE asset = %s", 
            conn_bronze, 
            params=(asset_name,), 
            index_col="date"
        )
    finally:
        conn_bronze.close()

    if df.empty:
        raise FileNotFoundError(f"Données Bronze introuvables en base pour {asset_name}. Lancez la couche Bronze.")
        
    df.index = pd.to_datetime(df.index)
    df = df.dropna()
    df = df.sort_index()
    
    # Calcul des indicateurs techniques
    df["daily_return"] = df["close"].pct_change()
    df["sma_20"] = sim.calculate_sma(df["close"], 20)
    df["sma_50"] = sim.calculate_sma(df["close"], 50)
    df["rsi_14"] = sim.calculate_rsi(df["close"], 14)
    
    # Gestion des valeurs NaN générées par les fenêtres glissantes (SMA/RSI)
    df = df.replace({np.nan: None})
    
    df.index = df.index.strftime("%Y-%m-%d %H:%M:%S")
    df.index.name = "date"
    df = df.reset_index()
    
    # Écriture dans Silver
    conn_silver = db.get_silver_connection()
    try:
        cursor = conn_silver.cursor()
        cursor.execute("DELETE FROM silver_prices WHERE asset = %s", (asset_name,))
        
        # Insertion optimisée pour PostgreSQL
        values = [tuple(x) for x in df.to_numpy()]
        insert_query = """
            INSERT INTO silver_prices (asset, date, open, high, low, close, volume, daily_return, sma_20, sma_50, rsi_14) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (asset, date) DO NOTHING
        """
        cursor.executemany(insert_query, values)
        conn_silver.commit()
    finally:
        cursor.close()
        conn_silver.close()
        
    return f"DB silver: silver_prices ({asset_name})"

def run_gold_layer(asset_name: str, benchmark_name: str = "S&P 500 ETF (Tradable)") -> str:
    """
    Couche Gold : Calcule les indicateurs décisionnels (volatilité, ratio de Sharpe, bêta)
    et les agrège dans la table SQL 'gold_kpis'.
    """
    conn_silver = db.get_silver_connection()
    try:
        try:
            run_bronze_layer(benchmark_name)
            run_silver_layer(benchmark_name)
        except Exception:
            pass
            
        # Charger l'actif (%s au lieu de ?)
        df_asset = pd.read_sql_query(
            "SELECT * FROM silver_prices WHERE asset = %s", 
            conn_silver, 
            params=(asset_name,), 
            index_col="date"
        )
        if df_asset.empty:
            raise FileNotFoundError(f"Données Silver introuvables en base pour {asset_name}.")
            
        df_asset.index = pd.to_datetime(df_asset.index)
        df_asset = df_asset.sort_index()
        
        # Charger le benchmark (%s au lieu de ?)
        df_bench = pd.read_sql_query(
            "SELECT * FROM silver_prices WHERE asset = %s", 
            conn_silver, 
            params=(benchmark_name,), 
            index_col="date"
        )
    finally:
        conn_silver.close()
        
    is_crypto = "USD" in data_loader.MARKET.get(asset_name, "")
    vol = grk.calculate_historical_volatility(df_asset["close"], is_crypto=is_crypto)
    sharpe = grk.calculate_sharpe_ratio(df_asset["close"], is_crypto=is_crypto)
    
    beta = 1.0
    if not df_bench.empty:
        df_bench.index = pd.to_datetime(df_bench.index)
        df_bench = df_bench.sort_index()
        beta = grk.calculate_beta(df_asset["close"], df_bench["close"])
    
    # Nettoyage des valeurs NaN/Inf avant conversion en float pour PostgreSQL
    vol = None if np.isnan(vol) or np.isinf(vol) else float(vol)
    sharpe = None if np.isnan(sharpe) or np.isinf(sharpe) else float(sharpe)
    beta = None if np.isnan(beta) or np.isinf(beta) else float(beta)
    
    # Stockage consolidé dans Gold
    conn_gold = db.get_gold_connection()
    try:
        cursor = conn_gold.cursor()
        cursor.execute("DELETE FROM gold_kpis WHERE asset = %s", (asset_name,))
        cursor.execute("""
        INSERT INTO gold_kpis (asset, last_price, annualized_volatility, sharpe_ratio, beta_vs_market, data_points, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            asset_name,
            float(df_asset["close"].iloc[-1]),
            vol,
            sharpe,
            beta,
            int(len(df_asset)),
            pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn_gold.commit()
    finally:
        cursor.close()
        conn_gold.close()
        
    return f"DB gold: gold_kpis ({asset_name})"

def get_gold_kpis(asset_name: str) -> dict:
    """Récupère les KPI de la couche Gold depuis la base de données SQL."""
    conn = db.get_gold_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gold_kpis WHERE asset = %s", (asset_name,))
        row = cursor.fetchone()
        if row:
            return {
                "asset": row[0],
                "last_price": row[1],
                "annualized_volatility": row[2],
                "sharpe_ratio": row[3],
                "beta_vs_market": row[4],
                "data_points": row[5],
                "last_updated": row[6]
            }
    finally:
        cursor.close()
        conn.close()
    return {}

def _update_single_asset_thread_safe(asset_name: str, period: str, interval: str, benchmark_name: str, lock: any) -> bool:
    """Met à jour un actif unique à travers les couches Medallion de manière thread-safe."""
    try:
        run_bronze_layer(asset_name, period, interval)
        run_silver_layer(asset_name)
        with lock:
            run_gold_layer(asset_name, benchmark_name)
        return True
    except Exception as e:
        import sys
        print(f"Erreur lors de la mise à jour de {asset_name} : {e}", file=sys.stderr)
        return False

def run_full_pipeline_multithreaded(period: str = "1y", interval: str = "1d", max_workers: int = 15) -> dict:
    """
    Exécute le pipeline Medallion complet pour tous les actifs de MARKET 
    de manière concurrente avec un ThreadPoolExecutor.
    """
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed

    benchmark = "S&P 500 ETF
