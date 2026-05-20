"""
database.py — Gestion des bases de données SQLite (Architecture Medallion)
========================================================================

Ce module gère le stockage persistant du simulateur boursier. Il implémente :
1. L'architecture de données Medallion (Bronze -> Silver -> Gold).
2. La base de données de portefeuille (Paper Trading) et de gestion des utilisateurs.

Relations avec les autres modules :
----------------------------------
- data.py & medallion.py : alimentent la table `bronze_prices` (Bronze), puis nettoient et
  calculent les indicateurs pour remplir `silver_prices` (Silver) et `gold_kpis` (Gold).
- equities.py : lit et écrit les positions et transactions du portefeuille dans `portfolio_positions`,
  `portfolio_transactions` et `portfolio_state`.
- web.py : gère la connexion/enregistrement des utilisateurs via la table `users`.
"""

import sqlite3
import os
import pandas as pd

# Chemins vers les bases de données SQLite
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BRONZE_DB_PATH    = os.path.join(BASE_DIR, "data", "bronze",    "bronze.db")
SILVER_DB_PATH    = os.path.join(BASE_DIR, "data", "silver",    "silver.db")
GOLD_DB_PATH      = os.path.join(BASE_DIR, "data", "gold",      "gold.db")
PORTFOLIO_DB_PATH = os.path.join(BASE_DIR, "data", "portfolio", "portfolio.db")
DB_PATH = PORTFOLIO_DB_PATH  # alias pour rétrocompatibilité

def get_bronze_connection():
    """Retourne une connexion active à la base de données Bronze (données brutes)."""
    return sqlite3.connect(BRONZE_DB_PATH, timeout=30.0)

def get_silver_connection():
    """Retourne une connexion active à la base de données Silver (données nettoyées)."""
    return sqlite3.connect(SILVER_DB_PATH, timeout=30.0)

def get_gold_connection():
    """Retourne une connexion active à la base de données Gold (KPIs calculés)."""
    return sqlite3.connect(GOLD_DB_PATH, timeout=30.0)

def get_portfolio_connection():
    """Retourne une connexion active à la base de données de portefeuille."""
    return sqlite3.connect(PORTFOLIO_DB_PATH, timeout=30.0)

def get_connection():
    """Retourne une connexion active par défaut (Portefeuille)."""
    return get_portfolio_connection()

def init_db():
    """Initialise les bases de données et crée les tables correspondantes."""
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "data", "bronze"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "data", "silver"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "data", "gold"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "data", "portfolio"), exist_ok=True)
    
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
    
    # 4. Base de données Portefeuille (Paper Trading + Utilisateurs)
    conn = get_portfolio_connection()
    cursor = conn.cursor()
    
    # Vérification et migration de l'ancienne base mono-utilisateur si nécessaire
    try:
        cursor.execute("PRAGMA table_info(portfolio_state)")
        columns = [row[1] for row in cursor.fetchall()]
        if len(columns) > 0 and "user_id" not in columns:
            cursor.execute("DROP TABLE IF EXISTS portfolio_state")
            cursor.execute("DROP TABLE IF EXISTS portfolio_positions")
            cursor.execute("DROP TABLE IF EXISTS portfolio_transactions")
    except Exception:
        pass

    # Table des utilisateurs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # Table d'état du portefeuille liée à l'utilisateur
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_state (
        user_id INTEGER PRIMARY KEY,
        cash REAL NOT NULL,
        initial_cash REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Table des positions du portefeuille liée à l'utilisateur
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_positions (
        user_id INTEGER NOT NULL,
        asset TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        avg_price REAL NOT NULL,
        PRIMARY KEY (user_id, asset),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Table des transactions du portefeuille liée à l'utilisateur
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        type TEXT NOT NULL,
        asset TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        commission REAL NOT NULL,
        total_net REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()

# Initialisation automatique au chargement du module
init_db()
