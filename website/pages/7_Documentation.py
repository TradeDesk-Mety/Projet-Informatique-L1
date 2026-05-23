import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui

set_global_ui()
render_assistant()

import streamlit as st

if not st.session_state.get("logged_in", False):
    st.warning("Connecte-toi depuis la page d'accueil.")
    st.stop()

st.title("Documentation & Apprentissage")
st.caption("Mode d'emploi complet, explication des graphiques, stratégies et cours de finance.")

tab_mode_emploi, tab_graphiques, tab_strategies, tab_cours, tab_glossaire = st.tabs([
    "Mode d'Emploi",
    "Comprendre les Graphiques",
    "Stratégies & Indicateurs",
    "Cours de Finance",
    "Glossaire",
])

#TAB 1 — MODE D'EMPLOI
with tab_mode_emploi:
    st.header("Mode d'Emploi de la Plateforme TradeDesk")
    st.info(
        "TradeDesk est une plateforme de **paper trading** — vous investissez avec de l'argent fictif "
        "sur des données de marché réelles. Aucun risque financier réel."
    )

    with st.expander("1. Démarrage rapide — Premiers pas", expanded=True):
        st.markdown("""
**Étape 1 : Créez votre compte**

Depuis la page d'accueil, choisissez l'onglet **Inscription** :
- Choisissez un pseudo (min. 3 caractères)
- Définissez un mot de passe (min. 4 caractères)
- Sélectionnez votre **capital de départ** (entre 1 000 € et 1 000 000 €) via le curseur

Ce capital est fictif. Il simule le montant que vous auriez à investir.

**Étape 2 : Explorez le marché**

Rendez-vous dans l'onglet **Marché** :
- Choisissez un actif dans la liste (actions, ETFs, cryptos, indices)
- Sélectionnez la **période** (ex. 1 mois, 1 an) et l'**intervalle** (ex. 1 jour, 1 heure)
- Parcourez les 6 sous-onglets pour analyser l'actif sous tous ses angles

**Étape 3 : Passez votre premier ordre**

Dans l'onglet **Portefeuille** → **Passer un ordre** :
- Choisissez **Achat** ou **Vente**, le type d'instrument et l'actif
- Entrez la quantité souhaitée
- Vérifiez le récapitulatif (prix, commission, montant net)
- Cliquez sur **ACHETER — Confirmer**

Une commission de **1%** est automatiquement déduite, comme dans la réalité.

**Étape 4 : Suivez vos performances**

Dans l'onglet **Positions** du Portefeuille :
- Consultez vos positions ouvertes avec les gains/pertes en temps réel
- Le graphique camembert montre la répartition de votre portefeuille
- L'onglet **Historique** liste toutes vos transactions passées
""")

    with st.expander("2. Onglet Marché — Guide détaillé", expanded=False):
        st.markdown("""
L'onglet **Marché** est votre centre d'analyse. Il contient 6 sous-onglets :

| Sous-onglet | Ce qu'il montre | Quand l'utiliser |
|---|---|---|
| **Temps Réel** | Cours selon la période/intervalle sélectionnés + VWAP + jauge RSI | Pour suivre l'évolution sur n'importe quelle fenêtre temporelle |
| **Historique** | Chandeliers japonais + SMA20/50 + Bandes de Bollinger + Volume | Pour analyser la tendance et les niveaux techniques |
| **Volatilité & Volume** | Volatilité glissante + anomalies de volume | Pour identifier les périodes de risque accru |
| **Statistiques** | Sharpe, Bêta, Skewness, Kurtosis, Rendement | Pour évaluer la qualité risque/rendement |
| **Rendements** | Distribution empirique vs loi normale | Pour comprendre le comportement statistique |
| **Corrélation** | Matrice de corrélation entre plusieurs actifs | Pour optimiser la diversification |

**Combinaisons période/intervalle recommandées :**

| Objectif | Période | Intervalle |
|---|---|---|
| Trading intraday | 1d | 1m ou 5m |
| Analyse court terme | 5d | 15m ou 1h |
| Analyse moyen terme | 3mo ou 6mo | 1d |
| Analyse long terme | 1y ou 2y | 1d ou 1wk |

⚠️ Les données intraday (1m, 5m, 15m) ne sont disponibles que sur des périodes courtes via yfinance :
- 1m → max 7 jours
- 5m/15m → max 60 jours
- 1h → max 730 jours
""")

    with st.expander("3. Onglet Portefeuille — Guide détaillé", expanded=False):
        st.markdown("""
L'onglet **Portefeuille** contient 3 sous-onglets indépendants :

**Passer un ordre**

Deux types d'instruments disponibles :

*Actions / ETFs :*
- Achat : sélectionnez n'importe quel actif de la liste du marché
- Vente : seules vos positions existantes sont proposées (évite les erreurs)
- Le prix affiché est le dernier cours connu (rafraîchi toutes les 10 secondes)

*Options (Call / Put) :*
- Un **Call** parie sur la hausse du sous-jacent
- Un **Put** parie sur la baisse (ou sert de couverture)
- Le prix de l'option (prime) est calculé automatiquement via le modèle **Black-Scholes**
- La volatilité historique (3 mois) est estimée automatiquement
- Le ticker de l'option suit le format : `ACTIF_TYPE_STRIKE_MATURITE`

**Structure des commissions :**
```
Montant brut    = Quantité × Prix unitaire
Commission      = Montant brut × 1%
Montant net     = Montant brut + Commission  (à l'achat)
                = Montant brut - Commission  (à la vente)
```

**Positions**

Le tableau des positions affiche pour chaque actif :
- `Px moyen` : prix d'acquisition moyen pondéré (PAMP)
- `Px actuel` : valeur de marché actuelle
- `G/P` : Gain/Perte en euros (valeur actuelle - valeur d'achat) × quantité
- `ROI` : Return on Investment en % = (Px actuel - Px moyen) / Px moyen × 100

**Historique**

Toutes vos transactions sont enregistrées avec horodatage, prix et commission.
Exportez-les en CSV pour votre propre analyse.
""")

    with st.expander("4. Onglet Bot de Trading — Guide détaillé", expanded=False):
        st.markdown("""
Le **Bot de Trading** est un assistant algorithmique qui analyse le marché et propose des décisions.

**Important** : le bot ne passe jamais un ordre sans votre validation explicite.

**Workflow en 5 étapes :**
1. Sélectionnez l'actif et la stratégie
2. Ajustez les paramètres (fenêtres SMA, seuils RSI, etc.)
3. Cliquez sur **Analyser**
4. Lisez le rapport narratif complet généré par le bot
5. Si un signal ACHAT ou VENTE est détecté, validez ou refusez l'ordre

**Les 4 stratégies disponibles :**

| Stratégie | Logique de décision | Force | Limite |
|---|---|---|---|
| SMA | Croisement de moyennes mobiles | Simple, robuste | Retardée (lagging) |
| RSI | Zones de surachat/survente | Bon pour les marchés en range | Génère de faux signaux en tendance forte |
| VWAP | Écart au prix moyen institutionnel | Référence des pros | Moins pertinent sur données journalières |
| Machine Learning | Random Forest entraîné sur 1 an | Capte des patterns complexes | Nécessite assez d'historique |

**La stratégie ML en détail :**
Le modèle est entraîné sur des features calculées à partir des 252 derniers jours :
rendements récents, ratio SMA, RSI, volatilité court terme.
Il prédit si le cours sera plus haut dans 3 jours.
Un Grid Search C++ optimise les paramètres SMA/RSI avant l'entraînement.
""")

    with st.expander("5. Onglet Backtesting — Guide détaillé", expanded=False):
        st.markdown("""
Le **Backtesting** simule une stratégie sur des données historiques réelles pour évaluer sa rentabilité
*avant* de l'appliquer avec du vrai argent.

**Métriques clés et leur interprétation :**

| Métrique | Définition | Bonne valeur |
|---|---|---|
| Rendement stratégie | Gain total de l'algorithme sur la période | Le plus élevé possible |
| Buy & Hold | Référence : acheter au début et ne jamais vendre | Votre benchmark |
| Alpha | Différence Stratégie - Buy & Hold | > 0 (la stratégie bat le marché) |
| Max Drawdown | Pire chute depuis un sommet | Le plus proche de 0% |
| Nombre d'ordres | Total des transactions | Peu d'ordres = moins de commissions |
| Commissions payées | 1% × chaque transaction | Le moins possible |

**Conseil d'interprétation :**
Un alpha positif ne suffit pas. Si le Max Drawdown est de -50%, la stratégie est trop risquée
même si elle performe sur le long terme. Le meilleur système combine alpha positif ET drawdown limité.

**Pièges à éviter :**
- L'**overfitting** : paramètres trop optimisés sur le passé qui ne fonctionnent plus en live
- Le **data snooping** : tester des dizaines de combinaisons jusqu'à trouver la meilleure par hasard
- Les **biais de survie** : les actifs qui ont disparu ne sont pas dans la liste (biais favorable)
""")

    with st.expander("6. Onglet Dérivés — Guide détaillé", expanded=False):
        st.markdown("""
L'onglet **Dérivés** permet de pricer des options européennes avec le modèle Black-Scholes (1973).

**Les 5 paramètres du modèle :**

| Paramètre | Symbole | Description |
|---|---|---|
| Prix actuel | S | Valeur du sous-jacent aujourd'hui |
| Strike | K | Prix d'exercice de l'option |
| Maturité | T | Temps restant avant expiration (en années) |
| Volatilité | σ | Volatilité annualisée du sous-jacent |
| Taux sans risque | r | Rendement d'un actif sans risque (ex: OAT 10 ans) |

**Les 3 sous-onglets :**
- **Surface 3D** : visualise Prix = f(Strike, Maturité) — vous voyez comment le prix évolue selon ces deux axes simultanément
- **Volatility Smile** : compare le prix pour différentes volatilités implicites. En pratique, la volatilité implicite varie selon le strike (phénomène de "smile")
- **Sensibilité des Greeks** : montre comment chaque Greek évolue quand le prix du sous-jacent change

**Ordre de grandeur des Greeks typiques (option ATM, σ=25%, T=1 an) :**

| Greek | Ordre de grandeur | Signe |
|---|---|---|
| Delta Call | 0.45 à 0.65 | + |
| Gamma | 0.005 à 0.02 | + |
| Theta | -0.05 à -0.02 | - (toujours) |
| Vega | 0.2 à 0.6 | + |
| Rho | 0.2 à 0.6 | + (Call), - (Put) |
""")

