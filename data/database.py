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
    # Récupération des secrets individuels depuis Streamlit Cloud
    pg_secrets = st.secrets.get("postgres", {})
    
    # Sécurité au cas où les secrets seraient vides
    if not pg_secrets:
        raise ValueError("❌ Les secrets [postgres] sont introuvables ou vides dans Streamlit Cloud.")
        
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
    
    # 5. Table des portefeuilles (support multi-portefeuilles par utilisateur)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolios (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        initial_cash REAL NOT NULL DEFAULT 10000.0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 6. Table d'état du portefeuille liée à l'utilisateur ET au portefeuille
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_state (
        user_id INTEGER NOT NULL,
        portfolio_id INTEGER NOT NULL DEFAULT 1,
        cash REAL NOT NULL,
        initial_cash REAL NOT NULL,
        PRIMARY KEY (user_id, portfolio_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 7. Table des positions du portefeuille liée à l'utilisateur ET au portefeuille
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_positions (
        user_id INTEGER NOT NULL,
        portfolio_id INTEGER NOT NULL DEFAULT 1,
        asset TEXT NOT NULL,
        quantity REAL NOT NULL,
        avg_price REAL NOT NULL,
        PRIMARY KEY (user_id, portfolio_id, asset),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 8. Table des transactions du portefeuille liée à l'utilisateur ET au portefeuille
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_transactions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        portfolio_id INTEGER NOT NULL DEFAULT 1,
        timestamp TEXT NOT NULL,
        type TEXT NOT NULL,
        asset TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        commission REAL NOT NULL,
        total_net REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # ── Migration 1 : ajout colonne portfolio_id si absente ─────────────────
    for table, col_def in [
        ("portfolio_state",        "portfolio_id INTEGER NOT NULL DEFAULT 1"),
        ("portfolio_positions",    "portfolio_id INTEGER NOT NULL DEFAULT 1"),
        ("portfolio_transactions", "portfolio_id INTEGER NOT NULL DEFAULT 1"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col_def}")
            conn.commit()
        except Exception:
            conn.rollback()

    # ── Migration 2 : corriger la PRIMARY KEY de portfolio_state ────────────
    # Ancienne PK : user_id seul → ne supporte qu'un portefeuille par user
    # Nouvelle PK : (user_id, portfolio_id) → multi-portefeuilles
    try:
        cursor.execute("""
            DO $$
            BEGIN
                -- Vérifie si portfolio_id est absent de la PK actuelle
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.key_column_usage
                    WHERE table_name = 'portfolio_state'
                      AND constraint_name = (
                          SELECT constraint_name FROM information_schema.table_constraints
                          WHERE table_name = 'portfolio_state' AND constraint_type = 'PRIMARY KEY'
                          LIMIT 1
                      )
                      AND column_name = 'portfolio_id'
                ) THEN
                    ALTER TABLE portfolio_state DROP CONSTRAINT IF EXISTS portfolio_state_pkey;
                    ALTER TABLE portfolio_state ADD PRIMARY KEY (user_id, portfolio_id);
                END IF;
            END $$;
        """)
        conn.commit()
    except Exception:
        conn.rollback()

    # ── Migration 3 : corriger la PRIMARY KEY de portfolio_positions ─────────
    try:
        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.key_column_usage
                    WHERE table_name = 'portfolio_positions'
                      AND constraint_name = (
                          SELECT constraint_name FROM information_schema.table_constraints
                          WHERE table_name = 'portfolio_positions' AND constraint_type = 'PRIMARY KEY'
                          LIMIT 1
                      )
                      AND column_name = 'portfolio_id'
                ) THEN
                    ALTER TABLE portfolio_positions DROP CONSTRAINT IF EXISTS portfolio_positions_pkey;
                    ALTER TABLE portfolio_positions ADD PRIMARY KEY (user_id, portfolio_id, asset);
                END IF;
            END $$;
        """)
        conn.commit()
    except Exception:
        conn.rollback()

    # ── Migration 4 : modifier la colonne quantity en REAL ─────────────────
    try:
        cursor.execute("ALTER TABLE portfolio_positions ALTER COLUMN quantity TYPE REAL")
        cursor.execute("ALTER TABLE portfolio_transactions ALTER COLUMN quantity TYPE REAL")
        conn.commit()
    except Exception:
        conn.rollback()

    conn.commit()
    cursor.close()
    conn.close()


def create_portfolio(user_id: int, name: str, initial_cash: float = 10000.0) -> int:
    """Crée un nouveau portefeuille pour un utilisateur et retourne son id."""
    from datetime import datetime
    conn = get_portfolio_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO portfolios (user_id, name, initial_cash, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
            (user_id, name, initial_cash, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def get_portfolios(user_id: int) -> list:
    """Retourne la liste des portefeuilles d'un utilisateur [(id, name, initial_cash, created_at)]."""
    conn = get_portfolio_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, initial_cash, created_at FROM portfolios WHERE user_id = %s ORDER BY id",
            (user_id,)
        )
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        conn.close()


def rename_portfolio(portfolio_id: int, user_id: int, new_name: str) -> bool:
    """Renomme un portefeuille. Retourne True si succès."""
    conn = get_portfolio_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE portfolios SET name = %s WHERE id = %s AND user_id = %s",
            (new_name, portfolio_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()


def delete_portfolio(portfolio_id: int, user_id: int) -> bool:
    """Supprime un portefeuille et toutes ses données. Retourne True si succès."""
    conn = get_portfolio_connection()
    try:
        cursor = conn.cursor()
        for table in ("portfolio_state", "portfolio_positions", "portfolio_transactions"):
            cursor.execute(
                f"DELETE FROM {table} WHERE user_id = %s AND portfolio_id = %s",
                (user_id, portfolio_id)
            )
        cursor.execute(
            "DELETE FROM portfolios WHERE id = %s AND user_id = %s",
            (portfolio_id, user_id)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

# Initialisation automatique au chargement du module
try:
    init_db()
except Exception as e:
    print(f"Note lors de l'initialisation de la base PostgreSQL Cloud: {e}")    
