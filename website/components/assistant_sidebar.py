import streamlit as st
import random
import re
import difflib

KNOWLEDGE_BASE = {
    # ── Produits financiers ───────────────────────────────────────────────────
    "action": (
        "Une **action** est un titre de propriété représentant une fraction d'une entreprise. "
        "Elle confère un droit aux dividendes, au vote en assemblée et à une part des actifs en cas de liquidation. "
        "Son rendement provient des dividendes **et** de la plus-value (variation du cours). "
        "Sur TradeDesk, tu peux acheter/vendre des actions dans l'onglet **Portefeuille**."
    ),
    "etf": (
        "Un **ETF** (Exchange Traded Fund) est un fonds indiciel coté qui réplique la performance d'un indice "
        "(ex : S&P 500, CAC 40). Il permet de diversifier à faible coût avec une seule transaction. "
        "Les ETF combinent les avantages des actions (liquidité, cotation continue) et des fonds (diversification). "
        "Un ETF S&P 500 comme SPY vous donne une exposition à 500 entreprises américaines en une seule ligne."
    ),
    "option": (
        "Une **option** est un contrat dérivé qui donne le droit — mais pas l'obligation — "
        "d'acheter (Call) ou de vendre (Put) un actif à un prix prédéfini (Strike) avant une date d'échéance. "
        "Le prix de l'option est la **prime**. En cas d'expiration sans exercice, la prime est perdue. "
        "TradeDesk propose le pricing d'options via Black-Scholes dans l'onglet **Dérivés**."
    ),
    "call": (
        "Un **Call** est une option d'achat : il prend de la valeur quand le cours du sous-jacent monte. "
        "Vous payez une prime pour le droit d'acheter à un prix fixé (Strike). "
        "Si le cours dépasse le Strike à l'échéance, le Call est *dans la monnaie* (In The Money). "
        "Stratégie haussière typique. Risque limité à la prime, gain potentiellement illimité."
    ),
    "put": (
        "Un **Put** est une option de vente : il prend de la valeur quand le cours baisse. "
        "Utilisé comme assurance contre un krach (hedging) ou pour spéculer à la baisse. "
        "Le Put est rentable quand le cours tombe sous le Strike moins la prime payée. "
        "Risque limité à la prime, gain limité à Strike - 0."
    ),
    "dividende": (
        "Un **dividende** est la fraction des bénéfices distribués aux actionnaires, "
        "généralement de façon trimestrielle (US) ou annuelle (Europe). "
        "Le **taux de distribution (payout ratio)** = dividendes / bénéfice net. "
        "Le **rendement du dividende** = dividende annuel / cours actuel. "
        "Attention : un dividende très élevé peut signaler une entreprise en difficulté."
    ),
    "bitcoin": (
        "Le **Bitcoin (BTC)** est la première cryptomonnaie décentralisée (créée en 2009 par Satoshi Nakamoto). "
        "Offre limitée à 21 millions d'unités. Très volatile : historiquement > 60 % de volatilité annualisée. "
        "Sur TradeDesk, coté en USD. Le prix affiché inclut la conversion EUR/USD en temps réel. "
        "À utiliser dans la catégorie **Cryptomonnaie** du Portefeuille."
    ),
    "crypto": (
        "Les **cryptomonnaies** sont des actifs numériques décentralisés (Bitcoin, Ethereum, Solana…). "
        "Très volatiles et spéculatifs (corrections de -50 % à -90 % possibles). "
        "Cotées en USD sur TradeDesk avec conversion EUR/USD automatique. "
        "Disponibles dans la catégorie **Cryptomonnaie** de l'onglet Portefeuille. "
        "Ne jamais y investir plus que ce que vous êtes prêt à perdre totalement."
    ),
    "ethereum": (
        "**Ethereum (ETH)** est la deuxième cryptomonnaie par capitalisation. "
        "Sa blockchain supporte les **smart contracts** et les applications DeFi. "
        "Moins rare que Bitcoin (pas de limite fixe), mais brûlage de tokens depuis EIP-1559. "
        "Volatilité historique ~80 % annualisée. Coté en USD sur TradeDesk."
    ),
    "indice": (
        "Un **indice boursier** est un panier pondéré d'actifs représentant un marché ou secteur. "
        "Exemples : **CAC 40** (40 plus grandes françaises), **S&P 500** (500 plus grandes américaines), "
        "**Nasdaq** (tech US), **Nikkei 225** (Japon). "
        "Ils servent de référence (benchmark) pour évaluer une performance. "
        "On y investit via des ETF qui répliquent leur composition."
    ),
    "obligation": (
        "Une **obligation** est un titre de créance émis par un État ou une entreprise. "
        "Elle verse un intérêt fixe (le **coupon**) puis rembourse le capital à l'échéance. "
        "Moins risquée qu'une action, mais sensible aux taux d'intérêt : "
        "quand les taux montent, le cours des obligations baisse. "
        "Le spread de crédit mesure le risque de défaut de l'émetteur."
    ),

    # ── Indicateurs techniques ────────────────────────────────────────────────
    "rsi": (
        "Le **RSI** (Relative Strength Index) oscille entre 0 et 100. "
        "< 30 = survente (signal d'achat potentiel) · > 70 = surachat (signal de vente potentiel). "
        "Calculé sur 14 périodes par défaut. Le Bot TradeDesk utilise des seuils de 35/65. "
        "Attention aux *divergences* : un RSI qui monte alors que le cours baisse est souvent un signal de retournement."
    ),
    "sma": (
        "La **SMA** (Simple Moving Average – Moyenne Mobile Simple) calcule la moyenne des N derniers cours. "
        "Le croisement SMA courte / SMA longue (Golden Cross : SMA50 passe au-dessus de SMA200) est un signal haussier. "
        "Death Cross (SMA50 passe en-dessous de SMA200) = signal baissier. "
        "Visible sur le graphique Historique et utilisable comme stratégie dans le Bot."
    ),
    "ema": (
        "La **EMA** (Exponential Moving Average – Moyenne Mobile Exponentielle) pondère davantage les données récentes. "
        "Réagit plus vite que la SMA aux changements de tendance. "
        "Utilisée dans le calcul du MACD (EMA12 - EMA26). "
        "Préférée par de nombreux traders pour les signaux d'entrée/sortie."
    ),
    "vwap": (
        "Le **VWAP** (Volume Weighted Average Price) est le prix moyen pondéré par les volumes. "
        "Référence des traders institutionnels pour évaluer si un ordre a été bien exécuté. "
        "Si le cours est sous le VWAP → l'actif est bon marché par rapport à la journée. "
        "Disponible sur les graphiques Temps Réel et comme stratégie dans le Bot TradeDesk."
    ),
    "bollinger": (
        "Les **Bandes de Bollinger** encadrent le cours à ±2 écarts-types de la SMA(20). "
        "Cours proche de la bande haute → surévalué à court terme (vente potentielle). "
        "Proche de la bande basse → sous-évalué (achat potentiel). "
        "Le rétrécissement des bandes (*squeeze*) précède souvent une forte variation de cours. "
        "Visibles sur le graphique Historique de TradeDesk."
    ),
    "macd": (
        "Le **MACD** (Moving Average Convergence Divergence) = EMA12 − EMA26. "
        "La **ligne de signal** est l'EMA9 du MACD. "
        "Quand le MACD croise sa ligne de signal par le haut → signal haussier. "
        "L'**histogramme** représente l'écart MACD − Signal. "
        "Indicateur de momentum particulièrement utile pour confirmer une tendance."
    ),
    "sharpe": (
        "Le **Ratio de Sharpe** = (Rendement − Taux sans risque) / Volatilité. "
        "Il mesure la rentabilité **ajustée au risque**. "
        "< 0 = stratégie moins bonne qu'un livret · ≥ 1 = bon · ≥ 2 = excellent · ≥ 3 = exceptionnel. "
        "Affiché dans l'onglet **Statistiques** du Marché et dans le Backtesting."
    ),
    "volatilite": (
        "La **volatilité** mesure l'amplitude des variations de prix, annualisée (× √252 pour les actions, × √365 pour les cryptos). "
        "Actions tech : 20–35 % · Indices : 10–20 % · Cryptos : 60–100 %+. "
        "Une volatilité élevée amplifie les gains ET les pertes. "
        "Elle est utilisée comme paramètre clé dans le pricing des options (Black-Scholes)."
    ),
    "beta": (
        "Le **Bêta (β)** mesure la sensibilité d'un actif par rapport au marché (S&P 500). "
        "β = 1 → l'actif suit le marché · β > 1 → plus volatile (amplifie) · β < 1 → défensif. "
        "Exemples : Tesla β ≈ 2, Utilities β ≈ 0.4. "
        "Calculé dans l'onglet **Statistiques** du Marché. "
        "Dans un portefeuille, le β agrégé indique le risque systématique total."
    ),
    "drawdown": (
        "Le **drawdown** mesure la baisse depuis un sommet. "
        "Le **Max Drawdown** (MDD) est la pire perte historique pic-à-creux. "
        "Ex : MDD de −50 % signifie que le capital a été divisé par 2 à un moment. "
        "Pour récupérer un drawdown de −50 %, il faut +100 % de gain ! "
        "Affiché dans l'onglet **Backtesting** de TradeDesk."
    ),
    "per": (
        "Le **PER** (Price-to-Earnings Ratio) = Prix / Bénéfice par action. "
        "PER < 15 = potentiellement sous-évalué · 15–25 = normal · > 30 = cher (croissance intégrée). "
        "À comparer au PER sectoriel moyen. "
        "Attention : un PER bas peut refléter des difficultés, un PER élevé une forte croissance attendue."
    ),
    "skewness": (
        "Le **Skewness** mesure l'asymétrie de la distribution des rendements. "
        "Skewness négatif = queue gauche épaisse → risque de krach soudain (actions, cryptos). "
        "Skewness positif = rallyes fréquents. "
        "La loi normale a un skewness de 0 — les actifs réels s'en écartent souvent. "
        "Affiché dans l'onglet **Statistiques** du Marché."
    ),
    "kurtosis": (
        "Le **Kurtosis** mesure l'épaisseur des queues de distribution. "
        "Loi normale : kurtosis = 3 (ou 0 en excess kurtosis). "
        "> 3 = *leptokurtique* : chocs extrêmes plus fréquents que prévu (fat tails). "
        "Les actions et cryptos ont souvent un kurtosis élevé, ce qui rend la VaR gaussienne trompeuse. "
        "Affiché dans l'onglet **Statistiques**."
    ),

    # ── Concepts de trading ───────────────────────────────────────────────────
    "rendement": (
        "Le **rendement** = (Prix final − Prix initial + dividendes) / Prix initial × 100. "
        "Le rendement annualisé = (1 + R)^(1/n) − 1 (avec n = nombre d'années). "
        "Le rendement total = rendement en capital + rendement sur dividendes. "
        "Pour comparer des stratégies, utilisez toujours le rendement **annualisé ajusté du risque** (Sharpe)."
    ),
    "risque": (
        "Le **risque** financier comprend : "
        "1) Risque de marché (variation des cours) · "
        "2) Risque de crédit (défaut de l'émetteur) · "
        "3) Risque de liquidité (impossibilité de vendre) · "
        "4) Risque opérationnel (erreurs, fraudes). "
        "La diversification réduit le risque **non-systématique** (spécifique), "
        "mais pas le risque **systématique** (marché). Le Bêta mesure ce dernier."
    ),
    "diversification": (
        "La **diversification** = répartir les investissements sur des actifs décorrélés. "
        "Elle réduit le risque spécifique sans sacrifier le rendement espéré. "
        "Règle pratique : 15–20 titres dans des secteurs différents suffisent à éliminer ~90 % du risque idiosyncratique. "
        "Markowitz (1952) a formalisé cela : c'est le seul 'repas gratuit' de la finance."
    ),
    "stop loss": (
        "Un **stop loss** est un ordre de vente automatique déclenché si le cours passe sous un seuil. "
        "Il limite les pertes en cas de retournement brutal. "
        "Exemple : achat à 100 €, stop loss à 92 € → perte maximale de 8 %. "
        "Ne pas placer le stop trop près (bruit du marché) ni trop loin (perte trop importante). "
        "Le trailing stop loss suit le cours à la hausse automatiquement."
    ),
    "leverage": (
        "L'**effet de levier** (leverage) amplifie gains ET pertes par un coefficient. "
        "Levier ×2 : 10 % de gain → 20 % effectif, mais 10 % de perte → 20 %. "
        "Avec un levier ×10, une baisse de 10 % efface tout le capital ! "
        "Réservé aux traders expérimentés avec une gestion stricte du risque. "
        "Non disponible directement sur TradeDesk (paper trading sans levier)."
    ),
    "backtesting": (
        "Le **Backtesting** teste une stratégie sur des données historiques réelles. "
        "Il simule les décisions passées pour estimer si la stratégie aurait été rentable. "
        "Attention au **sur-apprentissage** (overfitting) : une stratégie trop optimisée sur le passé "
        "peut échouer en conditions réelles. "
        "TradeDesk propose SMA, RSI et VWAP dans l'onglet **Backtesting** avec métriques complètes."
    ),
    "monte carlo": (
        "La **Simulation de Monte-Carlo** génère des milliers de scénarios probabilistes "
        "pour estimer l'évolution future d'un portefeuille. "
        "Elle repose sur la dérive (rendement moyen) et la volatilité historiques. "
        "Le résultat est une fourchette de valeurs probables à horizon T, "
        "avec intervalles de confiance (5e–95e percentile). "
        "Disponible dans l'onglet **Portefeuille** de TradeDesk."
    ),
    "black scholes": (
        "Le modèle **Black-Scholes** (1973) calcule le prix théorique d'une option européenne. "
        "Paramètres : S (sous-jacent), K (strike), T (maturité), σ (volatilité), r (taux sans risque). "
        "La formule donne aussi les **Greeks** : Delta, Gamma, Theta, Vega, Rho. "
        "Hypothèses simplificatrices : volatilité constante, marché efficace, pas de dividendes. "
        "Disponible dans l'onglet **Dérivés** de TradeDesk."
    ),
    "alpha": (
        "L'**Alpha (α)** mesure la surperformance d'une stratégie vs son benchmark (Buy & Hold). "
        "α > 0 % → la stratégie bat le marché · α < 0 % → elle fait moins bien. "
        "Il faut distinguer l'alpha réel (surperformance après coûts et ajustement du risque) "
        "de l'alpha apparent (chance sur une période courte). "
        "Affiché dans l'onglet **Backtesting** de TradeDesk."
    ),
    "grid search": (
        "Le **Grid Search** teste toutes les combinaisons de paramètres d'une stratégie "
        "pour trouver les réglages optimaux historiquement. "
        "Exemple : tester SMA avec toutes les paires (courte 5–50, longue 10–200). "
        "TradeDesk utilise un moteur C++ pour l'exécuter très rapidement. "
        "Disponible dans l'onglet **Backtesting** via le bouton d'optimisation."
    ),
    "value at risk": (
        "La **VaR** (Value at Risk) est la perte maximale sur un horizon donné pour un niveau de confiance. "
        "Ex : VaR 95 % à 1 jour = 5 000 € → 95 % de chances de perdre moins de 5 000 € demain. "
        "La VaR **paramétrique** suppose la normalité (dangereuse car fat tails). "
        "La **CVaR** (Expected Shortfall) mesure la perte moyenne au-delà de la VaR."
    ),
    "pea": (
        "Le **PEA** (Plan d'Épargne en Actions) est une enveloppe fiscale française. "
        "Avantage : après 5 ans de détention, plus-values et dividendes exonérés d'impôt sur le revenu (mais CSG/CRDS maintenues). "
        "Plafond : 150 000 € de versements. "
        "Réservé aux actions européennes et ETF éligibles."
    ),
    "assurance vie": (
        "L'**assurance-vie** est le placement préféré des Français. "
        "Deux compartiments : fonds euros (capital garanti, ~2–3 %) et unités de compte (risqué). "
        "Avantages fiscaux après 8 ans (abattement 4 600 €/9 200 € pour un couple). "
        "Aussi un outil de transmission patrimoniale (hors succession jusqu'à 152 500 €/bénéficiaire)."
    ),

    # ── Pages de l'application ────────────────────────────────────────────────
    "marché": (
        "L'onglet **Marché** offre 6 sous-onglets : "
        "Temps Réel (cours + RSI), Historique (chandeliers, Bollinger), "
        "Volatilité & Volume, Statistiques (Sharpe, Bêta, Skewness), "
        "Rendements (distribution), Corrélation (heatmap). "
        "Nouveau : sélecteur de date personnalisé quand la période est '1d', "
        "et affichage EUR/USD pour les actifs cotés en dollars."
    ),
    "portefeuille": (
        "L'onglet **Portefeuille** permet de gérer tes investissements fictifs. "
        "3 types d'instruments : Action/ETF, Cryptomonnaie, Option (Call/Put). "
        "Conversion EUR/USD automatique pour les actifs US et cryptos. "
        "Nouveau : **multi-portefeuilles** — crée plusieurs portefeuilles avec des stratégies différentes ! "
        "Commission de 1 % sur chaque transaction."
    ),
    "backtest": (
        "L'onglet **Backtesting** simule tes stratégies sur des données historiques. "
        "3 stratégies disponibles : SMA (croisement de moyennes), RSI (surachat/survente), VWAP. "
        "Métriques : rendement, Max Drawdown, nombre d'ordres, Alpha vs Buy & Hold. "
        "Le Grid Search optimise automatiquement les paramètres."
    ),
    "bot": (
        "Le **Bot de Trading** propose 4 stratégies : "
        "SMA (croisement), RSI (surachat/survente), VWAP (prix institutionnel), "
        "et Machine Learning (Random Forest). "
        "Il génère un rapport narratif complet avant d'agir. "
        "Le bot ne passe jamais d'ordre sans ta validation explicite."
    ),
    "dérivés": (
        "L'onglet **Dérivés** permet de pricer des options Call/Put avec Black-Scholes. "
        "Tu peux visualiser la surface 3D du prix en fonction du Strike et de la Maturité. "
        "Les Greeks (Delta, Gamma, Theta, Vega, Rho) sont calculés automatiquement. "
        "Paramètres : sous-jacent, Strike, maturité (1–12 mois), taux sans risque."
    ),
    "assistant": (
        "L'onglet **Assistant** (cette page !) est ton conseiller financier personnel TradeDesk. "
        "Il peut expliquer des concepts, analyser ton portefeuille, calculer des formules, "
        "et te recommander des actifs basé sur le Ratio de Sharpe en temps réel. "
        "Pose tes questions librement !"
    ),
    "documentation": (
        "L'onglet **Documentation** contient le guide complet : "
        "Mode d'emploi, Comprendre les graphiques, Stratégies & Indicateurs, "
        "Cours de Finance (6 chapitres), et Glossaire (60+ termes). "
        "C'est la référence à consulter pour maîtriser TradeDesk et la finance."
    ),

    # ── Indices ───────────────────────────────────────────────────────────────
    "cac40": (
        "Le **CAC 40** est l'indice des 40 plus grandes entreprises françaises cotées à Euronext Paris. "
        "Calculé depuis 1987, pondéré par flottant boursier. "
        "Principales valeurs : LVMH, TotalEnergies, Sanofi, L'Oréal, Airbus. "
        "Accessible via TradeDesk : chercher 'CAC 40 Index'."
    ),
    "nasdaq": (
        "Le **Nasdaq Composite** regroupe toutes les entreprises cotées sur le Nasdaq (~3 000 valeurs). "
        "Le **Nasdaq 100** concentre les 100 plus grandes hors finance. "
        "Dominé par Apple, Microsoft, Nvidia, Amazon, Meta. "
        "Très corrélé aux taux d'intérêt (duration longue des valorisations tech). "
        "Performant à long terme mais avec des corrections violentes (-80 % en 2000)."
    ),
    "sp500": (
        "Le **S&P 500** est l'indice des 500 plus grandes entreprises américaines pondéré par capitalisation. "
        "Considéré comme le meilleur baromètre de l'économie américaine. "
        "Rendement annuel moyen historique : ~10 % brut, ~7 % après inflation. "
        "Un investissement régulier sur un ETF S&P 500 bat 90 % des fonds actifs sur 20 ans."
    ),

    # ── Macroéconomie ──────────────────────────────────────────────────────────
    "inflation": (
        "L'**inflation** est la hausse générale des prix, mesurée par l'IPC (Indice des Prix à la Consommation). "
        "Elle érode le pouvoir d'achat et la valeur réelle des obligations à taux fixe. "
        "Les actions et l'immobilier sont traditionnellement de bons protège contre l'inflation à long terme. "
        "La BCE cible 2 % d'inflation dans la zone euro."
    ),
    "taux": (
        "Les **taux d'intérêt** fixés par les banques centrales (BCE, Fed) influencent tous les actifs. "
        "Hausse des taux → obligations moins attractives, valorisations tech baissent, crédit plus cher. "
        "Baisse des taux → effets inverses, favorable aux actions de croissance. "
        "Le taux sans risque (OAT 10 ans, T-Bond US) sert de référence dans Black-Scholes."
    ),
}