#TAB 2 — COMPRENDRE LES GRAPHIQUES
with tab_graphiques:
    st.header("Comprendre les Graphiques de TradeDesk")
    st.info("Cette section explique en détail à quoi sert chaque graphique et comment l'interpréter correctement.")

    with st.expander("Graphique en Chandeliers Japonais (Candlestick)", expanded=True):
        st.markdown("""
**À quoi ça sert ?** C'est LE graphique central de l'analyse technique. Il résume en un coup d'œil
toute l'action du marché sur une période (une bougie = un jour, une heure, une minute...).

**Anatomie d'une bougie :**

```
          ┃  ← Mèche haute : plus haut atteint sur la période
    ┌─────┸─────┐
    │           │  ← Corps : entre ouverture et clôture
    │   CORPS   │
    └─────┰─────┘
          ┃  ← Mèche basse : plus bas atteint sur la période
```

| Élément | Bougie verte (haussière) | Bougie rouge (baissière) |
|---|---|---|
| Bas du corps | Prix d'ouverture | Prix de clôture |
| Haut du corps | Prix de clôture | Prix d'ouverture |
| Mèche haute | Plus haut de la période | Plus haut de la période |
| Mèche basse | Plus bas de la période | Plus bas de la période |

**Les indicateurs superposés :**

- **SMA 20 (orange)** : Moyenne des 20 derniers prix de clôture. Représente la tendance court terme.
  Si le prix est au-dessus → tendance haussière à court terme.
  Si le prix croise la SMA20 à la hausse → signal d'achat.

- **SMA 50 (bleu)** : Moyenne des 50 derniers prix de clôture. Tendance moyen terme.
  Un croisement SMA20 > SMA50 (Golden Cross) = signal haussier fort.
  Un croisement SMA20 < SMA50 (Death Cross) = signal baissier fort.

- **Bandes de Bollinger (gris, pointillé)** : SMA20 ± 2 écarts-types.
  Représentent 95% des prix "normaux". Un prix qui sort des bandes = anomalie.
  Bandes rétrécies (squeeze) → une forte variation est souvent imminente.
  Bandes écartées → marché volatile, en mode panique ou euphorie.

**Les barres de volume (en bas) :**
Vertes si la journée est haussière, rouges si baissière. Un volume élevé confirme la force du mouvement.
*Règle d'or : Le volume confirme le prix. Une hausse sans volume = signal faible.*
""")

    with st.expander("Graphique Temps Réel — Cours & VWAP", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Suivre l'évolution du cours sur la période et l'intervalle sélectionnés.
Adapté à toutes les fenêtres temporelles : du temps réel 1 minute à l'analyse pluriannuelle.

**Les éléments du graphique :**

- **Ligne colorée (cours)** : Trace l'évolution du prix bar par bar.
  - Verte → le prix est au-dessus du cours d'ouverture de la période.
  - Rouge → le prix est en-dessous du cours d'ouverture.

- **Ligne orange pointillée (VWAP)** : Volume Weighted Average Price.
  - Si le cours est **au-dessus du VWAP** → acheteurs dominants sur la période.
  - Si le cours est **en-dessous du VWAP** → vendeurs dominants.
  - Le VWAP est la référence d'exécution des fonds institutionnels.
  - Un cours qui revient vers le VWAP après s'en être éloigné = phénomène de "mean reversion".

- **Ligne horizontale pointillée** : Cours le plus récent pour une lecture facilitée.

- **Barres de volume (bas)** : Intensité des échanges à chaque période.

**La jauge RSI :**
Si au moins 15 barres sont disponibles, une jauge RSI(14) est affichée.
- Zone verte (< 30) : survente — possible rebond à venir
- Zone grise (30-70) : zone neutre — attendre un signal
- Zone rouge (> 70) : surachat — possible retournement à venir
""")

    with st.expander("Distribution des Rendements Journaliers", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Comprendre le comportement statistique d'un actif et quantifier son risque réel.
Ce graphique est la base de toute la finance quantitative moderne.

**Comment le lire ?**

- **Histogramme bleu** : fréquence empirique des rendements journaliers sur la période.
  Chaque barre représente un intervalle de rendements (ex: de -1% à -0.5%).

- **Courbe orange** : distribution normale théorique (courbe de Gauss "en cloche").
  Elle représente ce que devrait donner un actif parfaitement aléatoire.

**Les 4 scénarios d'interprétation :**

| Observation | Signification | Implication |
|---|---|---|
| Queues épaisses vs la courbe | Kurtosis élevé (leptokurtique) | Chocs extrêmes fréquents — risque réel sous-estimé par les modèles classiques |
| Asymétrie à gauche | Skewness négatif | Krachs soudains probables mais rallyes progressifs |
| Asymétrie à droite | Skewness positif | Rallyes fréquents mais krachs possibles |
| Centré, symétrique, proche de la normale | Actif bien comporté | Modèles de risque classiques fiables |

**Les lignes de référence :**
- **μ (moyenne)** : rendement journalier moyen. Annualisé × 252 = rendement attendu.
- **±1σ** : intervalle de confiance à 68%. Environ 68% des jours sont dans cette fourchette.
- **±2σ** : intervalle à 95%. Un jour hors de cette zone = événement rare (1 sur 20 statistiquement).

**Formule du rendement journalier :** `r_t = (Prix_t - Prix_{t-1}) / Prix_{t-1}`
""")

    with st.expander("Volatilité Historique Glissante", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Mesurer et visualiser l'évolution du risque dans le temps.
La volatilité n'est pas constante — elle clusterise : les périodes calmes sont suivies de périodes calmes,
et les périodes agitées sont suivies de périodes agitées (phénomène GARCH).

**Comment lire le graphique :**

- L'axe Y représente la **volatilité annualisée en %**.
- La ligne trace l'évolution de la volatilité calculée sur une fenêtre glissante (20 jours).

**Niveaux de référence par classe d'actif :**

| Niveau de volatilité | Interprétation | Exemples typiques |
|---|---|---|
| < 10% | Très faible | Obligations court terme, stablecoins |
| 10% — 20% | Faible | Grandes capitalisations défensives (santé, conso) |
| 20% — 35% | Normal | Actions tech, ETFs large cap |
| 35% — 60% | Élevé | Petites caps, secteurs cycliques |
| > 60% | Très élevé | Cryptomonnaies, biotech |

**Les pics de volatilité** correspondent à des événements de marché :
crises financières, publications de résultats surprises, événements géopolitiques, décisions de banques centrales.

**Formule** : `Vol_annualisée = σ(rendements) × √252`
*(252 = nombre moyen de jours de trading par an)*
""")

    with st.expander("Analyse des Volumes & Breakouts", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Identifier les signaux forts en repérant les anomalies de volume.
Le volume est la "conviction" derrière un mouvement de prix.

**Règle fondamentale :** *Le volume confirme le prix.*
- Hausse + volume fort = mouvement fiable ✅
- Hausse + volume faible = possible fausse cassure ⚠️
- Baisse + volume fort = panique vendeuse (bas potentiel) ou poursuite de la baisse

**Code couleur des barres de volume :**

| Couleur | Signification |
|---|---|
| Vert normal | Journée haussière, volume dans la norme |
| Rouge normal | Journée baissière, volume dans la norme |
| Jaune | Anomalie de volume (> 2× la moyenne mobile 20j) — signal fort |

**Les lignes superposées :**
- **Ligne bleue pointillée** : Moyenne Mobile du Volume sur 20 jours. C'est le niveau "normal" de volume.
- **Ligne jaune pointillée** : Seuil d'anomalie = 2× la moyenne. Toute barre dépassant ce niveau est une anomalie statistique significative.

**Stratégie pratique :** Combiné avec les chandeliers, un volume jaune lors d'un breakout haussier
(cassure d'une résistance) est un signal d'entrée potentiel fort.
""")

    with st.expander("Matrice de Corrélation (Heatmap)", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Comprendre comment les actifs évoluent ensemble.
La corrélation est la clé de la diversification de portefeuille (théorie de Markowitz, 1952).

**Comment lire la Heatmap :**

| Valeur | Couleur | Signification | Impact sur la diversification |
|---|---|---|---|
| +1.0 | Rouge | Évolution identique | Nulle — comme avoir le même actif |
| +0.5 à +0.9 | Orange | Fortement corrélés | Faible |
| -0.1 à +0.1 | Blanc/Neutre | Aucune relation | Excellente |
| -0.5 à -0.9 | Bleu | Fortement anti-corrélés | Parfaite — couverture naturelle |
| -1.0 | Bleu foncé | Évolution opposée exacte | Idéale pour la couverture |

**La diagonale** vaut toujours 1.0 (un actif est parfaitement corrélé à lui-même).

**Corrélations typiques observées :**
- Apple / Microsoft : ~0.85 (très corrélés, même secteur tech)
- Actions / Obligations : ~-0.2 à -0.5 (légèrement anti-corrélés)
- Bitcoin / S&P 500 : ~0.3 à 0.6 (corrélation variable selon les crises)
- Or / Marchés actions : ~-0.1 à 0.1 (quasi-décorrélé)

**Conseil de construction de portefeuille :**
Visez un panier d'actifs avec des corrélations moyennes proches de 0.3 à 0.5 maximum.
Un portefeuille 100% corrélé (corrélation = 1) n'offre aucune protection en cas de choc de marché.
""")

    with st.expander("Graphique Backtest : Equity Curve & Drawdown", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Évaluer la performance historique d'une stratégie algorithmique sur la durée.

**Panneau supérieur — Equity Curve (Évolution du capital) :**

| Ligne | Couleur | Signification |
|---|---|---|
| Stratégie | Verte | Évolution du capital investi avec la règle algorithmique |
| Buy & Hold | Orange pointillé | Référence passive : acheter au début et ne jamais vendre |

- Si la ligne stratégie est **constamment au-dessus** du Buy & Hold → alpha positif persistant
- Si elle est **en dessous** → la stratégie détruit de la valeur par rapport à l'inaction
- Des **croisements fréquents** → performance instable, dépendante des conditions de marché

**Panneau inférieur — Drawdown :**

Le drawdown mesure la perte en % depuis le dernier sommet historique du capital.
```
Drawdown(t) = (Valeur(t) - Maximum historique jusqu'à t) / Maximum historique jusqu'à t
```

- Toujours ≤ 0 (c'est une perte par rapport au sommet)
- **Max Drawdown** : le pire creux absolu. Ex: -25% = à un moment, le capital a perdu 25% depuis son pic
- Un Max Drawdown de -50% signifie qu'il faut ensuite +100% pour récupérer le capital initial !

**Critères de qualité d'un bon système :**

| Critère | Valeur cible |
|---|---|
| Alpha | > 5% annualisé |
| Max Drawdown | < 20% |
| Ratio Calmar (Alpha / |MaxDD|) | > 0.5 |
| Nombre d'ordres | Limité (commissions) |
""")

    with st.expander("Surface 3D Black-Scholes (Options)", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Visualiser simultanément comment le prix d'une option varie en fonction
de deux paramètres : le Strike et la Maturité.

**Les 3 axes :**

| Axe | Variable | Interprétation |
|---|---|---|
| X | Strike K | Prix d'exercice de l'option |
| Y | Maturité T | Temps restant avant expiration (en années) |
| Z | Prix | Valeur théorique calculée par Black-Scholes |

**Ce qu'on observe sur la surface :**

1. **Croissance avec la maturité** : plus l'option a de temps devant elle, plus elle est chère.
   Plus de temps = plus de chances que le marché bouge favorablement.

2. **Pic autour de ATM** (At-The-Money, K ≈ S) : les options à la monnaie ont la valeur temps maximale.
   Les options très dans la monnaie (ITM) n'ont presque que de la valeur intrinsèque.
   Les options très hors de la monnaie (OTM) ont quasi uniquement de la valeur temps.

3. **Colorscale** : les zones chaudes (rouge/jaune) = options les plus chères,
   les zones froides (bleu) = options les moins chères.

**Rappel valeur d'une option :**
```
Prix option = Valeur intrinsèque + Valeur temps
Valeur intrinsèque Call = max(S - K, 0)
Valeur intrinsèque Put  = max(K - S, 0)
Valeur temps            = Prix - Valeur intrinsèque  (toujours ≥ 0)
```
""")

#TAB 3 — STRATÉGIES & INDICATEURS
with tab_strategies:
    st.header("Stratégies & Indicateurs Techniques")
    st.write("Comprendre les algorithmes derrière chaque stratégie disponible sur TradeDesk.")

    with st.expander("SMA — Moyenne Mobile Simple", expanded=True):
        st.markdown("""
**Définition**

La SMA (Simple Moving Average) calcule la **moyenne arithmétique** des `n` derniers prix de clôture.
C'est l'indicateur le plus utilisé en analyse technique.

**Formule :**
```
SMA(n, t) = (Close_t + Close_{t-1} + ... + Close_{t-n+1}) / n
```

**Stratégie de croisement (utilisée dans TradeDesk) :**

```
Si SMA_courte(5) > SMA_longue(15) → SIGNAL ACHAT
Si SMA_courte(5) < SMA_longue(15) → SIGNAL VENTE
```

La logique : quand les prix récents (moyenne courte) dépassent les prix moyens (moyenne longue),
la tendance court terme accélère à la hausse → signal d'entrée optimiste.

**Paramètres sur TradeDesk :**
- Bot : SMA(5) / SMA(15) par défaut
- Backtesting : SMA court terme (5-50j) et long terme (20-200j) ajustables
- Graphique Marché : SMA(20) orange et SMA(50) bleue affichées en permanence

**Golden Cross et Death Cross :**

| Pattern | Condition | Signal |
|---|---|---|
| Golden Cross | SMA20 croise SMA50 à la hausse | Haussier fort — souvent suivi d'un rally |
| Death Cross | SMA20 croise SMA50 à la baisse | Baissier fort — souvent suivi d'une correction |

**Limites importantes :**
- **Indicateur retardé (lagging)** : les signaux arrivent *après* le début du mouvement
- Génère des faux signaux en marchés **latéraux** (sans tendance)
- Plus les fenêtres sont courtes, plus les signaux sont fréquents et les faux signaux nombreux
- Plus les fenêtres sont longues, plus les signaux sont rares mais fiables
""")

    with st.expander("RSI — Relative Strength Index", expanded=False):
        st.markdown("""
**Définition**

Développé par J. Welles Wilder (1978), le RSI est un **oscillateur de momentum** qui mesure
la vitesse et l'amplitude des mouvements de prix. Il est toujours compris entre 0 et 100.

**Formule de calcul (en 3 étapes) :**

```
Étape 1 : Calcul des variations journalières
  ΔP_t = Close_t - Close_{t-1}

Étape 2 : Séparation hausses/baisses sur n jours (14 par défaut)
  Gain_moyen = Moyenne(max(ΔP_t, 0)) sur n jours
  Perte_moyenne = Moyenne(max(-ΔP_t, 0)) sur n jours

Étape 3 : Calcul du RSI
  RS = Gain_moyen / Perte_moyenne
  RSI = 100 - (100 / (1 + RS))
```

**Zones d'interprétation standard :**

| Valeur RSI | Zone | Signal | Probabilité |
|---|---|---|---|
| < 20 | Survente extrême | Achat fort | Rebond très probable |
| 20 – 30 | Survente | Achat potentiel | Rebond probable |
| 30 – 70 | Zone neutre | Pas de signal | Attendre |
| 70 – 80 | Surachat | Vente potentielle | Correction probable |
| > 80 | Surachat extrême | Vente forte | Retournement très probable |

**Seuils utilisés sur TradeDesk :**
- Bot RSI : seuils **35/65** (légèrement plus conservateurs que 30/70)
- Backtesting : seuils oversold/overbought ajustables via les sliders

**Divergences RSI (signal avancé puissant) :**
- **Divergence haussière** : le prix fait un nouveau plus bas, mais le RSI fait un plus haut → inversement probable
- **Divergence baissière** : le prix fait un nouveau plus haut, mais le RSI fait un plus bas → correction probable

**Limites :**
Le RSI peut rester longtemps en zone de surachat dans une tendance haussière forte.
Il fonctionne mieux sur des marchés en **range** (sans tendance directionnelle forte).
""")

    with st.expander("VWAP — Volume Weighted Average Price", expanded=False):
        st.markdown("""
**Définition**

Le VWAP est le **prix moyen pondéré par le volume** d'échanges sur une période.
C'est LA référence de pricing des traders institutionnels (fonds, banques d'investissement).

