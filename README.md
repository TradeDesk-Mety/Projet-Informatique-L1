# 📈 Simulateur Place Boursière — Projet Informatique L1

Simulateur de **paper trading quantitatif** avec analyse de marché en temps réel, backtesting de stratégies et pricing d'options.

---

## 🏗️ Architecture

### Pipeline Medallion SQL
```
yfinance API
     │
     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Bronze DB  │ ──► │  Silver DB  │ ──► │   Gold DB   │
│  (données   │     │ (nettoyage  │     │   (KPIs :   │
│   brutes)   │     │  + SMA/RSI) │     │ Sharpe/Bêta)│
└─────────────┘     └─────────────┘     └─────────────┘
data/bronze/        data/silver/        data/gold/
bronze.db           silver.db           gold.db

                    + Portfolio DB : data/portfolio/portfolio.db
```

### Structure des fichiers
```
📁 Projet-Informatique-L1/
├── 📁 .streamlit/          → Config thème sombre
├── 📁 bot/                 → TradingBot (SMA / RSI)
├── 📁 data/
│   ├── data.py             → MARKET dict (1000 actifs) + cache SQL
│   ├── database.py         → Connexions SQLite par couche
│   ├── medallion.py        → Pipeline Bronze/Silver/Gold multi-threadé
│   ├── 📁 bronze/          → bronze.db (données brutes yfinance)
│   ├── 📁 silver/          → silver.db (SMA20, SMA50, RSI14, rendements)
│   ├── 📁 gold/            → gold.db   (Sharpe, Bêta, volatilité ann.)
│   └── 📁 portfolio/       → portfolio.db (paper trading)
├── 📁 equities/            → Portfolio (achat/vente, PAMP)
├── 📁 finance/             → Moteur C++ (commissions 1%, ROI)
├── 📁 greeks/              → Black-Scholes, Greeks (Δ, Γ, ν, Θ, ρ)
├── 📁 simulation/          → Backtesting SMA/RSI
├── 📁 tests/               → 24 tests unitaires
├── 📁 visualisation/       → Graphiques Plotly (7 types)
├── 📁 website/
│   ├── web.py              → Point d'entrée (login + session)
│   └── 📁 pages/
│       ├── 1_📊_Marché.py      → Temps réel + historique + corrélation
│       ├── 2_💼_Portefeuille.py → Ordres + positions + CSV
│       ├── 3_🔬_Backtesting.py → Stratégies historiques
│       ├── 4_🤖_Bot.py         → Trading automatique
│       └── 5_📐_Options_3D.py  → Black-Scholes 3D + Greeks
├── populate_db.py          → Remplit les 4 BDD (1000 actifs, 20 threads)
└── run_tests.py            → Suite de tests
```

---

## 🚀 Démarrage rapide

### 1. Installer les dépendances
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit yfinance pandas numpy scipy plotly pytickersymbols
```

### 2. Remplir la base de données (1ère utilisation)
```bash
./.venv/bin/python3 populate_db.py
```
> ⚠️ ~1000 actifs, prévoir 2–5 minutes. Utilise 20 threads en parallèle.

### 3. Lancer le site
```bash
./.venv/bin/streamlit run website/web.py
```

### 4. Lancer les tests
```bash
./.venv/bin/python3 run_tests.py
```

---

## 📊 Fonctionnalités

### Page Marché (`1_📊_Marché.py`)
| Onglet | Contenu |
|--------|---------|
| ⚡ **Temps Réel** | Cours intraday 1 min, VWAP, jauge RSI, métriques J |
| 📈 **Historique** | Chandeliers + Bollinger Bands + SMA20/50 + Volume + RSI |
| 📐 **Statistiques** | Volatilité ann., Sharpe, Bêta, Skewness, Kurtosis |
| 📉 **Rendements** | Distribution + courbe normale théorique |
| 🔗 **Corrélation** | Heatmap multi-actifs sur 1 an |

### Page Portefeuille (`2_💼_Portefeuille.py`)
- Passer des ordres Achat/Vente avec calcul de commission (moteur C++)
- Tableau des positions coloré (vert/rouge selon PnL)
- Pie chart de répartition du portefeuille
- Export CSV de l'historique des transactions

### Page Backtesting (`3_🔬_Backtesting.py`)
- Stratégies : **SMA** (croisement de moyennes mobiles) et **RSI** (force relative)
- Métriques : rendement, alpha vs Buy&Hold, drawdown maximum, commissions
- Graphique de performance avec courbe de drawdown
- Signaux Achat/Vente affichés sur le cours

### Page Options 3D (`5_📐_Options_3D.py`)
- Surface 3D Black-Scholes : prix = f(Strike K, Maturité T)
- Volatility Smile : prix vs Strike pour σ ∈ {15%, 20%, 25%, 35%, 50%}
- Sensibilité des Greeks (Δ, Γ, ν, Θ) en fonction du prix S

---

## 🔧 Architecture Medallion SQL

| Couche | Base | Contenu | Connexion |
|--------|------|---------|-----------|
| **Bronze** | `bronze/bronze.db` | OHLCV brut yfinance | `get_bronze_connection()` |
| **Silver** | `silver/silver.db` | + daily_return, SMA20, SMA50, RSI14 | `get_silver_connection()` |
| **Gold** | `gold/gold.db` | Sharpe, Bêta, Volatilité, last_price | `get_gold_connection()` |
| **Portfolio** | `portfolio/portfolio.db` | Cash, positions, transactions | `get_portfolio_connection()` |

**Multi-threading** : `ThreadPoolExecutor` avec 20 workers pour traiter 1000 actifs en parallèle.

---

## 💹 Univers de marché (1000 actifs)

| Région | Indices | Tickers |
|--------|---------|---------|
| 🇺🇸 USA | S&P 500, NASDAQ 100, DOW JONES | ~500 |
| 🇪🇺 Europe | CAC 40, DAX, FTSE 100, AEX, IBEX 35, Swiss 20, OMX... | ~498 |
| + | Indices, ETFs, Cryptos | 18 |

---

## 🧪 Tests (24 tests, 100% ✅)

```
Finance (C++)    : commission, ROI, total net       — 5 tests
Greeks           : Black-Scholes, Greeks, Sharpe     — 5 tests
Medallion SQL    : pipeline Bronze→Silver→Gold       — 1 test
Portfolio        : achat/vente, PAMP, sauvegarde     — 8 tests
Simulation       : SMA, RSI, backtest                — 5 tests
```

---

*Projet réalisé dans le cadre du cours Informatique L1 — Université Paris Nanterre*