ALL_TOPICS = [
    "ETF", "Dividende", "PER", "CAC 40", "Nasdaq", "S&P 500", "Bitcoin", "RSI", "SMA", "VWAP",
    "Sharpe", "Volatilité", "Bollinger", "Alpha", "Drawdown", "Inflation", "Taux", "VaR",
    "MACD", "Beta", "Monte Carlo", "Black-Scholes"
]


def generate_response(query: str, p) -> str:
    q = query.lower().strip()

    # ── 1. Calculs mathématiques ──────────────────────────────────────────────
    math_match = re.search(r"(\d+(?:[.,]\d+)?)\s*([\+\-\*/xX%])\s*(\d+(?:[.,]\d+)?)", q)
    if math_match:
        try:
            v1_str = math_match.group(1).replace(",", ".")
            v2_str = math_match.group(3).replace(",", ".")
            v1, op, v2 = float(v1_str), math_match.group(2).lower(), float(v2_str)
            if op == "+":               res = v1 + v2
            elif op == "-":             res = v1 - v2
            elif op in ["*", "x"]:      res = v1 * v2; op = "×"
            elif op == "/":             res = (v1 / v2) if v2 != 0 else "∞"; op = "÷"
            elif op == "%":             res = (v1 * v2) / 100; op = "% de"
            return f"🔢 **{v1} {op} {v2}** = **{res}**"
        except Exception:
            pass

    # ── 2. Taux de change EUR/USD ─────────────────────────────────────────────
    if any(w in q for w in ["eur/usd", "eurusd", "euro dollar", "taux de change", "conversion", "dollar"]):
        try:
            import data.data as data_mod
            rate = data_mod.get_eurusd_rate()
            return (
                f"💱 **Taux EUR/USD en temps réel** : **1 € = {rate:.4f} $**\n\n"
                f"Inversement : **1 $ = {1/rate:.4f} €**\n\n"
                f"TradeDesk applique ce taux automatiquement pour convertir les actifs cotés en USD "
                f"(actions US, cryptomonnaies) en euros dans le Portefeuille et le Marché."
            )
        except Exception:
            return "💱 Taux EUR/USD actuel : environ **1.08** (impossible de récupérer le cours en temps réel)."

    # ── 3. Recommandations d'achat ────────────────────────────────────────────
    conseil_triggers = [
        "meilleur action", "meilleure action", "quoi acheter", "recommandation",
        "conseil", "acheter quoi", "meilleur investissement", "que acheter",
        "meilleure crypto", "meilleur etf"
    ]
    if any(t in q for t in conseil_triggers):
        is_crypto = "crypto" in q
        try:
            import data.data as data_mod
            if is_crypto:
                top_picks = list(data_mod.CRYPTO_ASSETS)[:6]
                label = "cryptomonnaies"
            else:
                top_picks = [
                    "Apple Inc.", "Nvidia", "Microsoft", "Amazon",
                    "Tesla, Inc.", "Meta Platforms", "Alphabet Inc. (Class A)"
                ]
                label = "valeurs suivies"
            best_sharpe = -999.0
            best_asset = None
            for asset in top_picks:
                try:
                    df = data_mod.recuperer_historique(asset, "1y", "1d")
                    if not df.empty and len(df) > 50:
                        ret = df["Close"].pct_change().dropna()
                        s_ratio = (ret.mean() / (ret.std() + 1e-9)) * (252 ** 0.5)
                        if s_ratio > best_sharpe:
                            best_sharpe = s_ratio
                            best_asset = asset
                except Exception:
                    continue
            if best_asset:
                return (
                    f"📊 D'après le **Ratio de Sharpe** actuel (rendement ajusté au risque), "
                    f"**{best_asset}** offre la meilleure performance parmi les {label} "
                    f"(Sharpe = **{best_sharpe:.2f}**).\n\n"
                    f"⚠️ Ce n'est pas un conseil financier personnel — diversifie toujours tes investissements ! "
                    f"Utilise l'onglet **Statistiques** du Marché pour comparer les Sharpe de chaque actif."
                )
        except Exception:
            pass
        return (
            "📊 **Nvidia** et **Apple** affichent d'excellentes statistiques quantitatives récentes. "
            "Pour les cryptos, **Bitcoin** reste la plus établie en termes de Ratio de Sharpe. "
            "Utilise l'onglet **Statistiques** du Marché pour comparer en temps réel."
        )

    # ── 4. Info portefeuille ──────────────────────────────────────────────────
    portfolio_triggers = [
        "portefeuille", "solde", "liquidité", "cash", "gain", "perte",
        "performance", "positions", "combien", "mon capital"
    ]
    if any(w in q for w in portfolio_triggers):
        total_value = p.cash
        for t, info in p.positions.items():
            total_value += info["quantity"] * info["avg_price"]
        perf = ((total_value - p.initial_cash) / p.initial_cash) * 100
        nb_pos = len(p.positions)
        nb_tx = len(p.transactions)

        # Répartition par type
        nb_crypto = sum(1 for t in p.positions if "USD" in t or "-USD" in t.split("_")[0] if "_" not in t)
        nb_options = sum(1 for t in p.positions if "_" in t)
        nb_stocks = nb_pos - nb_crypto - nb_options

        perf_emoji = "📈" if perf >= 0 else "📉"
        return (
            f"💼 **Ton Portefeuille**\n\n"
            f"- 💵 Liquidités : **{p.cash:,.2f} €**\n"
            f"- 📦 Positions ouvertes : **{nb_pos}** actif(s)\n"
            f"  - Actions/ETF : {nb_stocks} · Cryptos : {nb_crypto} · Options : {nb_options}\n"
            f"- 💰 Valeur estimée : **{total_value:,.2f} €**\n"
            f"- {perf_emoji} Performance : **{perf:+.2f}%** ({total_value - p.initial_cash:+,.2f} €)\n"
            f"- 📋 Transactions : **{nb_tx}** au total\n\n"
            f"Pour le détail complet, consulte l'onglet **Portefeuille**."
        )

    # ── 5. Aide contextuelle sur les onglets ──────────────────────────────────
    aide_triggers = ["comment", "aide", "comment faire", "comment utiliser", "c'est quoi", "c est quoi", "expliquer", "explique"]
    if any(t in q for t in aide_triggers):
        if "bot" in q:
            return (
                "🤖 **Utiliser le Bot** :\n"
                "1. Va dans l'onglet **Bot** (menu gauche)\n"
                "2. Choisis un actif et une stratégie (SMA / RSI / VWAP / ML)\n"
                "3. Clique sur **Analyser** → rapport complet généré\n"
                "4. Si signal ACHAT ou VENTE → bouton d'autorisation apparaît\n"
                "5. Tu valides ou non — le bot n'agit **jamais** sans ta permission !"
            )
        if "backtest" in q:
            return (
                "📊 **Utiliser le Backtesting** :\n"
                "1. Va dans l'onglet **Backtesting**\n"
                "2. Choisis actif, stratégie (SMA/RSI/VWAP) et période\n"
                "3. Ajuste les paramètres avec les sliders\n"
                "4. Clique sur **▶️ Lancer le Backtest**\n"
                "5. Lis l'Alpha : s'il est positif, ta stratégie bat le Buy & Hold !\n"
                "6. Utilise le Grid Search pour optimiser automatiquement les paramètres."
            )
        if "graphique" in q or "chart" in q:
            return (
                "📈 **Lire les graphiques** : Va dans l'onglet **Documentation** → "
                "**📊 Comprendre les Graphiques** pour une explication détaillée de chaque chart "
                "avec tableaux, formules et exemples pratiques."
            )
        if "crypto" in q:
            return (
                "₿ **Acheter des cryptos** :\n"
                "1. Va dans l'onglet **Portefeuille**\n"
                "2. Type d'instrument : **Cryptomonnaie**\n"
                "3. Sélectionne Bitcoin, Ethereum, Solana, etc.\n"
                "4. La quantité peut être fractionnaire (ex : 0.001 BTC)\n"
                "5. Le prix est converti automatiquement USD → EUR au taux en temps réel."
            )
        if "option" in q or "dérivé" in q:
            return (
                "📑 **Utiliser les Dérivés** :\n"
                "1. Onglet **Dérivés** pour pricer des options (Black-Scholes)\n"
                "2. Ou onglet **Portefeuille** → Type : Option (Call/Put) pour acheter\n"
                "3. Paramètres : Strike, Maturité, Type (Call haussier / Put baissier)\n"
                "4. La volatilité historique est calculée automatiquement."
            )
        if "portefeuille" in q or "portfolio" in q:
            return (
                "💼 **Gérer ton Portefeuille** :\n"
                "• **Nouveau portefeuille** : bouton '➕ Nouveau portefeuille' dans la sidebar\n"
                "• **Switcher** entre portefeuilles : menu déroulant en haut de la sidebar\n"
                "• **Acheter** : Passer un ordre → sélectionne l'actif → valider\n"
                "• **Vendre** : même onglet, radio 'Vente', choisir la position\n"
                "• **Renommer/Supprimer** un portefeuille : onglet **Paramètres** → Portefeuilles"
            )

    # ── 6. Base de connaissances (exact puis fuzzy) ───────────────────────────
    for k, v in KNOWLEDGE_BASE.items():
        if k in q:
            return f"💡 **{k.upper()}** :\n{v}"

    mots_cles = list(KNOWLEDGE_BASE.keys())
    for mot in q.split():
        if len(mot) > 3:
            matches = difflib.get_close_matches(mot, mots_cles, n=1, cutoff=0.72)
            if matches:
                k = matches[0]
                return f"💡 *(Tu voulais dire **'{k}'** ?)* \n**{k.upper()}** :\n{KNOWLEDGE_BASE[k]}"

    # ── 7. Réponse de secours avec suggestions ────────────────────────────────
    topic = random.choice(ALL_TOPICS)
    return (
        f"❓ Je n'ai pas bien compris ta question.\n\n"
        f"**Ce que je sais faire :**\n"
        f"- Expliquer un concept : *'C'est quoi le VWAP ?'*, *'Explique le Sharpe'*\n"
        f"- Guider sur un onglet : *'Comment utiliser le Bot ?'*, *'Comment acheter des cryptos ?'*\n"
        f"- Voir ton solde : *'Mon portefeuille'*, *'Combien j'ai ?'*\n"
        f"- Calculer : *'100 × 1.05'*, *'5% de 2000'*\n"
        f"- Conseiller : *'Quoi acheter ?'*, *'Meilleure crypto ?'*\n"
        f"- Taux de change : *'Taux EUR/USD'*, *'Combien vaut 1000 dollars en euros ?'*\n\n"
        f"💡 Essaie par exemple : *'C'est quoi le {topic} ?'*"
    )


def render_assistant():
    pass
