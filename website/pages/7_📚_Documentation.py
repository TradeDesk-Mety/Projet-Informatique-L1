import streamlit as st

st.set_page_config(
    page_title="📚 Documentation — FinanceBot Pro",
    page_icon="📚",
    layout="wide",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("📚 Documentation")
section = st.sidebar.selectbox(
    "Chapitre",
    [
        "📖 Mode d'Emploi Complet",
        "📐 Formules & Indicateurs",
        "🤖 Algorithmes du Bot",
        "📚 Cours de Finance — Les Bases",
    ],
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. MODE D'EMPLOI COMPLET
# ─────────────────────────────────────────────────────────────────────────────
if section == "📖 Mode d'Emploi Complet":
    st.title("📖 Mode d'Emploi Complet")
    st.markdown(
        """
> *Ce guide vous accompagne pas à pas dans la découverte et l'utilisation de la plateforme,
> du premier lancement jusqu'aux stratégies avancées.*
"""
    )

    # ── Présentation globale ──────────────────────────────────────────────
    st.header("🌐 Présentation Globale de la Plateforme")
    st.markdown(
        """
**FinanceBot Pro** est une plateforme d'analyse financière et de simulation boursière
conçue pour les investisseurs de tous niveaux. Elle réunit en un seul endroit :

| Module | Ce que vous pouvez faire |
|---|---|
| **Tableau de bord** | Visualiser l'évolution d'un portefeuille en temps réel |
| **Analyse de marché** | Explorer les cours historiques, tendances et volatilités |
| **Bot de trading** | Activer des stratégies automatiques basées sur des signaux |
| **Évaluation d'options** | Calculer le prix théorique d'une option financière |
| **Gestion de portefeuille** | Construire, diversifier et optimiser vos positions |

### À qui s'adresse cette plateforme ?
- 🎓 **Étudiants en finance** qui souhaitent mettre en pratique les cours théoriques.
- 💼 **Investisseurs particuliers** qui veulent analyser leurs décisions avant de les prendre.
- 🔍 **Curieux des marchés** qui désirent comprendre comment fonctionnent les outils des professionnels.

---
"""
    )

    # ── Premier lancement ─────────────────────────────────────────────────
    st.header("🚀 Premier Lancement — En 5 Minutes")
    st.markdown(
        """
### Étape 1 — Choisir un actif
Dans la barre latérale gauche, saisissez le **symbole boursier** de l'actif qui vous intéresse
(exemples : `AAPL` pour Apple, `MC.PA` pour LVMH, `^FCHI` pour le CAC 40).

### Étape 2 — Sélectionner la période
Choisissez la fenêtre temporelle souhaitée : **1 semaine**, **1 mois**, **6 mois**, **1 an** ou **5 ans**.
Plus la période est longue, plus les tendances de fond apparaissent clairement.

### Étape 3 — Explorer les graphiques
Les graphiques interactifs vous permettent de :
- **Survoler** un point pour afficher le cours exact ce jour-là.
- **Zoomer** en faisant glisser la souris sur une zone.
- **Comparer** plusieurs indicateurs simultanément (prix, volume, moyennes mobiles…).

### Étape 4 — Activer le Bot
Rendez-vous dans l'onglet **Bot de Trading**, sélectionnez une stratégie
(par exemple *Croisement de moyennes* ou *Intelligence artificielle*) et appuyez sur **Lancer la simulation**.
Le bot analyse les données historiques et vous affiche les signaux d'achat/vente qu'il aurait générés.

### Étape 5 — Interpréter les résultats
Chaque simulation présente :
- Le **rendement total** de la stratégie sur la période.
- Le **ratio de Sharpe** (performance ajustée du risque).
- Un **journal des transactions** détaillant chaque opération simulée.

---
"""
    )

    # ── Formules utilisées ────────────────────────────────────────────────
    st.header("📐 Les Indicateurs Clés — Vue d'Ensemble")
    st.markdown(
        """
La plateforme calcule automatiquement plusieurs indicateurs financiers professionnels.
Voici ce qu'ils signifient en pratique :

| Indicateur | Ce qu'il mesure | Comment l'interpréter |
|---|---|---|
| **Volatilité** | L'amplitude des variations de prix | Plus elle est haute, plus l'actif est risqué |
| **Ratio de Sharpe** | La performance par unité de risque | Au-dessus de 1 = bon ; au-dessus de 2 = excellent |
| **Bêta (β)** | La sensibilité par rapport au marché global | β > 1 : amplifie les mouvements du marché |
| **SMA / EMA** | Les moyennes mobiles des cours | Indiquent la tendance générale (hausse ou baisse) |
| **RSI** | La force relative du cours | < 30 = survendu (occasion d'achat) ; > 70 = suracheté |

---
"""
    )

    # ── Stratégies du bot ─────────────────────────────────────────────────
    st.header("🤖 Les Stratégies du Bot — Comment Ça Fonctionne ?")
    st.markdown(
        """
Le bot de trading utilise des **règles mathématiques et statistiques** pour détecter
des opportunités d'achat ou de vente. Voici les trois stratégies disponibles :

### 📈 Croisement de Moyennes Mobiles
Le bot observe l'évolution du cours moyen sur deux horizons de temps différents
(court terme vs. long terme). Lorsque la moyenne courte **dépasse** la moyenne longue,
c'est un signal haussier. Quand elle **passe en dessous**, c'est un signal baissier.

### 📊 Stratégie RSI
Le bot surveille si un actif est **suracheté** (beaucoup de gens ont déjà acheté)
ou **survendu** (beaucoup ont vendu). Dans le premier cas, il anticipe une correction
à la baisse ; dans le second, il anticipe un rebond à la hausse.

### 🧠 Intelligence Artificielle
Le bot apprend à partir de l'historique des cours pour **reconnaître des schémas répétitifs**.
En combinant de nombreux signaux simultanément, il prédit la direction probable du cours
pour les prochaines séances.

---
"""
    )

    # ── Conseils ─────────────────────────────────────────────────────────
    st.header("💡 Conseils d'Utilisation")
    st.info(
        "**Testez toujours en simulation avant d'investir réellement.** "
        "Les résultats passés ne garantissent pas les performances futures."
    )
    st.markdown(
        """
- 🔄 **Comparez plusieurs stratégies** sur la même période pour trouver la plus adaptée à votre profil.
- 📅 **Allongez la période d'analyse** pour éviter les faux signaux liés aux fluctuations journalières.
- 🎯 **Fixez-vous des objectifs clairs** : rendement cible, perte maximale acceptée, durée de détention.
- 📚 **Utilisez le Cours de Finance** (chapitre dédié) pour renforcer vos connaissances avant de décider.
"""
    )

# ─────────────────────────────────────────────────────────────────────────────
# 2. FORMULES & INDICATEURS
# ─────────────────────────────────────────────────────────────────────────────
elif section == "📐 Formules & Indicateurs":
    st.title("📐 Formules & Indicateurs Financiers")
    st.markdown(
        """
> *Cette section présente les modèles mathématiques utilisés par la plateforme.
> Chaque formule est accompagnée d'une explication en langage clair.*
"""
    )

    # ── Black-Scholes ─────────────────────────────────────────────────────
    st.header("🎯 Modèle de Black-Scholes")
    st.markdown(
        """
### À quoi ça sert ?
Black-Scholes est le modèle de référence mondial pour **évaluer le prix d'une option financière**.
Une option est un contrat qui vous donne le droit (mais non l'obligation) d'acheter ou de vendre
un actif à un prix fixé à l'avance.

### La formule
Pour une option **Call** (droit d'achat) :
"""
    )
    st.latex(r"C = S \cdot N(d_1) - K \cdot e^{-rT} \cdot N(d_2)")
    st.latex(
        r"d_1 = \frac{\ln\!\left(\frac{S}{K}\right) + \left(r + \frac{\sigma^2}{2}\right)T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}"
    )
    st.markdown(
        """
### Traduction en langage simple
| Symbole | Signification |
|---|---|
| **S** | Prix actuel de l'action |
| **K** | Prix d'exercice (prix auquel vous pouvez acheter) |
| **r** | Taux d'intérêt sans risque (ex. : taux des obligations d'État) |
| **T** | Durée restante avant l'expiration de l'option (en années) |
| **σ (sigma)** | Volatilité de l'action — son niveau d'agitation |
| **N(…)** | Probabilité statistique (entre 0 et 1) |

**En résumé :** plus une action est volatile et plus l'échéance est lointaine,
plus l'option est chère — car l'incertitude crée de la valeur pour l'acheteur.

---
"""
    )

    # ── Volatilité ────────────────────────────────────────────────────────
    st.header("📊 Volatilité Annualisée")
    st.markdown(
        """
### À quoi ça sert ?
La volatilité mesure **l'amplitude des variations de prix** d'un actif.
Un actif très volatil peut gagner ou perdre 5 % en une seule journée ;
un actif peu volatil fluctue lentement et régulièrement.

### La formule
"""
    )
    st.latex(r"\sigma_{annuelle} = \sigma_{journalière} \times \sqrt{252}")
    st.markdown(
        """
### Traduction en langage simple
- On calcule d'abord l'écart-type des variations journalières du cours
  (combien le prix bouge en moyenne chaque jour).
- On le multiplie par √252 car il y a environ **252 jours de bourse** dans une année.
- Le résultat s'exprime en **pourcentage annuel**.

**Exemple :** une volatilité de 20 % signifie que l'actif peut raisonnablement
évoluer de ±20 % sur une année. Une valeur > 40 % est généralement considérée comme très risquée.

---
"""
    )

    # ── Ratio de Sharpe ───────────────────────────────────────────────────
    st.header("⚖️ Ratio de Sharpe")
    st.markdown("### À quoi ça sert ?")
    st.markdown(
        """
Le ratio de Sharpe répond à une question simple : **est-ce que le rendement obtenu
justifie le risque pris ?** Deux portefeuilles peuvent afficher le même gain,
mais l'un l'a obtenu en prenant beaucoup plus de risques que l'autre.
"""
    )
    st.latex(r"S = \frac{R_p - R_f}{\sigma_p}")
    st.markdown(
        """
### Traduction en langage simple
| Symbole | Signification |
|---|---|
| **Rp** | Rendement de votre portefeuille |
| **Rf** | Rendement « sans risque » (ex. : livret d'épargne ou obligations d'État) |
| **σp** | Volatilité (risque) de votre portefeuille |

### Comment l'interpréter ?
| Valeur | Interprétation |
|---|---|
| < 0 | Stratégie perdante |
| 0 — 1 | Rendement ne compensant pas vraiment le risque |
| 1 — 2 | Bon équilibre risque/rendement |
| > 2 | Excellent — c'est rare sur le long terme |

---
"""
    )

    # ── Bêta ──────────────────────────────────────────────────────────────
    st.header("📡 Coefficient Bêta (β)")
    st.markdown("### À quoi ça sert ?")
    st.markdown(
        """
Le bêta mesure **la sensibilité d'un actif aux mouvements du marché global**.
Si le marché monte de 1 %, combien va monter votre action ?
"""
    )
    st.latex(r"\beta = \frac{\text{Cov}(R_i,\, R_m)}{\text{Var}(R_m)}")
    st.markdown(
        """
### Traduction en langage simple
| Valeur de β | Comportement de l'actif |
|---|---|
| **β = 1** | L'actif suit exactement le marché |
| **β > 1** | L'actif amplifie les mouvements (ex. : β = 1,5 → si marché +10 %, action +15 %) |
| **β < 1** | L'actif est moins sensible (ex. : valeurs défensives comme l'alimentaire) |
| **β < 0** | L'actif évolue en sens inverse du marché (ex. : l'or en période de crise) |

**Conseil :** un portefeuille bien diversifié tend naturellement vers β ≈ 1.
Pour réduire le risque global, privilégiez des actifs à faible bêta.

---
"""
    )

    st.success(
        "💡 **Astuce :** tous ces indicateurs sont calculés automatiquement par la plateforme "
        "dès que vous sélectionnez un actif. Vous n'avez rien à calculer manuellement !"
    )

# ─────────────────────────────────────────────────────────────────────────────
# 3. ALGORITHMES DU BOT
# ─────────────────────────────────────────────────────────────────────────────
elif section == "🤖 Algorithmes du Bot":
    st.title("🤖 Algorithmes du Bot de Trading")
    st.markdown(
        """
> *Le bot de trading repose sur trois stratégies distinctes. Cette section explique
> comment chacune fonctionne et ce que vous observez dans l'interface.*
"""
    )

    # ── SMA ───────────────────────────────────────────────────────────────
    st.header("📈 Stratégie 1 — Croisement de Moyennes Mobiles (SMA)")
    st.markdown(
        """
### Comment ça fonctionne ?
Une **moyenne mobile simple (SMA)** est la moyenne des cours de clôture sur une période donnée.
Elle « lisse » les fluctuations journalières pour révéler la tendance de fond.

Le bot surveille **deux moyennes simultanément** :
- Une **moyenne courte** (ex. : sur 20 jours) — réactive aux mouvements récents.
- Une **moyenne longue** (ex. : sur 50 jours) — reflète la tendance de fond.

### Quand le bot agit-il ?
| Signal | Condition | Action |
|---|---|---|
| 🟢 **Achat** | La moyenne courte croise la longue **par le haut** | Le bot achète |
| 🔴 **Vente** | La moyenne courte croise la longue **par le bas** | Le bot vend |

### Ce que vous voyez dans l'interface
Sur le graphique principal, deux courbes colorées apparaissent superposées au cours.
Les **points verts** ▲ indiquent un signal d'achat ; les **points rouges** ▼, un signal de vente.
Le tableau de résultats montre ensuite le rendement cumulé de cette stratégie.

### Dans quel contexte cette stratégie est-elle efficace ?
Elle fonctionne bien lorsque le marché présente des **tendances claires et prolongées** (marchés dits « directionnels »).
Elle génère de faux signaux sur des marchés qui oscillent sans direction (marchés « en range »).

---
"""
    )

    # ── RSI ───────────────────────────────────────────────────────────────
    st.header("📊 Stratégie 2 — Indice de Force Relative (RSI)")
    st.markdown(
        """
### Comment ça fonctionne ?
Le **RSI** (Relative Strength Index) mesure la **dynamique des variations de prix** sur une période.
Il répond à la question : *l'actif a-t-il trop monté ou trop baissé récemment ?*

La valeur du RSI oscille toujours entre **0 et 100** :
- Proche de **100** → l'actif a beaucoup monté → risque de correction.
- Proche de **0** → l'actif a beaucoup baissé → possible rebond à venir.

### Quand le bot agit-il ?
| Signal | Condition | Signification |
|---|---|---|
| 🟢 **Achat** | RSI passe **en dessous de 30** | L'actif est survendu — potentiel rebond |
| 🔴 **Vente** | RSI passe **au-dessus de 70** | L'actif est suracheté — potentielle correction |

### Ce que vous voyez dans l'interface
Un second graphique affiche la courbe du RSI avec deux lignes horizontales en pointillés :
- La ligne à **30** (zone de survente — fond vert).
- La ligne à **70** (zone de surachat — fond rouge).

Lorsque la courbe franchit ces seuils, le bot génère automatiquement un signal visible sur le graphique des cours.

### Dans quel contexte cette stratégie est-elle efficace ?
Le RSI est particulièrement utile sur des marchés **sans tendance marquée**, où les cours rebondissent
régulièrement entre des niveaux de support et de résistance.

---
"""
    )

    # ── Random Forest / IA ────────────────────────────────────────────────
    st.header("🧠 Stratégie 3 — Intelligence Artificielle (Forêt Aléatoire)")
    st.markdown(
        """
### Comment ça fonctionne ?
Cette stratégie utilise un algorithme d'**intelligence artificielle** qui a appris
à reconnaître des configurations de marché en analysant des milliers de situations historiques.

Concrètement, le modèle observe un grand nombre de signaux simultanément :
- L'évolution du cours sur différentes fenêtres temporelles.
- Les niveaux de volatilité récents.
- Les croisements de moyennes mobiles.
- Les niveaux du RSI.
- Et bien d'autres indicateurs combinés.

Il prédit ensuite si le cours a plus de chances de **monter ou de baisser** dans les prochaines séances.

### L'idée de la « Forêt Aléatoire »
Imaginez que vous demandez leur avis à **500 experts financiers indépendants**,
chacun ayant analysé des données légèrement différentes.
Vous suivez ensuite l'avis de la **majorité**. C'est exactement le principe :
500 « arbres de décision » votent, et le résultat est la direction prédite par le plus grand nombre.

### Ce que vous voyez dans l'interface
- Une **barre de confiance** indique le niveau de certitude du modèle (ex. : « Hausse probable à 73 % »).
- Le graphique affiche les signaux d'achat/vente avec une couleur distincte pour les identifier facilement.
- Le tableau de performance compare cette stratégie aux deux précédentes.

### Dans quel contexte cette stratégie est-elle efficace ?
L'IA s'adapte à différents contextes de marché. Elle est généralement plus robuste que les stratégies
simples sur des **marchés complexes ou très volatils**, mais nécessite des données historiques
suffisamment longues pour fournir des prédictions fiables.

---
"""
    )

    st.info(
        "💡 **Conseil :** lancez les trois stratégies sur la même période et comparez leurs "
        "performances. Il n'existe pas de stratégie universellement supérieure : tout dépend "
        "des conditions de marché du moment."
    )

# ─────────────────────────────────────────────────────────────────────────────
# 4. COURS DE FINANCE
# ─────────────────────────────────────────────────────────────────────────────
elif section == "📚 Cours de Finance — Les Bases":
    st.title("📚 Cours de Finance — Les Bases de l'Investissement")
    st.markdown(
        """
> *Ce chapitre est une introduction complète aux marchés financiers,
> rédigée pour les débutants. Aucune connaissance préalable n'est requise.*
"""
    )

    tabs = st.tabs(
        [
            "🏛️ La Bourse",
            "📊 Les Indices",
            "🔧 Produits Dérivés",
            "📏 Indicateurs Clés",
            "🗂️ Portefeuille",
            "⚠️ Erreurs à Éviter",
            "📖 Glossaire",
        ]
    )

    # ── Tab 1 : La Bourse ─────────────────────────────────────────────────
    with tabs[0]:
        st.header("🏛️ Les Bases de la Bourse")
        st.markdown(
            """
### Qu'est-ce qu'une action ?
Une **action** est une petite part de propriété d'une entreprise.
Lorsqu'une société a besoin d'argent pour se développer, elle peut décider de
**s'introduire en bourse** : elle divise sa valeur en millions de petits morceaux
(les actions) et les vend au public.

En achetant une action Apple, vous devenez littéralement **co-propriétaire** d'Apple,
à hauteur de votre investissement.

### Comment le prix d'une action évolue-t-il ?
Le prix est déterminé par **l'offre et la demande** :
- Si beaucoup d'investisseurs veulent acheter → le prix monte.
- Si beaucoup veulent vendre → le prix baisse.

Ce déséquilibre est lui-même influencé par :
- Les **résultats financiers** de l'entreprise (chiffre d'affaires, bénéfices…).
- Les **anticipations** sur l'avenir (lancement d'un nouveau produit, expansion…).
- Le **contexte économique global** (taux d'intérêt, inflation, récession…).
- La **psychologie collective** des investisseurs (peur, euphorie…).

### Comment fonctionne une transaction boursière ?
1. Un investisseur place un **ordre d'achat** (il indique combien d'actions il veut et à quel prix maximum).
2. De l'autre côté, un autre investisseur place un **ordre de vente**.
3. Lorsqu'un acheteur et un vendeur s'accordent sur un prix, la transaction est **exécutée en quelques millisecondes**.
4. Vous devenez propriétaire des actions, qui apparaissent dans votre **portefeuille**.

### Quand gagne-t-on de l'argent en bourse ?
Il y a deux façons de gagner de l'argent avec des actions :

| Source de gain | Explication |
|---|---|
| **Plus-value** | Vous achetez à 100 €, vous revendez à 130 € → gain de 30 € |
| **Dividende** | L'entreprise redistribue une partie de ses bénéfices à ses actionnaires chaque année |
"""
        )

    # ── Tab 2 : Les Indices ───────────────────────────────────────────────
    with tabs[1]:
        st.header("📊 Les Grands Indices Boursiers")
        st.markdown(
            """
### Qu'est-ce qu'un indice boursier ?
Un indice boursier est un **baromètre** qui mesure la santé générale d'un marché.
Il regroupe les cours de plusieurs actions majeures et les agrège en un seul chiffre.

Quand on dit « le CAC 40 a gagné 1 % aujourd'hui », cela signifie que les 40 plus grandes
entreprises françaises cotées ont, **en moyenne**, vu leur valeur augmenter de 1 %.

### Les principaux indices mondiaux

| Indice | Pays / Zone | Nombre de valeurs | Ce qu'il représente |
|---|---|---|---|
| **CAC 40** | 🇫🇷 France | 40 | Les 40 plus grandes capitalisations françaises |
| **S&P 500** | 🇺🇸 États-Unis | 500 | Les 500 plus grandes entreprises américaines |
| **NASDAQ 100** | 🇺🇸 États-Unis | 100 | Les 100 plus grandes valeurs technologiques américaines |
| **Dow Jones** | 🇺🇸 États-Unis | 30 | 30 « blue chips » américaines historiques |
| **DAX** | 🇩🇪 Allemagne | 40 | Les 40 leaders de l'économie allemande |
| **Nikkei 225** | 🇯🇵 Japon | 225 | Les 225 plus grandes sociétés japonaises |
| **FTSE 100** | 🇬🇧 Royaume-Uni | 100 | Les 100 premières capitalisations britanniques |

### Comment utiliser les indices en pratique ?
- **Comparer** : si votre portefeuille a gagné 5 % alors que le CAC 40 a gagné 8 %,
  vous avez **sous-performé** le marché.
- **Investir directement** : via des produits comme les ETF (voir l'onglet suivant),
  vous pouvez répliquer la performance d'un indice entier sans choisir les actions une par une.
- **Jauger l'économie** : un indice en forte hausse traduit généralement un optimisme
  économique généralisé ; une chute soudaine peut signaler une crise ou une incertitude majeure.
"""
        )

    # ── Tab 3 : Produits Dérivés ──────────────────────────────────────────
    with tabs[2]:
        st.header("🔧 Les Produits Dérivés et Instruments Modernes")
        st.markdown(
            """
### Les Options — Call et Put
Une **option** est un contrat qui vous donne le **droit** (mais pas l'obligation) d'acheter
ou de vendre un actif à un **prix fixé à l'avance**, avant une **date d'expiration**.

#### Option Call (droit d'achat)
Vous achetez une option Call sur Apple à 150 $. Si Apple monte à 200 $,
vous pouvez acheter à 150 $ et revendre à 200 $, empochant la différence.
Si Apple reste en dessous de 150 $, vous ne l'exercez pas — vous perdez seulement
la **prime** payée pour acquérir l'option.

#### Option Put (droit de vente)
C'est l'inverse : vous acquérez le droit de **vendre** à un prix fixé.
Utile pour **se protéger** contre une baisse ou pour parier sur une chute des marchés.

| Type | Pari | Gain si… | Perte maximale |
|---|---|---|---|
| **Call** | Hausse du cours | Le cours monte au-dessus du prix d'exercice | La prime payée |
| **Put** | Baisse du cours | Le cours descend sous le prix d'exercice | La prime payée |

---

### Les ETF — Fonds Indiciels Cotés
Un **ETF** (Exchange-Traded Fund) est un panier d'actions qui **réplique automatiquement
la performance d'un indice**. En achetant un ETF CAC 40, vous investissez instantanément
dans les 40 entreprises de l'indice, proportionnellement à leur poids.

**Avantages des ETF :**
- 💰 Diversification immédiate avec un seul titre.
- 📉 Frais très bas (souvent < 0,20 % par an).
- 🔄 Liquidité : ils s'achètent et se vendent comme des actions ordinaires.
- 🎯 Idéal pour les débutants qui veulent suivre le marché sans le « battre ».

---

### Les Futures — Contrats à Terme
Un **future** est un accord d'acheter ou de vendre un actif à un **prix fixé aujourd'hui**,
mais pour une **livraison dans le futur**. Très utilisés par les professionnels pour
se couvrir contre les fluctuations de prix (sur les matières premières, les devises, les indices…).

> ⚠️ Les futures impliquent un **effet de levier** important et sont réservés
> aux investisseurs expérimentés. Évitez-les si vous débutez.
"""
        )

    # ── Tab 4 : Indicateurs Clés ──────────────────────────────────────────
    with tabs[3]:
        st.header("📏 Les Indicateurs Clés pour Analyser une Action")
        st.markdown(
            """
### Le PER — Price-to-Earnings Ratio
Le **PER** (ou ratio cours/bénéfice) indique combien de fois les investisseurs
sont prêts à payer les bénéfices annuels de l'entreprise.

> **PER = Prix de l'action ÷ Bénéfice par action**

| PER | Interprétation habituelle |
|---|---|
| < 10 | Action potentiellement sous-évaluée (ou secteur en difficulté) |
| 10 — 20 | Zone de valorisation « normale » pour beaucoup de secteurs |
| > 25 | Forte croissance attendue (ou action chère — risque de déception) |

---

### Le Dividende et le Rendement
Le **dividende** est la part des bénéfices que l'entreprise reverse directement
à ses actionnaires, généralement une fois par an.

> **Rendement du dividende = Dividende annuel ÷ Prix de l'action × 100**

**Exemple :** une action à 100 € versant 4 € de dividende offre un **rendement de 4 %**.

---

### La Capitalisation Boursière
C'est la valeur totale de l'entreprise en bourse.

> **Capitalisation = Prix de l'action × Nombre total d'actions**

| Taille | Capitalisation | Exemples |
|---|---|---|
| **Grandes capitalisations** | > 10 milliards € | Total, L'Oréal, LVMH |
| **Moyennes capitalisations** | 1 — 10 milliards € | Valeurs mid-cap |
| **Petites capitalisations** | < 1 milliard € | Small caps (plus risquées, plus dynamiques) |

---

### Le Risque et la Volatilité
- **Volatilité élevée** = les prix varient beaucoup → potentiellement très rentable,
  mais aussi très risqué.
- **Volatilité faible** = cours stables → rassurant, mais rendements souvent modestes.
- La règle fondamentale : **plus un investissement promet de rendement, plus il comporte de risque**.
  Il n'existe pas de rendement élevé sans risque élevé.
"""
        )

    # ── Tab 5 : Gestion de portefeuille ───────────────────────────────────
    with tabs[4]:
        st.header("🗂️ Gestion de Portefeuille — Construire et Diversifier")
        st.markdown(
            """
### La Diversification — Ne pas mettre tous ses œufs dans le même panier
C'est le principe fondamental de la gestion de portefeuille :
**répartir ses investissements** sur plusieurs actifs, secteurs et zones géographiques
afin que la mauvaise performance de l'un ne compromette pas l'ensemble.

**Exemple de diversification :**

| Catégorie | Allocation suggérée pour un profil équilibré |
|---|---|
| Actions grandes capitalisations (Europe) | 25 % |
| Actions grandes capitalisations (USA) | 25 % |
| ETF marchés émergents | 10 % |
| Obligations d'État | 20 % |
| Immobilier coté (SCPI, REIT) | 10 % |
| Liquidités / Fonds monétaires | 10 % |

---

### L'Allocation d'Actifs — Adapter à son Profil
Votre allocation dépend de **votre profil de risque** et de **votre horizon de temps** :

| Profil | Caractéristique | Allocation type |
|---|---|---|
| **Prudent** | Peu d'appétit pour le risque, horizon court | 70 % obligations / 30 % actions |
| **Équilibré** | Tolérance modérée, horizon moyen (5-10 ans) | 50 % / 50 % |
| **Dynamique** | Bonne tolérance, horizon long (> 10 ans) | 80 % actions / 20 % sécurité |

---

### Le Rééquilibrage
Avec le temps, certains actifs prennent plus de poids que d'autres dans votre portefeuille.
Le **rééquilibrage** consiste à **revendre une partie des actifs** qui ont trop progressé
et à **racheter ceux** qui ont pris moins de poids, pour revenir à l'allocation cible.

> 📅 **Fréquence recommandée :** une fois par an, ou lorsqu'un actif dépasse de plus de 5 %
> son poids cible.

---

### L'Investissement Progressif (DCA)
Le **Dollar-Cost Averaging** (investissement régulier) consiste à investir un montant fixe
à intervalles réguliers (ex. : 100 € par mois), quelle que soit l'évolution du marché.

**Avantages :**
- Vous achetez plus d'actions quand les prix sont bas, moins quand ils sont hauts.
- Vous lissez votre prix d'achat moyen sur le long terme.
- Vous évitez d'essayer de « timer » le marché (stratégie rarement gagnante).
"""
        )

    # ── Tab 6 : Erreurs à Éviter ──────────────────────────────────────────
    with tabs[5]:
        st.header("⚠️ Les Erreurs Classiques des Débutants à Éviter")
        st.markdown(
            """
### ❌ Erreur n°1 — Investir de l'argent dont vous pourriez avoir besoin
La bourse peut baisser pendant des mois, voire des années. N'investissez que de l'argent
que vous pouvez vous permettre de ne pas toucher pendant **au moins 5 ans**.
Gardez toujours une épargne de sécurité (3 à 6 mois de dépenses) sur un compte liquide.

---

### ❌ Erreur n°2 — Suivre les conseils de la « foule »
Lorsqu'un ami vous dit « il faut acheter telle action, elle va exploser »,
le plus souvent ceux qui savaient l'ont déjà acheté — et le potentiel de hausse est déjà intégré dans le prix.
**Faites vos propres recherches** avant d'investir.

---

### ❌ Erreur n°3 — Vendre en panique lors d'une baisse
Les marchés baissent régulièrement. Depuis 1900, les marchés américains ont connu
des dizaines de crises sévères — et se sont à chaque fois redressés.
**Vendre en panique cristallise la perte.** Si votre analyse de départ est toujours valide, tenez bon.

---

### ❌ Erreur n°4 — Concentrer son portefeuille sur un seul actif
Mettre 100 % de son capital sur une seule action, même solide, est une prise de risque extrême.
Des entreprises autrefois considérées comme « sûres à 100 % » ont fait faillite (Enron, Lehman Brothers…).
**Diversifiez toujours.**

---

### ❌ Erreur n°5 — Ignorer les frais
Les frais de courtage, les frais de gestion des fonds et les impôts sur les plus-values
**s'accumulent et réduisent significativement votre rendement** sur le long terme.
Comparez toujours les frais avant de choisir un courtier ou un produit financier.

---

### ❌ Erreur n°6 — Chercher à « battre le marché » à court terme
Même les gérants professionnels n'y parviennent pas durablement.
Sur 10 ans, plus de **80 % des fonds actifs** sous-performent leur indice de référence.
Pour la plupart des investisseurs, une stratégie passive via des ETF est statistiquement supérieure.

---

### ❌ Erreur n°7 — Ne pas avoir de plan
Investir sans objectif précis mène souvent à des décisions émotionnelles.
Avant d'investir, définissez :
- 🎯 **Mon objectif** (retraite, achat immobilier, projet dans 10 ans…)
- ⏳ **Mon horizon** (combien d'années je peux attendre)
- 📉 **Ma tolérance au risque** (quelle perte je peux absorber sans paniquer)
"""
        )

    # ── Tab 7 : Glossaire ─────────────────────────────────────────────────
    with tabs[6]:
        st.header("📖 Glossaire des 20 Termes Essentiels")
        st.markdown(
            """
| Terme | Définition |
|---|---|
| **Action** | Part de propriété d'une entreprise cotée en bourse. |
| **Obligation** | Titre de dette : vous prêtez de l'argent à une entreprise ou un État, qui vous rembourse avec intérêts. |
| **Indice boursier** | Indicateur synthétique mesurant l'évolution d'un panier d'actions (ex. : CAC 40). |
| **ETF** | Fonds coté en bourse qui réplique la performance d'un indice à moindres frais. |
| **Dividende** | Part des bénéfices d'une entreprise redistribuée à ses actionnaires. |
| **Plus-value** | Gain réalisé lors de la revente d'un actif à un prix supérieur au prix d'achat. |
| **PER** | Ratio cours/bénéfice, mesure la cherté d'une action par rapport à ses profits. |
| **Capitalisation boursière** | Valeur totale d'une entreprise en bourse (prix × nombre d'actions). |
| **Volatilité** | Mesure de l'amplitude des variations de prix d'un actif. |
| **Ratio de Sharpe** | Indicateur de performance ajustée du risque. |
| **Bêta (β)** | Sensibilité d'un actif aux mouvements du marché global. |
| **Option** | Contrat donnant le droit d'acheter (Call) ou de vendre (Put) un actif à prix fixé. |
| **Future** | Contrat d'achat/vente d'un actif à un prix fixé aujourd'hui pour livraison future. |
| **Diversification** | Répartition des investissements sur plusieurs actifs pour réduire le risque global. |
| **Liquidité** | Facilité avec laquelle un actif peut être acheté ou vendu rapidement sans impact sur son prix. |
| **Support / Résistance** | Niveaux de prix où l'actif a tendance à rebondir (support) ou à bloquer (résistance). |
| **Analyse technique** | Étude des graphiques de cours pour anticiper les mouvements futurs. |
| **Analyse fondamentale** | Évaluation de la valeur réelle d'une entreprise via ses données financières. |
| **Effet de levier** | Utilisation de capitaux empruntés pour amplifier les gains (et les pertes). |
| **DCA** | Dollar-Cost Averaging : stratégie d'investissement régulier à montant fixe pour lisser le prix d'achat. |
"""
        )

        st.success(
            "🎓 **Vous connaissez maintenant les bases !** Explorez les autres chapitres "
            "de cette documentation pour approfondir vos connaissances et utiliser "
            "pleinement toutes les fonctionnalités de la plateforme."
        )
