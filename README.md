# 📈 TradeDesk — Simulateur de Place Boursière (Projet Informatique L1)

TradeDesk est une plateforme complète de **paper trading quantitatif**, d'analyse de marché en temps réel, de backtesting de stratégies algorithmiques et de pricing d'options.

Inspiré de l'architecture moderne de traitement de données et doté d'une interface premium au style Revolut, ce projet a été développé pour le cours d'Informatique L1 de l'Université Paris Nanterre.

---

## 🛠️ Terminal de Lancement Unique

TradeDesk intègre un **unique terminal de lancement interactif** qui regroupe toutes les fonctionnalités de contrôle.

### Comment l'utiliser ?

*   **Linux / macOS** :
    ```bash
    ./launch.sh
    ```
*   **Windows** :
    ```cmd
    Lancer_TradeDesk.bat
    ```

### Fonctionnalités du Terminal de Lancement :
1.  **Lancer le Site Web (Streamlit)** : Démarre l'application Streamlit.
2.  **Récupérer / Mettre à jour les données (yfinance SQL)** : Télécharge les données dans PostgreSQL (pipeline multi-threadé).
3.  **Installer les bibliothèques / Dépendances** : Initialise `.venv` et installe les dépendances.
4.  **Lancer la suite de tests unitaires** : Exécute les tests unitaires.

---

## 🏗️ Architecture & Pipeline de Données (Medallion SQL)

Le projet implémente un pipeline **médaillon (Bronze → Silver → Gold)** stocké dans PostgreSQL Cloud (Supabase) :

```
    yfinance API
         │
         ▼
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │  Bronze DB   │ ──► │  Silver DB   │ ──► │   Gold DB    │
 │   (Données   │     │ (Nettoyage & │     │   (KPIs :    │
 │   Brutes)    │     │  Indicateurs)│     │ Sharpe/Bêta) │
 └──────────────┘     └──────────────┘     └──────────────┘

                      + Portfolio DB : tables users, positions, transactions
```

### Couches de Stockage SQL (PostgreSQL Cloud)

| Table | Rôle / Contenu |
| :--- | :--- |
| `bronze_prices` | Données brutes OHLCV issues de `yfinance` |
| `silver_prices` | Rendements journaliers, SMA20, SMA50, RSI14 |
| `gold_kpis` | Indicateurs de performance (Sharpe, Bêta, Volatilité) |
| `users` | Comptes utilisateurs (`username`, `password_hash`, `email`, `created_at`) |
| `portfolio_state` | Liquidités et capital initial par utilisateur |
| `portfolio_positions` | Positions ouvertes (actif, quantité, prix moyen) |
| `portfolio_transactions` | Historique complet des ordres passés |

---

## 🔐 Sécurité — Authentification & Gestion des Mots de Passe

TradeDesk utilise un système d'authentification **sans dépendances externes**, basé sur la bibliothèque standard Python :

### Hachage PBKDF2-HMAC-SHA256

```
Mot de passe brut ──► PBKDF2(password, sel_16_octets, 100_000_iterations, SHA-256)
                  ──► Stockage : "sel_hex:hash_hex"
```

- ✅ **Sel unique** par utilisateur (16 octets aléatoires via `os.urandom`) → même mot de passe = hashes différents
- ✅ **100 000 itérations** → attaque par force brute rendue computationnellement très coûteuse
- ✅ **`hmac.compare_digest()`** → protection contre les timing attacks (temps de comparaison constant)
- ✅ **Aucun mot de passe en clair** ne transite ni n'est stocké

### Récupération de mot de passe oublié

La récupération automatique par e-mail nécessite un serveur SMTP. En l'absence de serveur configuré, la procédure manuelle est :

```bash
# Générer un nouveau hash pour un mot de passe de remplacement
python3 -c "from data.security import hash_password; print(hash_password('nouveau_mdp'))"
```

Puis en base PostgreSQL :
```sql
UPDATE users SET password_hash = '<hash_ci_dessus>' WHERE username = 'nom_utilisateur';
```

---

## 🚀 Démarrage Manuel Rapide

