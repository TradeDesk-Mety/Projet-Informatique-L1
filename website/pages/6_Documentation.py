import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui
set_global_ui()
render_assistant()

import streamlit as st

st.title("📚 Documentation & Apprentissage")
st.caption("Mode d'emploi complet de la plateforme, explication des graphiques et cours de finance interactif.")

tab_mode_emploi, tab_graphiques, tab_strategies, tab_cours = st.tabs([
    "📖 Mode d'Emploi",
    "📊 Comprendre les Graphiques",
    "🧮 Stratégies & Indicateurs",
    "🎓 Cours de Finance",
])

# ─────────────────────────────────────────────────────────────────────────────
with tab_mode_emploi:
    st.header("Mode d'Emploi de la Plateforme")

    with st.expander("1. Présentation Globale", expanded=True):
        st.markdown(
            "Bienvenue sur **TradeDesk**. Cette plateforme vous permet de simuler des investissements "
            "en conditions réelles, sans risquer de véritable capital.\n\n"
            "**Les grandes étapes :**\n"
            "1. Consultez l'onglet **Marché** pour analyser les cours en temps réel et historique.\n"
            "2. Passez des ordres dans l'onglet **Portefeuille** (achat/vente avec commission 1%).\n"
            "3. Laissez le **Bot** analyser le marché et vous proposer des décisions automatiques.\n"
            "4. Vérifiez vos stratégies via le **Backtesting** sur des données passées réelles.\n"
            "5. Pricez des **Options** avec le modèle Black-Scholes."
        )

    with st.expander("2. Onglet Marché", expanded=False):
        st.markdown(
            "L'onglet **Marché** est votre centre d'analyse.\n\n"
            "| Sous-onglet | Ce qu'il montre |\n"
            "|---|---|\n"
            "| ⚡ Temps Réel | Cours intraday 1 min avec VWAP et jauge RSI |\n"
            "| 📈 Historique | Chandeliers japonais + SMA20/50 + Bollinger |\n"
            "| 📊 Volatilité & Volume | Volatilité glissante + anomalies de volume |\n"
            "| 📐 Statistiques | Sharpe, Bêta, Skewness, Kurtosis |\n"
            "| 📉 Rendements | Distribution empirique vs loi normale |\n"
            "| 🔗 Corrélation | Matrice de corrélation entre actifs |"
        )

    with st.expander("3. Onglet Portefeuille", expanded=False):
        st.markdown(
            "C'est ici que vous gérez votre capital virtuel.\n\n"
            "- **Acheter** : Choisissez un actif, saisissez la quantité et validez. Une commission de **1%** est appliquée.\n"
            "- **Vendre** : Vous ne pouvez vendre que les actifs que vous possédez.\n"
            "- **Positions** : Suivez vos gains/pertes (G/P) latents. Les valeurs s'actualisent automatiquement.\n"
            "- **Simulation Monte-Carlo** : Projette des trajectoires probabilistes pour votre portefeuille."
        )

    with st.expander("4. Onglet Bot de Trading", expanded=False):
        st.markdown(
            "Le **Bot** est un assistant algorithmique qui analyse le marché à votre place.\n\n"
            "**4 stratégies disponibles :**\n"
            "- **SMA** : Achète si la moyenne court terme > long terme, vend sinon.\n"
            "- **RSI** : Achète en zone de survente (< 35), vend en surachat (> 65).\n"
            "- **VWAP** : Achète si le cours est >2% sous le prix moyen pondéré. C'est la référence institutionnelle.\n"
            "- **Machine Learning** : Random Forest entraîné en direct sur 1 an d'historique.\n\n"
            "Le bot vous produit un **rapport narratif complet** avant de vous demander d'autoriser l'ordre."
        )

    with st.expander("5. Onglet Backtesting", expanded=False):
        st.markdown(
            "Le **Backtesting** simule une stratégie sur des données historiques réelles.\n\n"
            "**Métriques clés affichées :**\n"
            "- **Rendement stratégie** : performance totale de l'algorithme sur la période.\n"
            "- **Buy & Hold** : référence passive (acheter et ne jamais vendre).\n"
            "- **Alpha** : surperformance vs le Buy & Hold. Si positif, la stratégie bat le marché.\n"
            "- **Max Drawdown** : pire chute depuis un sommet. Plus proche de 0%, mieux c'est.\n"
            "- **Nombre d'ordres** : chaque transaction coûte 1% de commission."
        )

