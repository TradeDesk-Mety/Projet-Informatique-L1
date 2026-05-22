# 📈 TradeDesk — Simulateur de Place Boursière

TradeDesk est une plateforme complète de **paper trading quantitatif**, d'analyse de marché en temps réel, de backtesting de stratégies algorithmiques et de pricing d'options européennes.

Inspiré de l'architecture moderne de traitement de données (pipeline Medallion) et doté d'une interface premium au style fintech, ce projet a été développé pour le cours d'Informatique L1 de l'Université Paris Nanterre.

**Technologies** : Python · Streamlit · PostgreSQL (Supabase Cloud) · C++ (ctypes) · Plotly · scikit-learn · yfinance

---

## 📁 Structure Détaillée du Projet

```
📁 Projet-Informatique-L1/
│
├── 📁 .devcontainer/           → Configuration GitHub Codespaces
├── 📁 .streamlit/              → Configuration Streamlit (thème sombre + secrets)
├── 📁 bot/                     → Robot de trading algorithmique
├── 📁 data/                    → Pipeline de données Medallion + sécurité
├── 📁 equities/                → Gestion du portefeuille utilisateur
├── 📁 finance/                 → Moteur de calcul C++ + wrapper Python
├── 📁 greeks/                  → Formules Black-Scholes et Greeks
├── 📁 simulation/              → Backtesting et Monte-Carlo
├── 📁 tests/                   → Suite de tests unitaires
├── 📁 visualisation/           → Graphiques interactifs Plotly
├── 📁 website/                 → Application web Streamlit (pages + composants)
│
├── launch.sh                   → Script de lancement Linux / macOS
├── Lancer_TradeDesk.bat        → Script de lancement Windows
├── populate_db.py              → Alimentation des bases de données
├── run_tests.py                → Exécuteur de la suite de tests
├── run_grid_search.py          → Optimisation Grid Search en ligne de commande
├── requirements.txt            → Dépendances Python
└── .gitignore                  → Fichiers exclus du dépôt Git
```

---

### 📁 `.devcontainer/`

Configuration pour exécuter le projet dans **GitHub Codespaces** ou un Dev Container VS Code.

| Fichier | Description |
|---|---|
| `devcontainer.json` | Image Python 3.11, installation automatique des dépendances, lancement de Streamlit au démarrage, port 8501 exposé. |

---

### 📁 `.streamlit/`

Configuration globale de l'application Streamlit.

| Fichier | Description |
|---|---|
| `config.toml` | Thème sombre personnalisé (couleurs, police sans-serif), mode headless activé, collecte de statistiques désactivée. |
| `secrets.toml` *(ignoré par Git)* | Identifiants de connexion PostgreSQL Cloud (Supabase) : `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`. |

---

### 📁 `bot/`

Moteur du robot de trading automatique.

| Fichier | Description |
|---|---|
| `bot.py` | Classe `TradingBot` avec **4 stratégies** : **SMA** (croisement de moyennes mobiles), **RSI** (surachat/survente), **VWAP** (prix moyen pondéré par volume) et **ML_RF** (Random Forest avec Grid Search C++ pour SMA/RSI + Grid Search Python pour VWAP, calibration Platt Scaling, cross-validation 5-Folds). Génère des signaux d'achat/vente et exécute les ordres sur le portefeuille. |

---

### 📁 `data/`

Pipeline de données et couche de persistance.

| Fichier | Description |
|---|---|
| `database.py` | Connexions PostgreSQL Cloud (Supabase) via `psycopg2`. Initialise 8 tables SQL (`bronze_prices`, `silver_prices`, `gold_kpis`, `users`, `portfolios`, `portfolio_state`, `portfolio_positions`, `portfolio_transactions`). Gère les migrations automatiques et le CRUD des portefeuilles. |
| `data.py` | Dictionnaire `MARKET` de **+1 000 actifs** (500 US + 500 européens + cryptos + indices). Fonctions de récupération d'historique via `yfinance` avec cache Streamlit. Conversion EUR/USD en temps réel. |
| `medallion.py` | Pipeline **Medallion** (Bronze → Silver → Gold) : `run_bronze_layer()` ingère les données brutes, `run_silver_layer()` calcule les indicateurs techniques (SMA, RSI, rendements), `run_gold_layer()` agrège les KPIs (Sharpe, Bêta, volatilité). Exécution multi-threadée (`ThreadPoolExecutor`). |
| `security.py` | Hachage de mots de passe **PBKDF2-HMAC-SHA256** (100 000 itérations, sel 16 octets). Vérification en temps constant avec `hmac.compare_digest()` contre les timing attacks. Aucune dépendance externe. |