**Formule :**

```
Prix typique_t    = (High_t + Low_t + Close_t) / 3

VWAP_glissant(n) = Σ(Prix_typique_t × Volume_t) / Σ(Volume_t)
sur les n dernières périodes
```

**Signaux sur TradeDesk :**

| Condition | Signal | Logique |
|---|---|---|
| Cours < VWAP − 2% | ACHAT | L'actif est bon marché par rapport au consensus du marché |
| Cours > VWAP + 2% | VENTE | L'actif est cher par rapport au consensus |
| |Écart| < 2% | NEUTRE | Prix équitable, attendre |

**Pourquoi le VWAP est-il important ?**

Les grands fonds d'investissement ont pour objectif de trader **autour du VWAP** pour minimiser
leur impact sur le marché. Si un investisseur institutionnel achète massivement en dessous du VWAP,
c'est un signal que l'actif est considéré bon marché par les "smart money".

**Deux utilisations différentes :**

| Utilisation | Calcul | Reset |
|---|---|---|
| Intraday (graphique Temps Réel) | Depuis l'ouverture du jour | Chaque matin |
| Backtesting / Bot | Fenêtre glissante (20j) | Jamais (continu) |

**Avantages vs SMA :**
Le VWAP pondère par le volume — un prix échangé à fort volume "compte plus".
Il est donc plus représentatif du vrai consensus de marché que la simple moyenne des prix.
""")

    with st.expander("Machine Learning — Random Forest", expanded=False):
        st.markdown("""