# ─────────────────────────────────────────────────────────────────────────────
with tab_graphiques:
    st.header("📊 Comprendre les Graphiques de TradeDesk")
    st.info("Cette section vous explique en détail à quoi sert chaque graphique et comment le lire.")

    with st.expander("🕯️ Graphique en Chandeliers Japonais (Candlestick)", expanded=True):
        st.markdown("""
**À quoi ça sert ?** C'est LE graphique central de l'analyse technique. Il résume en un coup d'œil
toute l'action du marché sur une période (un jour, une heure, etc.).

**Comment le lire ?**

Chaque bougie représente une période et contient 4 informations essentielles :

| Élément | Signification |
|---|---|
| **Bas du corps** | Prix d'ouverture (si bougie verte) ou de clôture (si rouge) |
| **Haut du corps** | Prix de clôture (si verte) ou d'ouverture (si rouge) |
| **Mèche haute** | Plus haut atteint sur la période |
| **Mèche basse** | Plus bas atteint sur la période |

🟢 **Bougie verte** = le prix a **monté** sur la période (clôture > ouverture).  
🔴 **Bougie rouge** = le prix a **baissé** sur la période (clôture < ouverture).

**Les indicateurs superposés :**
- 🟠 **SMA 20** (orange) : Tendance court terme. Si le prix la croise à la hausse → signal haussier.
- 🔵 **SMA 50** (bleu) : Tendance moyen terme. Sert de support/résistance dynamique.
- ⬜ **Bandes de Bollinger** (gris, pointillé) : Zone de ±2 écarts-types autour de la SMA20.
  Un prix proche du bord supérieur = possiblement surévalué. Proche du bord inférieur = sous-évalué.
""")

    with st.expander("⚡ Graphique Temps Réel (Intraday 1 min) avec VWAP", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Suivre l'évolution du cours en temps réel au cours de la journée de trading.

**Comment le lire ?**
- La **ligne colorée** trace le cours minute par minute.
  - 🟢 Verte si le cours est au-dessus de l'ouverture, 🔴 rouge si en-dessous.
- La **ligne orange pointillée** est le **VWAP** (Volume Weighted Average Price).
  - Si le cours est **au-dessus du VWAP** → les acheteurs dominent la journée.
  - Si le cours est **en-dessous du VWAP** → les vendeurs dominent.
  - Le VWAP est la référence d'exécution des fonds d'investissement institutionnels.
- Les **barres de volume** en bas montrent l'intensité des échanges.
  Un volume élevé sur une hausse = signal fort et fiable.

**Ligne horizontale en pointillé** = prix actuel exact pour faciliter la lecture.
""")

    with st.expander("📉 Distribution des Rendements Journaliers", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Comprendre le comportement statistique d'un actif et évaluer son risque réel.

**Comment le lire ?**
- Chaque barre de l'**histogramme bleu** montre combien de jours l'actif a affiché ce niveau de rendement.
- La **courbe orange** est la distribution normale théorique (courbe en cloche).

**Ce que vous cherchez :**
- **Queues épaisses** (barres aux extrémités plus hautes que la courbe orange) → l'actif subit régulièrement des chocs extrêmes (krach ou rally). Indiqué par un **Kurtosis > 3**.
- **Asymétrie à gauche** (queue gauche plus longue) → risque de krach soudain. Indiqué par un **Skewness négatif**.
- **Centré sur 0%** avec queue droite légèrement plus longue → actif sain avec tendance à la hausse.

**Lignes de référence :**
- 🟢 **μ** : Rendement moyen journalier.
- 🔴 **±1σ** : Les rendements se situent dans cet intervalle ~68% du temps.
""")

    with st.expander("📊 Volatilité Historique Glissante", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Mesurer et visualiser l'évolution du risque d'un actif dans le temps.

**Comment le lire ?**
- L'axe Y représente la **volatilité annualisée en %**.
  - En dessous de **20%** : actif stable (type obligation ou grande capitalisation défensive).
  - Entre **20% et 40%** : volatilité normale pour une action tech.
  - Au-dessus de **40%** : actif très risqué (cryptomonnaies, petites capitalisations).
- Les **pics** correspondent à des périodes de stress de marché (crise, publication de résultats, événement géopolitique).
- Une volatilité **en hausse** = incertitude grandissante = risque accru.

**Formule** : `Vol = σ(rendements) × √252` (annualisée sur la base de 252 jours de trading/an).
""")

    with st.expander("📈 Analyse des Volumes & Breakouts", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Identifier les signaux forts en repérant les anomalies de volume.

**Règle d'or** : *Le volume confirme le prix.* Une hausse accompagnée d'un fort volume est fiable.
Une hausse sans volume est suspecte (possible fausse cassure).

**Code couleur des barres :**
- 🟢 **Vert** : Journée haussière (clôture > ouverture), volume normal.
- 🔴 **Rouge** : Journée baissière, volume normal.
- 🟡 **Jaune** : **Anomalie de volume** (> 2× la moyenne mobile). Signal fort à surveiller !

**Les deux lignes superposées :**
- 🔵 **Ligne bleue** (pointillé) = Moyenne Mobile du Volume (20j) : ligne de base "normale".
- 🟡 **Ligne jaune** (pointillé) = Seuil d'anomalie = 2× la moyenne. Toute barre qui dépasse ce niveau est une anomalie.
""")

    with st.expander("🔗 Matrice de Corrélation", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Comprendre comment les actifs de ton portefeuille évoluent ensemble.

**Comment lire la Heatmap ?**
- Chaque case indique la corrélation entre 2 actifs (valeur de **-1 à +1**).
- 🔴 **+1 (rouge)** : Les deux actifs évoluent exactement dans le même sens. Pas de diversification.
- ⬜ **0 (blanc)** : Aucune relation entre les deux actifs. Bonne diversification.
- 🔵 **-1 (bleu)** : Les actifs évoluent en sens opposés. Diversification parfaite.

**Conseil pratique :** Un portefeuille bien diversifié contient des actifs avec des corrélations proches de 0 ou négatives.
Par exemple, ajouter des obligations (bonds) à un portefeuille d'actions réduit la corrélation globale.

**Note :** La diagonale vaut toujours 1.0 (un actif est parfaitement corrélé à lui-même).
""")

    with st.expander("📐 Graphique Backtest : Equity Curve & Drawdown", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Évaluer la performance historique d'une stratégie algorithmique.

**Panneau supérieur — Equity Curve (Évolution du capital) :**
- 🟢 **Ligne verte** : Évolution du capital investi avec la stratégie.
- 🟠 **Ligne orange** (pointillé) : Stratégie passive Buy & Hold (acheter et conserver).
- Si la ligne verte est **au-dessus** de l'orange → la stratégie **bat le marché** (alpha positif).

**Panneau inférieur — Drawdown (Perte depuis le dernier sommet) :**
- Représente la perte en % depuis le pic de valeur le plus récent.
- **Toujours négatif ou nul** (une perte par rapport au sommet).
- Le **Max Drawdown** est le pire creux atteint. Ex: -25% signifie qu'à un moment, le capital a perdu 25% depuis son point haut.
- Un bon système de trading vise un Max Drawdown **< 20%**.
""")

    with st.expander("🌐 Surface 3D Black-Scholes (Options)", expanded=False):
        st.markdown("""
**À quoi ça sert ?** Visualiser comment le prix d'une option varie en fonction de deux paramètres simultanément.

**Les 3 axes :**
- **Axe X (Strike K)** : Le prix d'exercice de l'option. Plus il est éloigné du prix actuel (S), moins l'option vaut.
- **Axe Y (Maturité T)** : Temps restant avant l'échéance en années. Plus la maturité est longue, plus l'option est chère (car plus de temps = plus de chance que le marché bouge).
- **Axe Z (Prix de l'option)** : La valeur théorique calculée par Black-Scholes.

**Ce qu'on observe :**
- La surface est croissante avec la maturité (temps = valeur pour les options).
- La surface est en forme de "dôme" autour du prix actuel (options "à la monnaie" sont les plus sensibles).
- Les zones de couleur chaude = options chères, zones froides = options bon marché.

**Colorscale** : Viridis (Call) ou Plasma (Put).
""")