**Sous-dossiers de données** (fichiers `.db` ignorés par Git) :

| Dossier | Contenu |
|---|---|
| `bronze/` | `bronze.db` — Données OHLCV brutes issues de yfinance. |
| `silver/` | `silver.db` — Données nettoyées + indicateurs techniques (SMA20, SMA50, RSI14, rendements). |
| `gold/` | `gold.db` — KPIs agrégés par actif (volatilité, Sharpe, Bêta vs S&P 500). |
| `portfolio/` | `portfolio.db` — Comptes utilisateurs, portefeuilles, positions et transactions. |

---

### 📁 `equities/`

Gestion du portefeuille de paper trading.

| Fichier | Description |
|---|---|
| `equities.py` | Classe `Portfolio` : achat/vente avec calcul du prix d'achat moyen pondéré (PAMP), commission de 1 % via le moteur C++, calcul du ROI et de la valeur totale. Persistance en base PostgreSQL (`save_to_db` / `load_from_db`). Support multi-portefeuilles par utilisateur. |

---

### 📁 `finance/`

Moteur de calcul haute performance C++ + interface Python.

| Fichier | Description |
|---|---|
| `engine.cpp` | Code source C++ compilé en bibliothèque dynamique (`.so` / `.dll` / `.dylib`). Expose via `extern "C"` : `total_brut`, `calculer_commission`, `total_net_achat`, `total_net_vente`, `calculer_performance`, `black_scholes_pricing_cpp`, `grid_search_sma_cpp`, `grid_search_rsi_cpp`. |
| `engine.so` | Binaire compilé (Linux). Recompilé automatiquement par `finance.py` si absent ou obsolète. |
| `finance.py` | Wrapper Python via `ctypes` : détection OS, compilation automatique (`g++` / `clang++`), déclaration des signatures, **fallback Python pur** si le compilateur est absent. Fonctions exposées : calculs financiers, pricing Black-Scholes, Grid Search SMA/RSI. |

---

### 📁 `greeks/`

Formules mathématiques financières.

| Fichier | Description |
|---|---|
| `greeks.py` | Pricing **Black-Scholes** (Call/Put) avec `scipy.stats.norm`. Calcul des 5 **Greeks** : Delta (Δ), Gamma (Γ), Vega (ν), Theta (Θ), Rho (ρ). Volatilité historique annualisée (252j actions / 365j cryptos). Ratio de Sharpe. Bêta vs benchmark (avec correction des timezones). |

---

### 📁 `simulation/`

Moteur de backtesting et simulation stochastique.