**Définition**

Le Random Forest est un algorithme d'**apprentissage supervisé par ensemble** :
il combine les prédictions de nombreux arbres de décision pour obtenir une prédiction robuste.

**Architecture du modèle TradeDesk :**

```
Données historiques (252 jours)
         ↓
Feature Engineering (7 features)
         ↓
Grid Search C++ (optimisation SMA/RSI)
         ↓
Random Forest (50 arbres, profondeur max 5)
         ↓
Calibration Platt Scaling
         ↓
Cross-Validation 5-Folds
         ↓
Probabilité de hausse dans 3 jours
```

**Les 7 features utilisées :**

| Feature | Formule | Ce qu'elle capte |
|---|---|---|
| ret1 | (P_t - P_{t-1}) / P_{t-1} | Momentum 1 jour |
| ret3 | (P_t - P_{t-3}) / P_{t-3} | Momentum 3 jours |
| ret5 | (P_t - P_{t-5}) / P_{t-5} | Momentum 5 jours |
| sma_ratio | SMA(5) / SMA(15) | Force de la tendance |
| rsi14 | RSI(14) | Zone surachat/survente |
| vol10 | σ(ret) sur 10j | Incertitude récente |
| volume_ratio | Vol_j / MA(Vol, 20j) | Anomalie de volume |