1. **Créer l'environnement virtuel et installer les packages** :
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configurer les secrets Supabase** (créer `.streamlit/secrets.toml`) :
   ```toml
   [postgres]
   DB_USER     = "postgres"
   DB_PASSWORD = "votre_mot_de_passe_supabase"
   DB_HOST     = "votre_host.supabase.co"
   DB_PORT     = "5432"
   DB_NAME     = "postgres"
   ```

3. **Remplir les bases de données (première utilisation)** :
   ```bash
   ./.venv/bin/python3 populate_db.py
   ```

4. **Lancer le serveur de développement Streamlit** :
   ```bash
   ./.venv/bin/streamlit run website/TradeDesk.py
   ```

5. **Lancer la suite de tests unitaires** :
   ```bash
   ./.venv/bin/python3 run_tests.py
   ```

---

## 📁 Structure du Projet

```
📁 Projet-Informatique-L1/
├── 📁 .streamlit/          → Configuration du thème sombre + secrets.toml (ignoré par Git)
├── 📁 bot/                 → Robot de trading (SMA / RSI / VWAP / Random Forest + Grid Search)
├── 📁 data/                → Pipeline Medallion, PostgreSQL, sécurité (PBKDF2)
│   ├── database.py         → Connexions psycopg2 + initialisation des tables
│   ├── security.py         → Hachage PBKDF2-HMAC-SHA256 + vérification hmac.compare_digest
│   ├── data.py             → Extraction yfinance + cache Streamlit
│   └── medallion.py        → Pipeline Bronze → Silver → Gold
├── 📁 equities/            → Gestion du portefeuille utilisateur (Achat/Vente, PAMP)
├── 📁 finance/             → Moteur C++ (engine.cpp) via ctypes : frais, ROI, Black-Scholes, Grid Search
├── 📁 greeks/              → Formules de Black-Scholes et Grecs (Delta, Gamma, Vega, Theta, Rho)
├── 📁 simulation/          → Backtesting SMA / RSI / VWAP + Monte-Carlo (GBM)
├── 📁 tests/               → Suite de tests unitaires
├── 📁 visualisation/       → Graphiques Plotly (Candlestick, VWAP RT, Bollinger, Heatmap, 3D...)
├── 📁 website/             → Application Streamlit
│   ├── TradeDesk.py        → Point d'entrée (authentification & page d'accueil)
│   └── 📁 pages/
│       ├── 1_Marché.py     → Cours temps réel, chandeliers, statistiques, corrélation
│       ├── 2_Portefeuille.py → Ordres, positions, options, historique
│       ├── 3_Backtesting.py → Simulation SMA / RSI / VWAP + comparatif
│       ├── 4_Bot.py        → Bot algorithmique (SMA/RSI/VWAP/ML avec Grid Search C++)
│       ├── 5_Options.py    → Pricing Black-Scholes + surface 3D
│       ├── 6_Documentation.py → Mode d'emploi + explication des graphiques + cours finance
│       └── 7_Paramètres.py → Gestion du compte (MDP, email, suppression)
├── requirements.txt        → Dépendances Python
├── populate_db.py          → Script d'alimentation des BDD
└── run_tests.py            → Exécuteur de la suite de tests
```

---

## 📊 Fonctionnalités Détaillées

### 1. Page Marché (`1_Marché.py`)
- **Temps Réel** : Données intraday 1 min, VWAP, jauge RSI (avec protection NaN), métriques journalières.
- **Historique** : Chandeliers japonais, Bandes de Bollinger (SMA20 ±2σ), SMA20/50, volume coloré, RSI(14).
- **Volatilité & Volume** : Volatilité glissante annualisée, détection des anomalies de volume (> 2× MM).
- **Statistiques** : Volatilité, Ratio de Sharpe, Bêta (vs S&P 500), Rendement 1 an, Skewness, Kurtosis.
- **Rendements** : Distribution empirique vs loi normale avec marqueurs μ et ±1σ.
- **Corrélation** : Heatmap Pearson entre plusieurs actifs (avec correction des fuseaux horaires).

