"""
database.py — Gestion des bases de données PostgreSQL Cloud (Supabase)
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

import os
import psycopg2
import streamlit as st

def get_connection():
    """Retourne une connexion active à la base de données PostgreSQL Cloud via paramètres individuels."""
    # Récupération des secrets individuels
    pg_secrets = st.secrets.get("postgres", {})
    
    return psycopg2.connect(
        user=pg_secrets.get("DB_USER", "postgres"),
        password=pg_secrets.get("DB_PASSWORD", ""),
        host=pg_secrets.get("DB_HOST", ""),
        port=pg_secrets.get("DB_PORT", "5432"),
        database=pg_secrets.get("DB_NAME", "postgres"),
        connect_timeout=30
    )

def get_bronze_connection():
    """Retourne une connexion active pour la couche Bronze."""
    return get_connection()

def get_silver_connection():
    """Retourne une connexion active pour la couche Silver."""
    return get_connection()

def get_gold_connection():
    """Retourne une connexion active pour la couche Gold."""
    return get_connection()

def get_portfolio_connection():
    """Retourne une connexion active à la base de données de portefeuille."""
    return get_connection()

def get_connection_default():
    """Retourne une connexion active par défaut (Alias rétrocompatibilité)."""
    return get_portfolio_connection()

def init_db():
    """Initialise les tables de données directement dans le Cloud PostgreSQL."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Base de données Bronze (données brutes d'historique de prix)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bronze_prices (
        asset TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume BIGINT,
        PRIMARY KEY (asset, date)
    )
    """)
    
    # 2. Base de données Silver (données nettoyées et enrichies d'indicateurs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS silver_prices (
        asset TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume BIGINT,
        daily_return REAL,
        sma_20 REAL,
        sma_50 REAL,
        rsi_14 REAL,
        PRIMARY KEY (asset, date)
    )
    """)
    
    # 3. Base de données Gold (KPIs financiers agrégés)
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
    
    # 4. Table des utilisateurs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # 5. Table d'état du portefeuille liée à l'utilisateur
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_state (
        user_id INTEGER PRIMARY KEY,
        cash REAL NOT NULL,
        initial_cash REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # 6. Table des positions du portefeuille liée à l'utilisateur
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
    
    # 7. Table des transactions du portefeuille liée à l'utilisateur
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_transactions (
        id SERIAL PRIMARY KEY,
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
    cursor.close()
    conn.close()

# Initialisation automatique au chargement du module
try:
    init_db()
except Exception as e:
    print(f"Note lors de l'initialisation de la base PostgreSQL Cloud: {e}")