**Règles de décision :**

| Probabilité de hausse | Signal | Action proposée |
|---|---|---|
| > 55% | ACHAT | Ordre d'achat soumis à validation |
| 45% — 55% | NEUTRE | Aucun ordre (incertitude trop haute) |
| < 45% | VENTE | Ordre de vente soumis à validation |

**Mesures anti-overfitting :**
- Profondeur max des arbres : 5 (évite la mémorisation)
- Cross-validation 5-Folds : détecte si le modèle mémorise plutôt qu'apprend
- Calibration Platt Scaling : corrige le biais des probabilités brutes du Random Forest
""")

    with st.expander("Bandes de Bollinger", expanded=False):
        st.markdown("""
**Définition**

Développées par John Bollinger dans les années 1980, les Bandes de Bollinger créent
une **enveloppe dynamique** autour du prix basée sur la volatilité récente.

**Formule :**
```
Bande centrale   = SMA(20)
Bande supérieure = SMA(20) + 2 × σ(20)   (écart-type sur 20 jours)
Bande inférieure = SMA(20) - 2 × σ(20)
```

**Propriété statistique :**
Dans une distribution normale, ~95% des prix devraient se situer entre les deux bandes.
Quand un prix sort des bandes, c'est un événement statistiquement rare (< 5% du temps).

**Signaux d'interprétation :**

| Situation | Interprétation | Signal potentiel |
|---|---|---|
| Prix touche la bande supérieure | Surévaluation à court terme | Vente ou prudence |
| Prix touche la bande inférieure | Sous-évaluation à court terme | Achat potentiel |
| Bandes rétrécies (Squeeze) | Faible volatilité → explosion imminente | Anticiper une forte variation |
| Bandes très écartées | Forte volatilité → épuisement possible | Possible retournement |
| Prix revient vers la bande centrale | Mean reversion | Signal neutre |

**Stratégie Bollinger Bounce :**
Acheter quand le prix touche la bande inférieure ET revient vers le milieu.
Vendre quand il touche la bande supérieure ET redescend.
Fonctionne bien en marchés sans tendance (range).

**Stratégie Bollinger Breakout :**
Acheter lors d'une cassure de la bande supérieure après un squeeze (signe de tendance forte).
""")

    with st.expander("Ratio de Sharpe — Mesure de Performance Ajustée au Risque", expanded=False):
        st.markdown("""
**Définition**

Développé par William Sharpe (Prix Nobel 1990), le Ratio de Sharpe est **la mesure de performance
ajustée au risque de référence** en finance quantitative.

**Formule :**
```
Sharpe = (Rendement annualisé − Taux sans risque) / Volatilité annualisée

Où :
- Rendement annualisé = Rendement moyen journalier × 252
- Volatilité annualisée = σ(rendements journaliers) × √252
- Taux sans risque ≈ 0% sur TradeDesk (pour simplifier)
```

**Tableau d'interprétation :**