# ─────────────────────────────────────────────────────────────────────────────
with tab_strategies:
    st.header("🧮 Stratégies & Indicateurs Techniques")

    with st.expander("📈 SMA — Moyenne Mobile Simple", expanded=True):
        st.markdown("""
**Définition** : La SMA (Simple Moving Average) calcule la moyenne arithmétique des `n` derniers prix de clôture.

**Formule** : `SMA(n) = (P₁ + P₂ + ... + Pₙ) / n`

**Utilisation sur TradeDesk :**
- **Bot SMA** : Croisement SMA(5) / SMA(15). Achat si SMA courte > SMA longue, vente sinon.
- **Graphique Marché** : SMA(20) et SMA(50) affichées sur le graphique en chandeliers.

**Avantages** : Simple, robuste, filtre le bruit des prix.  
**Limites** : Indicateur retardé (lagging), génère des faux signaux dans les marchés latéraux.
""")

    with st.expander("⚡ RSI — Relative Strength Index", expanded=False):
        st.markdown("""
**Définition** : Oscillateur mesurant la vitesse et l'amplitude des mouvements de prix. Borné entre 0 et 100.

**Formule** :
```
RSI = 100 - (100 / (1 + RS))
RS  = Moyenne(hausses sur n jours) / Moyenne(baisses sur n jours)
```

**Zones d'interprétation :**
| Valeur RSI | Interprétation | Signal |
|---|---|---|
| < 30 | Survente excessive | 🟢 Potentiel achat (rebond attendu) |
| 30 – 70 | Zone neutre | ⏸️ Attendre |
| > 70 | Surachat excessif | 🔴 Potentiel vente (correction attendue) |

**Sur TradeDesk** : Le bot RSI utilise des seuils de 35/65 (légèrement plus conservateurs que le standard 30/70).
""")

    with st.expander("💧 VWAP — Volume Weighted Average Price", expanded=False):
        st.markdown("""
**Définition** : Prix moyen pondéré par le volume d'échanges. C'est **LA référence** des traders institutionnels.

**Formule** :
```
Prix Typique  = (High + Low + Close) / 3
VWAP = Σ(Prix_Typique × Volume) / Σ(Volume)
```

**Pourquoi c'est important ?**
Le VWAP représente le prix "juste" du marché pour une journée donnée, en tenant compte de chaque
transaction et de son poids en volume. Si votre ordre est exécuté **sous le VWAP**, vous avez
obtenu un meilleur prix que la moyenne du marché.

**Signaux sur TradeDesk :**
- **Cours < VWAP - 2%** → L'actif est bon marché par rapport au consensus → Signal d'**ACHAT**.
- **Cours > VWAP + 2%** → L'actif est cher par rapport au consensus → Signal de **VENTE**.
- **Dans la bande ±2%** → Prix équitable → **NEUTRE**, on attend.

**Différence intraday vs glissant** :
- Sur le graphique Temps Réel, le VWAP est calculé depuis l'ouverture (reset chaque jour).
- Dans le Bot et le Backtesting, on utilise un VWAP glissant sur 20 jours.
""")

    with st.expander("🤖 Machine Learning — Random Forest", expanded=False):
        st.markdown("""
**Définition** : Algorithme d'intelligence artificielle qui apprend des patterns historiques pour prédire
la direction du marché à 3 jours.

**Étapes du modèle :**

1. **Feature Engineering** : On crée des variables explicatives :
   - `ret1`, `ret3`, `ret5` : Rendements à 1, 3 et 5 jours (dynamique récente)
   - `sma_ratio` : SMA(5)/SMA(15) — capte la tendance
   - `rsi` : Mesure le momentum
   - `vol10` : Volatilité sur 10 jours — mesure l'incertitude actuelle

2. **Variable cible** : Est-ce que le cours sera plus haut dans 3 jours ? (1=Oui, 0=Non)

3. **Entraînement** : Un Random Forest de 50 arbres, profondeur max 5, est entraîné sur 1 an d'historique.
   Une **calibration Platt Scaling** ajuste les probabilités pour qu'elles soient fiables.

4. **Décision** :
   - Probabilité de hausse > 55% → **ACHAT**
   - Probabilité de hausse < 45% → **VENTE**
   - Entre 45% et 55% → **NEUTRE** (incertitude trop haute, on n'agit pas)

**Validation** : Une cross-validation 5-Folds vérifie l'absence d'overfitting.
""")

    with st.expander("📉 Bandes de Bollinger", expanded=False):
        st.markdown("""
**Définition** : Enveloppe dynamique autour de la SMA(20) à ±2 écarts-types.

**Formule** :
```
Bande supérieure = SMA(20) + 2 × σ(20)
Bande inférieure = SMA(20) - 2 × σ(20)
```

**Interprétation :**
- Prix proche de la **bande supérieure** → Surévaluation à court terme, possible retournement.
- Prix proche de la **bande inférieure** → Sous-évaluation à court terme, possible rebond.
- Bandes **rétrécies** (faible volatilité) → Une explosion de volatilité est souvent imminente.
- Bandes **écartées** (forte volatilité) → Le marché est en mode panique ou euphorie.
""")

    with st.expander("📐 Ratio de Sharpe", expanded=False):
        st.markdown("""
**Définition** : Mesure de la rentabilité ajustée au risque. C'est l'indicateur de performance ultime.

**Formule** :
```
Sharpe = (Rendement annualisé − Taux sans risque) / Volatilité annualisée
```
*(Le taux sans risque est approximé à 0% sur TradeDesk pour simplifier.)*

**Interprétation :**
| Ratio de Sharpe | Qualité de l'investissement |
|---|---|
| < 0 | Perd de l'argent après ajustement au risque ❌ |
| 0 – 0.5 | Médiocre |
| 0.5 – 1.0 | Acceptable |
| 1.0 – 2.0 | Bon ✅ |
| > 2.0 | Excellent, rare en pratique 🏆 |
""")

