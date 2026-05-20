# 📈 TradeDesk — Simulateur de Place Boursière (Projet Informatique L1)

TradeDesk est une plateforme complète de **paper trading quantitatif**, d'analyse de marché en temps réel, de backtesting de stratégies et de pricing d'options. 

Inspiré de l'architecture moderne de traitement de données et doté d'une interface premium au style Revolut, ce projet a été développé pour le cours d'Informatique L1 de l'Université Paris Nanterre.

---

## 🛠️ Terminal de Lancement Unique

TradeDesk intègre un **unique terminal de lancement interactif** qui regroupe toutes les fonctionnalités de contrôle. Il permet d'installer les bibliothèques, de récupérer les données de marché et de lancer le site web depuis un menu simple.

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
Une fois lancé, le terminal affiche un menu interactif :
1.  **Lancer le Site Web (Streamlit)** : Démarre l'application Streamlit.
2.  **Récupérer / Mettre à jour les données (yfinance SQL)** : Télécharge et met à jour l'ensemble des 1000 actifs dans la base de données SQLite (pipeline multi-threadé).
3.  **Installer les bibliothèques / Dépendances** : Initialise l'environnement virtuel `.venv` et installe automatiquement les dépendances du fichier `requirements.txt`.
4.  **Lancer la suite de tests unitaires** : Exécute les 24 tests unitaires pour valider le bon fonctionnement de l'application.


---

## 🏗️ Architecture & Pipeline de Données (Medallion SQL)

Le projet implémente un pipeline de données de type **médaillon (Bronze, Silver, Gold)** stocké sous 4 bases SQLite séparées, assurant une ségrégation propre des étapes de transformation :

```
    yfinance API
         │
         ▼
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │  Bronze DB   │ ──► │  Silver DB   │ ──► │   Gold DB    │
 │   (Données   │     │ (Nettoyage & │     │   (KPIs :    │
 │   Brutes)    │     │  Indicateurs)│     │ Sharpe/Bêta) │
 └──────────────┘     └──────────────┘     └──────────────┘
 data/bronze/         data/silver/         data/gold/
 bronze.db            silver.db            gold.db

                      + Portfolio DB : data/portfolio/portfolio.db
```

### Couches de Stockage SQL

| Couche | Base de Données | Rôle / Contenu | Méthode d'accès |
| :--- | :--- | :--- | :--- |
| **Bronze** | `data/bronze/bronze.db` | Données brutes OHLCV issues de `yfinance` | `get_bronze_connection()` |
| **Silver** | `data/silver/silver.db` | Rendements journaliers, SMA20, SMA50, RSI14 | `get_silver_connection()` |
| **Gold** | `data/gold/gold.db` | Indicateurs de performance (Sharpe, Bêta, Volatilité) | `get_gold_connection()` |
| **Portfolio**| `data/portfolio/portfolio.db`| Comptes utilisateurs, liquidités, transactions, positions | `get_portfolio_connection()` |

---

## 🚀 Démarrage Manuel Rapide (Alternative)

Si vous préférez ne pas utiliser les exécuteurs automatisés, vous pouvez effectuer les étapes manuellement :

1. **Créer l'environnement virtuel et installer les packages** :
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Remplir les bases de données (première utilisation)** :
   ```bash
   ./.venv/bin/python3 populate_db.py
   ```
   *Note : Le traitement de ~1000 actifs prend environ 2 à 5 minutes via l'exécuteur multi-threadé.*

3. **Lancer le serveur de développement Streamlit** :
   ```bash
   ./.venv/bin/streamlit run website/web.py
   ```

4. **Lancer la suite de tests unitaires** :
   ```bash
   ./.venv/bin/python3 run_tests.py
   ```

---

## 📁 Structure du Projet

