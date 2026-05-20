import sqlite3
import os
import pandas as pd

# Chemins vers les bases de données SQLite (architecture Medallion)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BRONZE_DB_PATH    = os.path.join(BASE_DIR, "data", "bronze",    "bronze.db")
SILVER_DB_PATH    = os.path.join(BASE_DIR, "data", "silver",    "silver.db")
GOLD_DB_PATH      = os.path.join(BASE_DIR, "data", "gold",      "gold.db")
PORTFOLIO_DB_PATH = os.path.join(BASE_DIR, "data", "portfolio", "portfolio.db")
DB_PATH = PORTFOLIO_DB_PATH  # alias rétrocompatibilité

def get_bronze_connection():
    """Retourne une connexion active à la base de données Bronze."""
    return sqlite3.connect(BRONZE_DB_PATH, timeout=30.0)

def get_silver_connection():
    """Retourne une connexion active à la base de données Silver."""
    return sqlite3.connect(SILVER_DB_PATH, timeout=30.0)

def get_gold_connection():
    """Retourne une connexion active à la base de données Gold."""
    return sqlite3.connect(GOLD_DB_PATH, timeout=30.0)

def get_portfolio_connection():
    """Retourne une connexion active à la base de données Portfolio."""
    return sqlite3.connect(PORTFOLIO_DB_PATH, timeout=30.0)

def get_connection():
    """Retourne une connexion active par défaut (Portefeuille)."""
    return get_portfolio_connection()

def init_db():
    """Initialise les bases de données et crée les tables correspondantes."""
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    
    # 1. Base de données Bronze (données brutes d'historique de prix)
    conn = get_bronze_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bronze_prices (
        asset TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        PRIMARY KEY (asset, date)
    )
    """)
    conn.commit()
    conn.close()
    
    # 2. Base de données Silver (données nettoyées et enrichies d'indicateurs)
    conn = get_silver_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS silver_prices (
        asset TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        daily_return REAL,
        sma_20 REAL,
        sma_50 REAL,
        rsi_14 REAL,
        PRIMARY KEY (asset, date)
    )
    """)
    conn.commit()
    conn.close()
    
    # 3. Base de données Gold (KPIs financiers agrégés)
    conn = get_gold_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gold_kpis (
        asset TEXT PRIMARY KEY,
        last_price REAL,
        annualized_volatility REAL,
        sharpe_ratio REAL,
        beta_vs_market REAL,
        data_points INTEGER,
        last_updated TEXT
    )
    """)
    conn.commit()
    conn.close()
    
    # 4. Base de données Portefeuille (Paper Trading)
    conn = get_portfolio_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_state (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        cash REAL,
        initial_cash REAL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_positions (
        asset TEXT PRIMARY KEY,
        quantity INTEGER,
        avg_price REAL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        type TEXT,
        asset TEXT,
        quantity INTEGER,
        price REAL,
        commission REAL,
        total_net REAL
    )
    """)
    
    conn.commit()
    conn.close()

# Initialisation automatique au chargement
init_db()
