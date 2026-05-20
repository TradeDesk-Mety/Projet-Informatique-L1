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
    
    # Préparation des colonnes pour la base de données SQL
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
        # Nettoyer l'ancien historique pour éviter les doublons
        cursor.execute("DELETE FROM bronze_prices WHERE asset = ?", (asset_name,))
        # Insertion des données brutes
        df_db.to_sql("bronze_prices", conn, if_exists="append", index=False)
        conn.commit()
    finally:
        conn.close()
        
    return f"DB bronze: bronze_prices ({asset_name})"

def run_silver_layer(asset_name: str) -> str:
    """
    Couche Silver : Charge les données brutes SQL de la table 'bronze_prices',
    nettoie les valeurs manquantes, calcule les rendements journaliers,
    ajoute les indicateurs techniques (SMA, RSI) et les sauvegarde dans 'silver_prices'.
    """
    # Lecture depuis Bronze
    conn_bronze = db.get_bronze_connection()
    try:
        # Chargement depuis SQL dans un DataFrame
        df = pd.read_sql_query(
            "SELECT * FROM bronze_prices WHERE asset = ?", 
            conn_bronze, 
            params=(asset_name,), 
            index_col="date"
        )
    finally:
        conn_bronze.close()

    if df.empty:
        raise FileNotFoundError(f"Données Bronze introuvables en base pour {asset_name}. Lancez la couche Bronze.")
        
    df.index = pd.to_datetime(df.index)
    # Nettoyage des données
    df = df.dropna()
    df = df.sort_index() # Tri chronologique
    
    # Calcul des indicateurs techniques
    df["daily_return"] = df["close"].pct_change()
    df["sma_20"] = sim.calculate_sma(df["close"], 20)
    df["sma_50"] = sim.calculate_sma(df["close"], 50)
    df["rsi_14"] = sim.calculate_rsi(df["close"], 14)
    
    # Réinitialisation de l'index pour stockage SQL
    df.index = df.index.strftime("%Y-%m-%d %H:%M:%S")
    df.index.name = "date"
    df = df.reset_index()
    
    # Écriture dans Silver
    conn_silver = db.get_silver_connection()
    try:
        cursor = conn_silver.cursor()
        cursor.execute("DELETE FROM silver_prices WHERE asset = ?", (asset_name,))
        df.to_sql("silver_prices", conn_silver, if_exists="append", index=False)
        conn_silver.commit()
    finally:
        conn_silver.close()
        
    return f"DB silver: silver_prices ({asset_name})"

def run_gold_layer(asset_name: str, benchmark_name: str = "S&P 500 ETF (Tradable)") -> str:
    """
    Couche Gold : Calcule les indicateurs décisionnels (volatilité, ratio de Sharpe, bêta)
    et les agrège dans la table SQL 'gold_kpis'.
    """
    conn_silver = db.get_silver_connection()
    try:
        # Si le benchmark n'est pas prêt, on le prépare en arrière-plan
        try:
            run_bronze_layer(benchmark_name)
            run_silver_layer(benchmark_name)
        except Exception:
            pass
            
        # Charger les données nettoyées Silver de l'actif
        df_asset = pd.read_sql_query(
            "SELECT * FROM silver_prices WHERE asset = ?", 
            conn_silver, 
            params=(asset_name,), 
            index_col="date"
        )
        if df_asset.empty:
            raise FileNotFoundError(f"Données Silver introuvables en base pour {asset_name}.")
            
        df_asset.index = pd.to_datetime(df_asset.index)
        df_asset = df_asset.sort_index()
        
        # Charger les données du benchmark
        df_bench = pd.read_sql_query(
            "SELECT * FROM silver_prices WHERE asset = ?", 
            conn_silver, 
            params=(benchmark_name,), 
            index_col="date"
        )
    finally:
        conn_silver.close()
        
    # Calcul des KPIs de risque et rendement
    is_crypto = "USD" in data_loader.MARKET.get(asset_name, "")
    vol = grk.calculate_historical_volatility(df_asset["close"], is_crypto=is_crypto)
    sharpe = grk.calculate_sharpe_ratio(df_asset["close"], is_crypto=is_crypto)
    
    beta = 1.0
    if not df_bench.empty:
        df_bench.index = pd.to_datetime(df_bench.index)
        df_bench = df_bench.sort_index()
        beta = grk.calculate_beta(df_asset["close"], df_bench["close"])
    
    # Stockage consolidé dans Gold
    conn_gold = db.get_gold_connection()
    try:
        cursor = conn_gold.cursor()
        cursor.execute("DELETE FROM gold_kpis WHERE asset = ?", (asset_name,))
        cursor.execute("""
        INSERT INTO gold_kpis (asset, last_price, annualized_volatility, sharpe_ratio, beta_vs_market, data_points, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            asset_name,
            float(df_asset["close"].iloc[-1]),
            float(vol),
            float(sharpe),
            float(beta),
            int(len(df_asset)),
            pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn_gold.commit()
    finally:
        conn_gold.close()
        
    return f"DB gold: gold_kpis ({asset_name})"

def get_gold_kpis(asset_name: str) -> dict:
    """Récupère les KPI de la couche Gold depuis la base de données SQL."""
    conn = db.get_gold_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gold_kpis WHERE asset = ?", (asset_name,))
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

    benchmark = "S&P 500 ETF (Tradable)"
    
    # 1. S'assurer d'abord que le benchmark (S&P 500 ETF) est prêt
    try:
        run_bronze_layer(benchmark, period, interval)
        run_silver_layer(benchmark)
        run_gold_layer(benchmark, benchmark)
    except Exception as e:
        print(f"Alerte : Impossible de pré-charger le benchmark {benchmark} : {e}")

    # 2. Préparer les autres actifs
    assets_to_update = [asset for asset in data_loader.MARKET.keys() if asset != benchmark]
    
    db_lock = threading.Lock()
    results = {benchmark: True}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_update_single_asset_thread_safe, asset, period, interval, benchmark, db_lock): asset
            for asset in assets_to_update
        }
        for future in as_completed(futures):
            asset = futures[future]
            try:
                results[asset] = future.result()
            except Exception:
                results[asset] = False
                
    return results