### 2. Page Portefeuille (`2_Portefeuille.py`)
- Ordres achat/vente sur Actions/ETFs et Options européennes (Call/Put) pricées avec Black-Scholes.
- Suivi des positions ouvertes avec PnL latent coloré et ROI en temps réel.
- Graphique camembert de l'allocation du portefeuille.
- Export CSV de l'historique des transactions.

### 3. Page Backtesting (`3_Backtesting.py`)
- Stratégies : **SMA** (croisement), **RSI** (surachat/survente), **VWAP** (prix moyen pondéré).
- Mode **Comparatif** : SMA vs RSI vs VWAP sur la même période sur un seul graphique.
- Métriques : Rendement, Alpha vs Buy & Hold, Max Drawdown, Commissions payées.
- Graphique des signaux d'achat/vente avec la courbe VWAP superposée.

### 4. Page Bot de Trading (`4_Bot.py`)
- **4 stratégies** : SMA, RSI, VWAP, Machine Learning (Random Forest).
- Le mode **ML** utilise le **Grid Search C++** (`finance/engine.cpp`) pour trouver les fenêtres SMA et RSI optimales avant de construire les features du modèle.
- Calibration Platt Scaling + Cross-Validation 5-Folds pour éviter l'overfitting.
- Rapport narratif complet avant autorisation d'ordre.

### 5. Page Options 3D (`5_Options.py`)
- Pricing Call/Put avec Black-Scholes (moteur C++ + fallback Python).
- Surface 3D interactive Prix = f(Strike, Maturité).
- Grecs dynamiques (Δ, Γ, ν, Θ, Ρ).

### 6. Page Documentation (`6_Documentation.py`)
- Mode d'emploi complet avec tableau des sous-onglets.
- **Explication détaillée de chaque graphique** : Candlestick, VWAP RT, Distribution, Volatilité, Volume Breakout, Corrélation, Equity Curve/Drawdown, Surface 3D.
- Formules et tables d'interprétation pour SMA, RSI, VWAP, ML, Bollinger, Sharpe.
- Cours de finance accéléré (Actions, Risque, ETF, Options, Analyse technique/fondamentale).

### 7. Page Paramètres (`7_Paramètres.py`) — **Nouveau**
- **Modifier le mot de passe** (avec vérification de l'ancien).
- **Ajouter/modifier l'e-mail** (migration automatique de la colonne DB).
- **Procédure de mot de passe oublié** documentée.
- **Informations de sécurité** : architecture PBKDF2, structure des tables, secrets Streamlit.
- **Supprimer le compte** avec double confirmation (username + mot de passe + checkbox).

---

## 🔧 Moteur C++ (Grid Search & Black-Scholes)

Le module `finance/engine.cpp` est compilé automatiquement en bibliothèque partagée (`.so`/`.dll`) via `g++` ou `clang++`. Il expose via `ctypes` :

| Fonction C++ | Rôle |
|---|---|
| `grid_search_sma_cpp` | Teste toutes les combinaisons de fenêtres SMA pour trouver les plus rentables |
| `grid_search_rsi_cpp` | Optimise la fenêtre RSI et les seuils surachat/survente |
| `black_scholes_pricing_cpp` | Pricing d'options Call/Put (modèle de Black-Scholes 1973) |
| `total_brut`, `total_net_achat/vente` | Calcul des coûts de transaction avec commission 1% |

Un **fallback Python pur** prend le relais automatiquement si le compilateur C++ est absent.

---

## 🧪 Suite de Tests (100% de réussite ✅)

```
Finance (C++ / Python) : Calcul des commissions, ROI, total net    — 5 tests
Greeks & Math          : Black-Scholes, Sharpe, Volatilité          — 5 tests
Pipeline Medallion     : Flux Bronze → Silver → Gold                — 1 test
Gestion de Portefeuille: Passages d'ordres, PAMP, persistance SQLite — 8 tests
Simulation & Backtest  : Stratégies SMA, RSI, VWAP                  — 5 tests
```

Pour exécuter les tests :
```bash
./.venv/bin/python3 run_tests.py
```

---

*Projet informatique réalisé dans le cadre de la Licence L1 Économie-Gestion — Université Paris Nanterre.*