# ─────────────────────────────────────────────────────────────────────────────
with tab_cours:
    st.header("Les Bases de la Finance et de l'Investissement")
    st.write("Ce mini-cours vous donnera toutes les clés pour comprendre les marchés financiers avant d'investir virtuellement.")

    st.subheader("1. Qu'est-ce qu'une Action ?")
    st.markdown(
        "Une **action** représente une fraction du capital d'une entreprise. En l'achetant, vous devenez actionnaire.\n"
        "- **Plus-value** : Si l'entreprise se développe, l'action prend de la valeur.\n"
        "- **Dividendes** : Certaines entreprises reversent une partie de leurs bénéfices aux actionnaires.\n"
        "- **Risque** : Si l'entreprise fait faillite, l'action peut perdre toute sa valeur."
    )

    st.subheader("2. Le Risque et la Volatilité")
    st.markdown(
        "Sur les marchés financiers, **le risque et le rendement sont liés**. "
        "Plus un actif peut vous rapporter gros, plus il risque de vous faire perdre de l'argent.\n"
        "- La **volatilité** mesure l'instabilité du cours. Une cryptomonnaie a une forte volatilité (> 60%).\n"
        "- L'objectif d'un bon investisseur est d'**optimiser le rendement pour un niveau de risque donné** "
        "(c'est ce que mesure le Ratio de Sharpe).\n"
        "- La **diversification** (investir dans plusieurs actifs décorrélés) est le seul 'repas gratuit' de la finance."
    )

    st.subheader("3. Les Indices et les ETF")
    st.markdown(
        "- Un **Indice Boursier** (comme le CAC 40 ou le S&P 500) regroupe les plus grandes entreprises d'un marché.\n"
        "- Un **ETF** (Exchange Traded Fund) est un 'panier' d'actions qui copie exactement un indice. "
        "Acheter un ETF S&P 500 revient à investir dans les 500 plus grandes entreprises américaines d'un coup. "
        "C'est idéal pour **diversifier** à faible coût."
    )

    st.subheader("4. Comment analyser le marché ?")
    st.markdown(
        "Il existe deux grandes écoles :\n"
        "1. **L'Analyse Fondamentale** : Étudier les bilans financiers, les projets de l'entreprise et l'économie "
        "mondiale pour déduire sa 'vraie' valeur intrinsèque.\n"
        "2. **L'Analyse Technique** : Étudier les graphiques et les mathématiques (RSI, SMA, VWAP, Bollinger) "
        "pour repérer des tendances psychologiques et des patterns récurrents — c'est ce que fait TradeDesk."
    )

    st.subheader("5. Les Options Financières")
    st.markdown(
        "Une **option** est un contrat donnant le **droit** (mais pas l'obligation) d'acheter ou de vendre un actif.\n"
        "- **Option Call** : Droit d'**acheter** à un prix fixé (Strike). Parie sur une hausse.\n"
        "- **Option Put** : Droit de **vendre** à un prix fixé. Parie sur une baisse ou sert de couverture.\n"
        "- **Prime** : Le prix payé pour obtenir ce droit, calculé par le modèle **Black-Scholes** (1973).\n\n"
        "⚠️ Les options sont des produits **à effet de levier** : elles peuvent expirer sans valeur (perte totale de la prime)."
    )