| Ratio de Sharpe | Qualité de l'investissement |
|---|---|
| < 0 | Actif destructeur de valeur (perd de l'argent après ajustement) |
| 0 – 0.5 | Médiocre — ne vaut pas le risque pris |
| 0.5 – 1.0 | Acceptable — correct mais pas exceptionnel |
| 1.0 – 2.0 | Bon — rendement bien rémunéré par rapport au risque |
| > 2.0 | Excellent — très rare en pratique sur le long terme |

**Exemples réels :**
- S&P 500 (long terme) : ~0.5 à 0.6
- Warren Buffett (Berkshire Hathaway) : ~0.8 à 1.0 sur 50 ans
- Fonds Medallion de Simons : ~2.0+ (exceptionnel)
- Bitcoin (2020-2024) : ~0.5 à 1.5 selon les périodes

**Limites du Ratio de Sharpe :**
- Il suppose que les rendements suivent une loi normale (ce qui est faux pour les cryptos et en période de crise)
- Il pénalise également les bons et les mauvais écarts de rendement (la volatilité à la hausse n'est pas un risque !)
- Alternative : le **Ratio de Sortino** ne pénalise que la volatilité à la baisse.
""")

    with st.expander("Bêta — Sensibilité par rapport au Marché", expanded=False):
        st.markdown("""
**Définition**

Le Bêta (β) mesure la **sensibilité des rendements d'un actif par rapport à ceux du marché de référence** (S&P 500 sur TradeDesk).

**Formule :**
```
β = Cov(Rendements_actif, Rendements_marché) / Var(Rendements_marché)
```

**Interprétation :**

| Bêta | Signification | Exemple typique |
|---|---|---|
| β = 0 | Aucune corrélation avec le marché | Or, stablecoins |
| 0 < β < 1 | Moins réactif que le marché | Utilities, santé, alimentation |
| β = 1 | Suit parfaitement le marché | ETF S&P 500 |
| β > 1 | Plus réactif que le marché | Tech, biotech, cryptos |
| β < 0 | Évolue en sens inverse du marché | Options Put, actifs de couverture |

**Calcul du risque systématique :**
```
Risque total = Risque systématique (β × marché) + Risque spécifique (idiosyncratique)
```

Le risque spécifique peut être éliminé par la diversification.
Le risque systématique (β) ne peut PAS être éliminé — c'est le risque incompressible du marché.

**Exemple pratique :**
Si β = 1.5 et le S&P 500 baisse de -10%, votre actif devrait baisser de ~-15%.
Si le S&P 500 monte de +10%, votre actif devrait monter de ~+15%.
""")

#TAB 4 — COURS DE FINANCE
with tab_cours:
    st.header("Les Bases de la Finance et de l'Investissement")
    st.write("Un cours complet pour comprendre les marchés financiers, du plus simple au plus avancé.")

    with st.expander("Chapitre 1 — Qu'est-ce qu'une Action ?", expanded=True):
        st.markdown("""
**Définition**

Une action (ou *share* en anglais) est un **titre de propriété** représentant une fraction du capital
d'une entreprise. En achetant une action Apple, vous devenez propriétaire d'une infime partie d'Apple Inc.

**Les 3 droits d'un actionnaire :**
1. **Droit patrimonial** : participer aux bénéfices via les dividendes et la plus-value de l'action
2. **Droit de vote** : voter aux assemblées générales annuelles (proportionnel au nombre d'actions)
3. **Droit à l'information** : accès aux rapports financiers publiés

**Les 2 sources de rendement d'une action :**

| Source | Définition | Fréquence |
|---|---|---|
| Plus-value (capital gain) | Hausse du cours entre l'achat et la vente | À la vente uniquement |
| Dividende | Part des bénéfices versée aux actionnaires | Trimestrielle ou annuelle |

**Types d'actions :**
- **Actions ordinaires** : droits standards (dividendes, vote)
- **Actions de préférence** : dividendes prioritaires, souvent sans droit de vote
- **Actions à droit de vote double** : système utilisé par Hermès, LVMH pour garder le contrôle familial

**Le prix d'une action :**
Théoriquement, le prix d'une action = valeur actuelle de tous les dividendes futurs attendus.
En pratique, il reflète aussi les anticipations, les émotions et la liquidité du marché.

**Différence entre valeur et prix :**
- **Valeur intrinsèque** : ce que vaut réellement l'entreprise (analyse fondamentale)
- **Prix de marché** : ce que les investisseurs *acceptent de payer* à un instant T
- L'analyse technique étudie le prix. L'analyse fondamentale cherche la valeur.
""")

    with st.expander("Chapitre 2 — Le Risque et la Volatilité", expanded=False):
        st.markdown("""
**La relation fondamentale risque/rendement**

En finance, il n'y a pas de repas gratuit : **un rendement plus élevé exige de prendre plus de risque**.
C'est le principe de base du CAPM (Capital Asset Pricing Model).

```
Rendement attendu = Taux sans risque + β × (Rendement marché − Taux sans risque)
```

**Les différents types de risque :**

| Type de risque | Définition | Peut-on s'en protéger ? |
|---|---|---|
| Risque de marché (β) | Risque lié aux fluctuations globales du marché | Non (diversification insuffisante) |
| Risque spécifique | Risque propre à une entreprise (fraude, mauvais résultats) | Oui (diversification) |
| Risque de liquidité | Impossibilité de vendre rapidement sans impacter le prix | Partiellement |
| Risque de taux | Impact d'une variation des taux d'intérêt sur les prix | Partiellement (obligations) |
| Risque de change | Fluctuation des devises pour les actifs étrangers | Oui (couverture FX) |
| Risque de contrepartie | L'autre partie ne respecte pas ses obligations | Partiellement |

**Mesures quantitatives du risque sur TradeDesk :**

| Mesure | Ce qu'elle quantifie | Formule simplifiée |
|---|---|---|
| Volatilité annualisée | Amplitude des variations | σ(rendements) × √252 |
| Ratio de Sharpe | Rendement par unité de risque | (R - Rf) / σ |
| Bêta | Sensibilité au marché | Cov(actif, marché) / Var(marché) |
| Max Drawdown | Pire perte depuis un sommet | min((Valeur - Pic) / Pic) |
| Skewness | Asymétrie des rendements | Mesure statistique du 3e moment |
| Kurtosis | Fréquence des événements extrêmes | Mesure statistique du 4e moment |

**La règle de diversification de Markowitz (1952) :**
En combinant des actifs peu corrélés entre eux, on peut **réduire le risque global sans diminuer le rendement attendu**.
C'est le seul "repas gratuit" de la finance. Un portefeuille bien diversifié a un risque inférieur
à la moyenne des risques de ses composants.
""")

    with st.expander("Chapitre 3 — ETFs et Indices Boursiers", expanded=False):
        st.markdown("""
**Les indices boursiers**

Un indice boursier est un **baromètre statistique** mesurant la performance d'un groupe d'actions.
Il permet de suivre l'évolution globale d'un marché.

| Indice | Pays | Composition | Particularité |
|---|---|---|---|
| S&P 500 | USA | 500 plus grandes entreprises | Pondéré par capitalisation boursière |
| Nasdaq 100 | USA | 100 entreprises tech cotées | Très concentré sur la tech |
| CAC 40 | France | 40 plus grandes capi | Pondéré par capi flottante |
| FTSE 100 | UK | 100 plus grandes capi | Pondéré par capi |
| Nikkei 225 | Japon | 225 entreprises | Pondéré par les prix (inhabituel) |
| DAX 40 | Allemagne | 40 plus grandes capi | Inclut les dividendes réinvestis |

**Les ETFs (Exchange Traded Funds)**

Un ETF est un **fonds indiciel coté en bourse** qui réplique la performance d'un indice.
En achetant 1 action d'un ETF S&P 500, vous investissez dans les 500 entreprises simultanément.

**Avantages des ETFs :**

| Avantage | Explication |
|---|---|
| Diversification instantanée | Un seul achat = exposition à des centaines d'entreprises |
| Frais réduits | 0.03% à 0.5% par an (vs 1-2% pour les fonds actifs) |
| Liquidité | Se négocient en bourse comme des actions, toute la journée |
| Transparence | Composition publique et mise à jour régulièrement |
| Accessibilité | Dès quelques dizaines d'euros |

**Deux types de réplication :**
- **Réplication physique** : le fonds achète réellement les actions de l'indice (plus sûr)
- **Réplication synthétique** : utilise des swaps avec une contrepartie bancaire (moins cher mais plus risqué)

**ETF disponibles sur TradeDesk :**
S&P 500 ETF (SPY), Nasdaq QQQ, iShares MSCI World, ARK Innovation ETF, etc.
""")

    with st.expander("Chapitre 4 — Analyse Fondamentale vs Analyse Technique", expanded=False):
        st.markdown("""
**Deux écoles de pensée radicalement différentes**

| Aspect | Analyse Fondamentale | Analyse Technique |
|---|---|---|
| Question centrale | Combien vaut réellement cet actif ? | Où va aller le prix demain ? |
| Données utilisées | Bilans, compte de résultat, marché, économie | Prix, volume, patterns graphiques |
| Horizon temporel | Long terme (mois à années) | Court à moyen terme (jours à mois) |
| Outils | PER, PBR, EV/EBITDA, DCF, analyse sectorielle | SMA, RSI, MACD, Bollinger, Fibonacci |
| Hypothèse centrale | Le marché finit par corriger vers la valeur intrinsèque | Le prix reflète tout, les patterns se répètent |
| Représentants | Warren Buffett, Benjamin Graham | Jesse Livermore, traders haute fréquence |

**Analyse Fondamentale — Ratios clés :**

| Ratio | Formule | Interprétation |
|---|---|---|
| PER | Prix / Bénéfice par action | Cher si élevé (> 25), bon marché si faible (< 15) |
| PBR | Prix / Actif Net par action | < 1 = action décotée, > 3 = premium élevé |
| ROE | Bénéfice net / Fonds propres | > 15% = entreprise rentable |
| Marge nette | Bénéfice net / Chiffre d'affaires | Plus c'est élevé, mieux c'est |
| Dette/EBITDA | Dette financière nette / EBITDA | < 3x = endettement raisonnable |

**TradeDesk utilise l'analyse technique**, car :
1. Elle est plus adaptée aux données de marché disponibles (prix, volume)
2. Elle permet une prise de décision algorithmique objective
3. Elle est parfaitement complémentaire avec le machine learning

**En pratique**, les meilleurs traders combinent les deux :
l'analyse fondamentale pour *sélectionner* les actifs, et l'analyse technique pour *timer* les entrées/sorties.
""")

    with st.expander("Chapitre 5 — Les Options Financières en Détail", expanded=False):
        st.markdown("""
**Définition**

Une option financière est un **contrat dérivé** qui donne à l'acheteur le droit (mais pas l'obligation)
d'acheter (Call) ou de vendre (Put) un actif sous-jacent à un prix convenu (Strike),
avant ou à une date d'échéance donnée.

**Les deux positions fondamentales :**

| | Achat (Long) | Vente (Short) |
|---|---|---|
| **Call** | Droit d'acheter au Strike — parie sur la hausse | Obligation de vendre au Strike — parie sur la stagnation/baisse |
| **Put** | Droit de vendre au Strike — parie sur la baisse | Obligation d'acheter au Strike — parie sur la stagnation/hausse |

**Le profil de gain/perte :**

*Long Call (achat de Call) :*
- Perte maximale = Prime payée (si l'option expire sans valeur)
- Gain potentiel = Illimité (si le sous-jacent monte)
- Point mort = Strike + Prime

*Long Put (achat de Put) :*
- Perte maximale = Prime payée
- Gain maximum = Strike − Prime (si l'actif tombe à 0)
- Point mort = Strike − Prime

**Le modèle Black-Scholes (1973) :**

Formule de pricing d'une option européenne Call :
```
C = S × N(d1) − K × e^{-rT} × N(d2)

d1 = [ln(S/K) + (r + σ²/2) × T] / (σ × √T)
d2 = d1 − σ × √T

Où :
- N() = fonction de répartition de la loi normale
- S = prix actuel du sous-jacent
- K = strike price
- r = taux sans risque
- T = maturité (en années)
- σ = volatilité annualisée
```

**Vocabulaire des options :**

| Terme | Condition | Valeur intrinsèque |
|---|---|---|
| ITM (In The Money) | Call : S > K / Put : S < K | Positive |
| ATM (At The Money) | S ≈ K | ≈ 0 |
| OTM (Out of The Money) | Call : S < K / Put : S > K | 0 |

**Usages pratiques des options :**
1. **Spéculation avec effet de levier** : une option coûte moins cher qu'une action mais offre une exposition similaire
2. **Couverture (hedging)** : acheter des Puts pour protéger un portefeuille d'actions contre une baisse
3. **Génération de revenus** : vendre des Calls couverts sur des actions détenues
""")

    with st.expander("Chapitre 6 — La Simulation de Monte-Carlo et la Finance Quantitative", expanded=False):
        st.markdown("""
**La Finance Quantitative**

La finance quantitative (ou "quant") applique des **modèles mathématiques et statistiques avancés**
aux marchés financiers. Elle est utilisée par les hedge funds, banques d'investissement et gestionnaires d'actifs.

**Le Mouvement Brownien Géométrique (MBG)**

Le MBG est le modèle de base pour simuler l'évolution des prix d'actifs financiers.

**Équation différentielle stochastique :**
```
dS_t = μ × S_t × dt + σ × S_t × dW_t

Où :
- dS_t = variation du prix
- μ = dérive (rendement moyen espéré par unité de temps)
- σ = volatilité
- dW_t = increment brownien (choc aléatoire gaussien)
- dt = petit incrément de temps
```

**Solution discrète pour simulation :**
```
S_{t+1} = S_t × exp[(μ - σ²/2) × Δt + σ × √Δt × ε]

Où ε ~ N(0,1) (nombre aléatoire tiré d'une loi normale standard)
```

**La Simulation de Monte-Carlo**

Le principe : simuler des **milliers de trajectoires possibles** du prix en tirant des nombres aléatoires
selon le MBG, puis analyser la distribution des résultats.

**Étapes :**
1. Estimer μ et σ à partir de l'historique
2. Générer N trajectoires (ex: 1 000 à 10 000) sur l'horizon voulu
3. Pour chaque trajectoire, calculer la valeur finale du portefeuille
4. Analyser la distribution des valeurs finales :
   - Valeur médiane (50e percentile)
   - Valeur au pire cas (5e percentile = Value at Risk)
   - Valeur dans le meilleur scénario (95e percentile)

**Limites du modèle :**
- Suppose des rendements normalement distribués (faux : fat tails en réalité)
- μ et σ sont estimés sur le passé et ne sont pas stables
- Ne capture pas les sauts brusques (krachs soudains)
- Extensions : modèles de Heston (volatilité stochastique), Jump-Diffusion de Merton
""")

#TAB 5 — GLOSSAIRE
with tab_glossaire:
    st.header("Glossaire Financier")
    st.write("Retrouvez ici la définition rapide de tous les termes utilisés sur TradeDesk.")

    glossaire = {
        "Action (Share)": "Titre de propriété représentant une fraction du capital d'une entreprise cotée en bourse.",
        "Alpha": "Surperformance d'une stratégie par rapport à son benchmark (marché). Alpha > 0 = la stratégie bat le marché.",
        "ATM (At The Money)": "Option dont le Strike est égal ou proche du prix actuel du sous-jacent.",
        "Backtesting": "Simulation d'une stratégie de trading sur des données historiques pour évaluer sa performance passée.",
        "Bêta (β)": "Mesure de la sensibilité d'un actif aux fluctuations du marché de référence. β > 1 = plus volatile que le marché.",
        "Bollinger (Bandes de)": "Enveloppe dynamique autour de la SMA(20) à ±2 écarts-types. Représente ~95% des prix 'normaux'.",
        "Call": "Option d'achat donnant le droit d'acheter un actif au prix d'exercice (Strike). Parie sur la hausse.",
        "Candlestick": "Graphique en chandeliers japonais résumant ouverture, clôture, plus haut et plus bas d'une période.",
        "Commission": "Frais de transaction prélevés lors de chaque ordre. Sur TradeDesk : 1% du montant brut.",
        "Corrélation": "Mesure statistique de la relation entre deux séries de prix (de -1 à +1).",
        "Coupon": "Intérêt versé par une obligation à son détenteur à intervalles réguliers.",
        "Death Cross": "Croisement baissier : la SMA20 passe sous la SMA50. Signal de tendance baissière.",
        "Dérivé (Produit)": "Instrument financier dont la valeur dépend d'un actif sous-jacent (option, future, swap...).",
        "Diversification": "Répartition d'un portefeuille sur des actifs peu corrélés pour réduire le risque total.",
        "Dividende": "Part des bénéfices annuels reversée par une entreprise à ses actionnaires.",
        "Drawdown": "Perte en % depuis le dernier sommet historique d'un portefeuille ou d'un actif.",
        "EBITDA": "Earnings Before Interest, Taxes, Depreciation & Amortization. Mesure la rentabilité opérationnelle brute.",
        "ETF": "Exchange Traded Fund. Fonds indiciel coté répliquant la performance d'un indice boursier.",
        "Feature Engineering": "Création de variables explicatives à partir de données brutes pour alimenter un modèle ML.",
        "Gamma (Γ)": "Taux de variation du Delta par rapport au prix du sous-jacent. Mesure la courbure de la position en options.",
        "Golden Cross": "Croisement haussier : la SMA20 passe au-dessus de la SMA50. Signal de tendance haussière.",
        "Greeks": "Lettres grecques mesurant la sensibilité du prix d'une option à ses paramètres (Δ, Γ, ν, Θ, ρ).",
        "Grid Search": "Optimisation exhaustive testant toutes les combinaisons de paramètres pour trouver la meilleure configuration.",
        "Hedging (Couverture)": "Stratégie visant à réduire le risque d'un portefeuille via des positions compensatoires (ex: achat de Puts).",
        "Indice boursier": "Panier d'actions représentant un marché ou un secteur (S&P 500, CAC 40, Nasdaq...)",
        "ITM (In The Money)": "Option avec valeur intrinsèque > 0. Call ITM si S > K. Put ITM si S < K.",
        "Kurtosis": "Mesure des queues de distribution. > 3 = événements extrêmes plus fréquents que la normale.",
        "Levier (Effet de)": "Amplification des gains ET des pertes par rapport au capital investi. Risque élevé.",
        "Liquidité": "Facilité à acheter/vendre un actif rapidement sans impacter significativement son prix.",
        "MACD": "Moving Average Convergence Divergence. Indicateur de momentum basé sur deux moyennes mobiles exponentielles.",
        "Maturité": "Date d'expiration d'une option ou d'une obligation. Aussi appelée échéance.",
        "Monte-Carlo": "Méthode de simulation générant des milliers de scénarios probabilistes pour estimer des distributions futures.",
        "OTM (Out of The Money)": "Option sans valeur intrinsèque. Call OTM si S < K. Put OTM si S > K.",
        "Overfitting": "Sur-apprentissage : un modèle trop bien adapté aux données historiques perd sa capacité de généralisation.",
        "PAMP": "Prix d'Achat Moyen Pondéré. Prix de revient moyen d'une position construite en plusieurs fois.",
        "PER": "Price-to-Earnings Ratio. Prix de l'action / Bénéfice par action. Mesure la cherté relative d'une action.",
        "Prime": "Prix payé pour acquérir une option. Calculé par Black-Scholes sur TradeDesk.",
        "Put": "Option de vente donnant le droit de vendre un actif au Strike. Parie sur la baisse ou sert de couverture.",
        "Random Forest": "Algorithme ML d'ensemble combinant de nombreux arbres de décision pour une prédiction robuste.",
        "Rendement": "Gain total sur un investissement : (Prix final - Prix initial) / Prix initial × 100.",
        "Rho (ρ)": "Sensibilité du prix d'une option à une variation du taux sans risque.",
        "ROI": "Return on Investment. Rendement en % d'un investissement par rapport à son coût.",
        "RSI": "Relative Strength Index. Oscillateur mesurant la force des mouvements (0 à 100). < 30 : survente. > 70 : surachat.",
        "Sharpe (Ratio de)": "Rendement ajusté au risque. = Rendement / Volatilité. > 1 = bon investissement.",
        "Skewness": "Asymétrie de la distribution des rendements. Négatif = risque de krach soudain.",
        "SMA": "Simple Moving Average. Moyenne mobile simple sur N périodes. Lisse le bruit des prix.",
        "Strike (Prix d'exercice)": "Prix auquel le détenteur d'une option peut acheter (Call) ou vendre (Put) l'actif sous-jacent.",
        "Theta (Θ)": "Sensibilité du prix d'une option au passage du temps. Toujours négatif pour l'acheteur.",
        "Vega (ν)": "Sensibilité du prix d'une option à la volatilité implicite.",
        "Volatilité": "Amplitude des variations de prix annualisée. Mesure le risque statistique d'un actif.",
        "VWAP": "Volume Weighted Average Price. Prix moyen pondéré par les volumes. Référence des traders institutionnels.",
    }

    search_term = st.text_input("Rechercher un terme...", placeholder="ex: RSI, Sharpe, option...")

    filtered = {k: v for k, v in sorted(glossaire.items()) if search_term.lower() in k.lower() or search_term.lower() in v.lower()} if search_term else glossaire

    if not filtered:
        st.info(f"Aucun terme trouvé pour '{search_term}'.")
    else:
        for term, definition in filtered.items():
            with st.expander(term, expanded=False):
                st.markdown(definition)

    st.markdown(f"*{len(filtered)} terme(s) affiché(s) sur {len(glossaire)} au total.*")