```
📁 Projet-Informatique-L1/
├── 📁 .streamlit/          → Configuration du thème sombre Streamlit
├── 📁 bot/                 → Robot de trading automatisé (SMA / RSI / Random Forest)
├── 📁 data/                → Gestion des bases SQLite et pipeline Medallion multi-threadé
│   ├── bronze/             → Données brutes (bronze.db)
│   ├── silver/             → Indicateurs techniques (silver.db)
│   ├── gold/               → Indicateurs quantitatifs (gold.db)
│   └── portfolio/          → Portefeuilles et utilisateurs (portfolio.db)
├── 📁 equities/            → Gestion du portefeuille utilisateur (Achat/Vente, PAMP)
├── 📁 finance/             → Moteur de calcul financier (frais 1%, ROI, option de liaison C++)
├── 📁 greeks/              → Formules de Black-Scholes et calcul des Grecs (Delta, Gamma, Vega, Theta, Rho)
├── 📁 simulation/          → Moteur de simulation historique et backtesting (SMA/RSI)
├── 📁 tests/               → Ensemble des 24 tests unitaires
├── 📁 visualisation/       → Gestion de l'affichage des graphiques dynamiques (Plotly)
├── 📁 website/             → Pages Streamlit du site
│   ├── web.py              → Point d'entrée principal (authentification & routeur)
│   └── 📁 pages/           → Pages secondaires (Marché, Portefeuille, Backtesting, Bot, Options 3D)
├── requirements.txt        → Liste complète des dépendances Python
├── populate_db.py          → Script d'alimentation des BDD
└── run_tests.py            → Exécuteur de la suite de tests
```

---

## 📊 Fonctionnalités Détaillées

### 1. Page Marché (`1_📊_Marché.py`)
- **Temps Réel** : Données intraday à intervalle 1 minute, calcul du VWAP, jauge RSI en direct et suivi des métriques journalières.
- **Historique** : Graphique de chandeliers interactifs, bandes de Bollinger, moyennes mobiles (SMA20/50), volume et RSI.
- **Statistiques** : Mesure de la volatilité annualisée, calcul du Ratio de Sharpe, du Bêta de marché, de la Skewness et de la Kurtosis.
- **Rendements** : Analyse de la distribution des rendements quotidiens avec comparaison par rapport à une loi normale.
- **Corrélation** : Carte thermique de corrélation de Pearson entre plusieurs actifs sur une période de 1 an.

### 2. Page Portefeuille (`2_💼_Portefeuille.py`)
- Passage d'ordres d'achat/vente au marché avec simulation de frais de commission de 1%.
- Affichage en temps réel des positions ouvertes, du prix moyen pondéré (PAMP) et du PnL latent coloré.
- Graphique en camembert interactif montrant l'allocation des actifs.
- Exportation de l'historique complet des transactions en format CSV.

### 3. Page Backtesting (`3_🔬_Backtesting.py`)
- Testez la pertinence de vos stratégies sur l'historique de n'importe quel actif.
- Stratégies incluses : **Moyennes Mobiles (SMA)** (croisement) et **RSI** (zones de surachat/survente).
- Visualisation interactive du solde historique, comparaison avec la stratégie Buy & Hold et calcul du Drawdown maximum.

### 4. Page Options 3D (`5_📐_Options_3D.py`)
- Pricing d'options européennes (Call/Put) avec le modèle de Black-Scholes.
- Modélisation en 3D interactif du prix de l'option en fonction du sous-jacent et du temps restant (maturité).
- Visualisation de la courbe de volatilité (Volatility Smile).
- Calcul et tracé dynamique des Grecs ($\Delta$, $\Gamma$, $\nu$, $\Theta$) pour piloter le risque de l'option.

### 5. Page Robot de Trading (`4_🤖_Bot.py`)
- Laissez un automate prendre des décisions d'achat et de vente.
- Trois modes décisionnels disponibles : signaux de croisement SMA, niveaux de RSI, ou prévisions d'un classifieur Machine Learning Random Forest (`scikit-learn`).

---

## 🧪 Suite de Tests (100% de réussite ✅)

Le projet contient **24 tests unitaires** couvrant l'ensemble de la logique métier et garantissant la robustesse de l'application :

```
Finance (C++ / Python) : Calcul des commissions, ROI, total net   — 5 tests
Greeks & Math         : Modèle de Black-Scholes, Sharpe, Volatilité — 5 tests
Pipeline Medallion    : Flux de données Bronze -> Silver -> Gold    — 1 test
Gestion de Portefeuille: Passages d'ordres, PAMP, persistance SQLite — 8 tests
Simulation & Backtest : Stratégies de croisement SMA, RSI         — 5 tests
```

Pour exécuter les tests :
- Depuis le centre de contrôle : Option `[4]` de `launch.sh` ou `Lancer_TradeDesk.bat`.
- Directement en ligne de commande : `./.venv/bin/python3 run_tests.py`

---

*Projet informatique réalisé dans le cadre de la Licence L1 Économie-Gestion — Université Paris Nanterre.*