| Fichier | Description |
|---|---|
| `simulation.py` | Calcul de la **SMA** et du **RSI**. Fonction `backtest_strategy()` simulant 3 stratégies (SMA, RSI, VWAP) avec capital initial de 10 000 €, commission 1 %, et métriques complètes (rendement, Alpha vs Buy & Hold, Max Drawdown, nombre d'ordres). Simulation **Monte-Carlo** (GBM) pour projections stochastiques de prix. |

---

### 📁 `tests/`

Suite de tests unitaires.

| Fichier | Description |
|---|---|
| `__init__.py` | Package Python pour la découverte automatique des tests. |
| `test_finance.py` | Tests du moteur C++ / fallback Python : commissions, ROI, total net (5 tests). |
| `test_greeks.py` | Tests de Black-Scholes, Sharpe, volatilité historique (5 tests). |
| `test_medallion.py` | Test du flux Bronze → Silver → Gold (1 test). |
| `test_ml_calibration.py` | Tests de la calibration du modèle ML (Random Forest + Platt Scaling). |
| `test_portfolio.py` | Tests de la gestion de portefeuille : ordres, PAMP, persistance SQL (8 tests). |
| `test_simulation.py` | Tests des stratégies de backtesting SMA, RSI, VWAP (5 tests). |

---

### 📁 `visualisation/`

Bibliothèque de graphiques interactifs.

| Fichier | Description |
|---|---|
| `visualisation.py` | 10 fonctions de tracé **Plotly** avec thème sombre unifié : chandeliers japonais (+ SMA + Bollinger + RSI + volumes colorés), cours temps réel avec VWAP, heatmap de corrélation (avec correction des timezones), distribution des rendements vs loi normale, scatter risque/rendement, courbe de performance + drawdown, surface 3D Black-Scholes, jauge RSI animée, volatilité glissante annualisée, détection d'anomalies de volume (> 2× moyenne mobile). |

---

### 📁 `website/`

Application web Streamlit.

| Fichier | Description |
|---|---|
| `TradeDesk.py` | **Point d'entrée principal**. Authentification sécurisée (connexion / inscription avec choix du capital initial). Page d'accueil avec onboarding interactif. Sidebar de navigation avec identité utilisateur et déconnexion. |
| `update_ui.py` | Script utilitaire d'injection du thème global (`set_global_ui`) dans toutes les pages. |

#### 📁 `website/assets/`

| Fichier | Description |
|---|---|
| `logo.png` | Logo de la plateforme TradeDesk affiché dans la sidebar. |

#### 📁 `website/components/`

| Fichier | Description |
|---|---|
| `ui_config.py` | CSS global injecté dans chaque page : police Inter (Google Fonts), thème Navy/Cyan, glassmorphism, boutons gradient, sidebar responsive (mobile plein écran), footer avec liens vers les pages légales. |
| `assistant_sidebar.py` | Moteur de l'assistant conversationnel : base de connaissances de **40+ concepts** financiers, calculs mathématiques, recommandations basées sur le Ratio de Sharpe en temps réel, consultation du portefeuille, aide contextuelle par onglet, recherche floue (`difflib`). |

#### 📁 `website/pages/`

| Page | Description |
|---|---|
| `1_Marché.py` | **Marché** — 6 sous-onglets : Temps Réel (cours 1 min + VWAP + jauge RSI), Historique (chandeliers + Bollinger + SMA), Volatilité & Volume (volatilité glissante + détection d'anomalies), Statistiques (Sharpe, Bêta, Skewness, Kurtosis), Rendements (distribution empirique vs normale), Corrélation (heatmap Pearson multi-actifs). |
| `2_Portefeuille.py` | **Portefeuille** — Ordres achat/vente sur Actions/ETFs et Options (Call/Put pricées Black-Scholes). Multi-portefeuilles. Suivi des positions avec PnL latent coloré. Camembert d'allocation. Export CSV. |
| `3_Backtesting.py` | **Backtesting** — Simulation historique de stratégies SMA, RSI, VWAP. Mode Comparatif (3 stratégies sur un seul graphique). Métriques : rendement, Alpha vs Buy & Hold, Max Drawdown, commissions. |
| `4_Bot.py` | **Bot de Trading** — 4 stratégies (SMA, RSI, VWAP, ML Random Forest). Le mode ML utilise le Grid Search C++ pour optimiser SMA/RSI + Grid Search Python pour VWAP. Calibration Platt Scaling + CV 5-Folds. Rapport narratif complet avant autorisation d'ordre. |
| `5_Dérivés.py` | **Dérivés** — Pricing Call/Put Black-Scholes avec surface 3D interactive, Volatility Smile (prix vs strike pour différentes σ), courbes de sensibilité des Greeks en fonction de S. |
| `6_Assistant.py` | **Assistant** — Chatbot interactif : explications de concepts, consultation du portefeuille, calculs, recommandations basées sur le Sharpe, aide contextuelle. Suggestions rapides et historique de conversation. |
| `7_Documentation.py` | **Documentation** — Mode d'emploi complet, explication détaillée de chaque graphique, formules et interprétation des indicateurs, cours de finance accéléré (Actions, Risque, ETF, Options, Analyse technique/fondamentale). |
| `8_Paramètres.py` | **Paramètres** — Modification du mot de passe (avec vérification), ajout/modification d'email, gestion des portefeuilles (renommer, supprimer), suppression du compte avec double confirmation. |
| `9_Légal.py` | **Légal** — Politique de Confidentialité (RGPD), Conditions Générales d'Utilisation, Mentions Légales. |

---

### Fichiers Racine

| Fichier | Description |
|---|---|
| `launch.sh` | Terminal de lancement interactif Linux/macOS : 6 options (site web, données, dépendances, tests, Grid Search, quitter) avec choix du navigateur et nettoyage automatique du port. |
| `Lancer_TradeDesk.bat` | Équivalent Windows du script de lancement avec les mêmes fonctionnalités. |
| `populate_db.py` | Script d'alimentation des bases de données : initialise les tables puis exécute le pipeline Medallion multi-threadé sur les +1 000 actifs. |
| `run_tests.py` | Découverte et exécution automatique de tous les tests unitaires avec rapport détaillé. |
| `run_grid_search.py` | Outil en ligne de commande pour lancer une optimisation Grid Search C++ (SMA + RSI) sur un actif choisi par l'utilisateur. |
| `requirements.txt` | Dépendances : `streamlit`, `yfinance`, `pandas`, `numpy`, `scipy`, `plotly`, `pytickersymbols`, `scikit-learn`, `psycopg2-binary`. |
| `.gitignore` | Exclusion des fichiers `.db`, `.so`, `.dll`, `.venv/`, `__pycache__/`, `.streamlit/`, binaires C++. |

---

## 🏗️ Architecture & Pipeline de Données (Medallion)

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

| Table | Contenu |
|---|---|
| `bronze_prices` | Données brutes OHLCV issues de yfinance |
| `silver_prices` | Rendements journaliers, SMA20, SMA50, RSI14 |
| `gold_kpis` | Indicateurs de performance (Sharpe, Bêta, Volatilité) |
| `users` | Comptes utilisateurs (username, password_hash, created_at) |
| `portfolios` | Liste des portefeuilles par utilisateur |
| `portfolio_state` | Liquidités et capital initial par portefeuille |
| `portfolio_positions` | Positions ouvertes (actif, quantité, prix moyen) |
| `portfolio_transactions` | Historique complet des ordres passés |

---

## 🔐 Sécurité — Authentification

```
Mot de passe brut ──► PBKDF2(password, sel_16_octets, 100_000_iterations, SHA-256)
                  ──► Stockage : "sel_hex:hash_hex"
```

- ✅ **Sel unique** par utilisateur (16 octets aléatoires via `os.urandom`)
- ✅ **100 000 itérations** → attaque par force brute rendue très coûteuse
- ✅ **`hmac.compare_digest()`** → protection contre les timing attacks
- ✅ **Aucun mot de passe en clair** ne transite ni n'est stocké

---

## 🔧 Moteur C++ (Grid Search & Black-Scholes)

Le module `finance/engine.cpp` est compilé automatiquement en bibliothèque partagée via `g++` ou `clang++`. Un **fallback Python pur** prend le relais si le compilateur est absent.

| Fonction C++ | Rôle |
|---|---|
| `grid_search_sma_cpp` | Teste toutes les combinaisons de fenêtres SMA (courte 5–20, longue 21–60) |
| `grid_search_rsi_cpp` | Optimise la fenêtre RSI (5–21) et les seuils surachat/survente |
| `black_scholes_pricing_cpp` | Pricing d'options Call/Put (modèle de Black-Scholes 1973) |
| `total_brut`, `total_net_achat/vente` | Calcul des coûts de transaction avec commission 1 % |
| `calculer_performance` | Calcul du ROI en pourcentage |

---

## 🧪 Suite de Tests

```
Finance (C++ / Python) : Calcul des commissions, ROI, total net    — 5 tests
Greeks & Math          : Black-Scholes, Sharpe, Volatilité          — 5 tests
Pipeline Medallion     : Flux Bronze → Silver → Gold                — 1 test
ML Calibration         : Random Forest + Platt Scaling              — tests
Gestion de Portefeuille: Passages d'ordres, PAMP, persistance SQL   — 8 tests
Simulation & Backtest  : Stratégies SMA, RSI, VWAP                  — 5 tests
```

---

## 🚀 Lancement en Local

### Méthode 1 — Terminal de lancement interactif (recommandé)

**Linux / macOS** :
```bash
chmod +x launch.sh    # Rendre le script exécutable (une seule fois)
./launch.sh
```

**Windows** :
```cmd
Lancer_TradeDesk.bat
```

Le terminal propose un menu interactif :
1. **Lancer le Site Web** — Démarre Streamlit avec choix du navigateur
2. **Récupérer les données** — Lance le pipeline Medallion multi-threadé
3. **Installer les dépendances** — Crée le `.venv` et installe les packages
4. **Lancer les tests** — Exécute toute la suite de tests unitaires
5. **Grid Search C++** — Optimisation des paramètres de trading
6. **Quitter**

### Méthode 2 — Lancement manuel pas à pas

**1. Créer l'environnement virtuel et installer les packages** :
```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

**2. Configurer les secrets Supabase** — Créer le fichier `.streamlit/secrets.toml` :
```toml
[postgres]
DB_USER     = "postgres"
DB_PASSWORD = "votre_mot_de_passe_supabase"
DB_HOST     = "votre_host.supabase.co"
DB_PORT     = "5432"
DB_NAME     = "postgres"
```

**3. Remplir les bases de données** (première utilisation) :
```bash
python populate_db.py
```

**4. Lancer le serveur Streamlit** :
```bash
streamlit run website/TradeDesk.py
```
L'application s'ouvre automatiquement sur `http://localhost:8501`.

**5. Lancer les tests** (optionnel) :
```bash
python run_tests.py
```

### Méthode 3 — GitHub Codespaces

Ouvrir le projet dans GitHub Codespaces : les dépendances s'installent automatiquement et Streamlit démarre sur le port 8501.

---

## 📖 Manuel d'Utilisation

### 1. Créer un compte

1. Ouvrir TradeDesk dans le navigateur.
2. Cliquer sur l'onglet **Inscription**.
3. Choisir un nom d'utilisateur (≥ 3 caractères) et un mot de passe (≥ 4 caractères).
4. Régler le **capital de départ** avec le slider (1 000 € à 1 000 000 €).
5. Cliquer sur **Créer mon compte**, puis se connecter.

### 2. Explorer le Marché

1. Aller dans la page **Marché** via le menu latéral.
2. Sélectionner un actif parmi les 1 000+ disponibles (actions US/EU, ETFs, cryptos, indices).
3. **Temps Réel** : voir le cours intraday 1 min avec la ligne VWAP et la jauge RSI.
4. **Historique** : afficher les chandeliers japonais, Bandes de Bollinger, SMA 20/50, RSI et volumes.
5. **Statistiques** : consulter la volatilité, le Ratio de Sharpe, le Bêta, le Skewness et le Kurtosis.
6. **Corrélation** : sélectionner plusieurs actifs pour afficher la heatmap de corrélation Pearson.

### 3. Gérer le Portefeuille

1. Page **Portefeuille** → choisir le type d'instrument (Action/ETF ou Option Call/Put).
2. Sélectionner l'actif, la quantité et l'action (Achat ou Vente).
3. Les options sont pricées automatiquement avec Black-Scholes (Strike + Maturité personnalisables).
4. Commission de **1 %** appliquée sur chaque transaction.
5. Suivre les positions ouvertes avec le PnL latent coloré (vert = gain, rouge = perte).
6. Consulter le camembert d'allocation et exporter l'historique en CSV.

### 4. Backtester une Stratégie

1. Page **Backtesting** → choisir un actif, une stratégie (SMA / RSI / VWAP) et une période.
2. Ajuster les paramètres avec les sliders (fenêtres SMA, seuils RSI, fenêtre VWAP).
3. Cliquer sur **Lancer le Backtest**.
4. Lire les résultats : rendement, Alpha vs Buy & Hold, Max Drawdown, nombre d'ordres.
5. Utiliser le mode **Comparatif** pour afficher SMA vs RSI vs VWAP sur le même graphique.

### 5. Utiliser le Bot de Trading

1. Page **Bot** → choisir un actif et une stratégie parmi SMA, RSI, VWAP ou **Machine Learning**.
2. Cliquer sur **Analyser** pour générer le rapport complet.
3. En mode ML, le bot exécute automatiquement un Grid Search C++ (SMA + RSI) et Python (VWAP), puis entraîne un modèle Random Forest calibré.
4. Si un signal d'achat ou de vente est détecté, un bouton d'**autorisation** apparaît.
5. **Le bot ne passe jamais d'ordre sans votre validation explicite.**

### 6. Pricer des Options (Dérivés)

1. Page **Dérivés** → régler les paramètres : prix de l'actif (S), Strike (K), maturité (T), volatilité (σ), taux sans risque (r).
2. Choisir Call ou Put.
3. Consulter le prix théorique et les 5 Greeks (Delta, Gamma, Vega, Theta, Rho).
4. Explorer la **surface 3D** interactive (prix = f(Strike, Maturité)).
5. Voir le **Volatility Smile** et les courbes de sensibilité des Greeks.

### 7. Poser des Questions à l'Assistant

1. Page **Assistant** → taper une question en langage naturel.
2. L'assistant peut : expliquer des concepts financiers (RSI, VWAP, Sharpe…), consulter votre portefeuille, faire des calculs, recommander des actifs (basé sur le Ratio de Sharpe), et guider dans l'application.

### 8. Consulter la Documentation

1. Page **Documentation** → mode d'emploi complet, explication de chaque graphique avec formules et tables d'interprétation, cours de finance accéléré en 6 chapitres.

### 9. Gérer les Paramètres du Compte

1. Page **Paramètres** → modifier le mot de passe, ajouter/modifier l'email, gérer les portefeuilles (renommer, supprimer), supprimer le compte (avec double confirmation).

---

*Projet informatique réalisé dans le cadre de la Licence L1 Économie-Gestion — Université Paris Nanterre.*
