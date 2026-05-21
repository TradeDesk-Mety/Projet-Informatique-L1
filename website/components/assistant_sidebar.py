import streamlit as st
import random
import re
import difflib

KNOWLEDGE_BASE = {
    # Produits financiers
    "action": "Une **action** est un titre de propriété représentant une fraction d'une entreprise. Elle donne droit aux dividendes et aux votes en assemblée.",
    "etf": "Un **ETF** (Exchange Traded Fund) est un fonds indiciel coté qui réplique la performance d'un indice (ex: S&P 500). Il permet de diversifier à faible coût.",
    "option": "Une **option** donne le droit (mais pas l'obligation) d'acheter (Call) ou de vendre (Put) un actif à un prix fixé (Strike) avant une date d'échéance.",
    "call": "Un **Call** est une option d'achat : il prend de la valeur quand le marché monte. Sur TradeDesk, tu peux pricer des Calls dans l'onglet Options.",
    "put": "Un **Put** est une option de vente : il prend de la valeur quand le marché baisse. Utilisé comme assurance (couverture) contre un krach.",
    "dividende": "Un **dividende** est la part des bénéfices reversée aux actionnaires, généralement annuellement ou trimestriellement.",
    "bitcoin": "Le **Bitcoin** est la première cryptomonnaie décentralisée (2009). Très volatile (> 60% annualisé). Disponible dans l'onglet Marché sur TradeDesk.",
    "crypto": "Les **cryptomonnaies** sont des actifs numériques décentralisés. Très volatiles et spéculatifs. TradeDesk inclut Bitcoin, Ethereum et Solana.",
    "indice": "Un **indice boursier** est un panier de valeurs (ex: CAC 40 = 40 plus grandes entreprises françaises, S&P 500 = 500 plus grandes américaines).",
    "obligation": "Une **obligation** est un titre de dette émis par un État ou une entreprise. Elle rapporte un intérêt fixe (coupon) et est moins risquée que l'action.",

    # Indicateurs techniques
    "rsi": "Le **RSI** (Relative Strength Index) oscille entre 0 et 100. En dessous de 30 = survente (signal d'achat potentiel). Au-dessus de 70 = surachat (signal de vente). Le Bot TradeDesk utilise des seuils de 35/65.",
    "sma": "La **SMA** (Moyenne Mobile Simple) lisse les prix sur une fenêtre de N jours. Le croisement SMA courte / SMA longue génère des signaux de trading. Visible sur le graphique Historique.",
    "vwap": "Le **VWAP** (Volume Weighted Average Price) est le prix moyen pondéré par les volumes. C'est la référence des traders institutionnels. Si le cours est sous le VWAP, l'actif est bon marché. Affiché sur le graphique Temps Réel et disponible comme stratégie dans le Bot.",
    "bollinger": "Les **Bandes de Bollinger** encadrent le cours à ±2 écarts-types de la SMA(20). Cours proche de la bande haute = surévalué. Proche de la bande basse = sous-évalué. Visibles sur le graphique Historique.",
    "macd": "Le **MACD** est un indicateur de momentum calculé comme la différence entre deux moyennes mobiles exponentielles (12j et 26j). Il génère des signaux quand il croise sa ligne de signal.",
    "sharpe": "Le **Ratio de Sharpe** = Rendement / Volatilité. Il mesure la rentabilité ajustée au risque. > 1 = bon, > 2 = excellent. Affiché dans l'onglet Statistiques du Marché.",
    "volatilite": "La **volatilité** mesure l'amplitude des variations de prix, annualisée (× √252). Une action tech tourne autour de 20-35%. Les cryptos dépassent souvent 60%. Plus la volatilité est haute, plus le risque est élevé.",
    "beta": "Le **Bêta (β)** mesure la sensibilité d'un actif par rapport au marché (S&P 500). β > 1 = plus risqué que le marché. β < 1 = plus défensif. Calculé dans l'onglet Statistiques.",
    "drawdown": "Le **drawdown** mesure la perte depuis un sommet. Le Max Drawdown est le pire creux historique. Ex: -30% signifie que le capital a perdu 30% depuis son pic. Affiché dans le Backtesting.",
    "per": "Le **PER** (Price-to-Earnings Ratio) = Prix de l'action / Bénéfice par action. Un PER élevé signifie que l'action est chère par rapport à ses bénéfices.",
    "skewness": "Le **Skewness** mesure l'asymétrie des rendements. Négatif = queue gauche épaisse = risque de krach soudain. Positif = rallyes fréquents. Affiché dans Statistiques.",
    "kurtosis": "Le **Kurtosis** mesure les queues de distribution. > 3 = l'actif connaît régulièrement des chocs extrêmes (bons ou mauvais) non prévus par la loi normale.",

    # Concepts de trading
    "rendement": "Le **rendement** est le pourcentage de gain sur un investissement : `(Prix final - Prix initial) / Prix initial × 100`.",
    "risque": "Le **risque** financier se mesure par la volatilité, le bêta et le drawdown. La diversification permet de réduire le risque sans sacrifier le rendement.",
    "diversification": "La **diversification** consiste à répartir les investissements sur des actifs décorrélés pour réduire le risque global. C'est le seul 'repas gratuit' de la finance selon Markowitz.",
    "stop loss": "Un **stop loss** est un ordre de vente automatique déclenché si le cours tombe sous un seuil prédéfini. Il limite les pertes en cas de retournement brutal.",
    "leverage": "Le **levier** (ou effet de levier) amplifie les gains ET les pertes. Un levier x2 double les gains mais double aussi les pertes. Très risqué pour les débutants.",
    "backtesting": "Le **Backtesting** teste une stratégie sur des données historiques réelles pour évaluer si elle aurait été rentable. Disponible dans l'onglet Backtesting de TradeDesk.",
    "monte carlo": "La **Simulation de Monte-Carlo** génère des milliers de scénarios probabilistes pour estimer l'évolution future possible d'un portefeuille. Basée sur la dérive et la volatilité historiques.",
    "black scholes": "Le modèle **Black-Scholes** (1973) calcule le prix théorique d'une option européenne à partir du prix actuel, du strike, de la maturité, de la volatilité et du taux sans risque. Disponible dans l'onglet Options.",
    "alpha": "L'**alpha** est la surperformance d'une stratégie par rapport au marché (Buy & Hold). Un alpha positif = la stratégie bat le marché. Affiché dans le Backtesting.",
    "grid search": "Le **Grid Search** est une technique d'optimisation qui teste toutes les combinaisons de paramètres possibles pour trouver les meilleurs réglages d'une stratégie. TradeDesk utilise un moteur C++ pour le faire très rapidement.",

    # Pages de l'application
    "marché": "L'onglet **Marché** affiche le cours en Temps Réel (VWAP, RSI), l'Historique (chandeliers, Bollinger), la Volatilité, les Statistiques (Sharpe, Bêta), la Distribution des rendements et la Corrélation.",
    "portefeuille": "L'onglet **Portefeuille** te permet d'acheter/vendre des actifs avec une commission de 1%, de suivre tes positions et G/P, et de lancer une Simulation de Monte-Carlo.",
    "backtest": "L'onglet **Backtesting** simule 3 stratégies (SMA, RSI, VWAP) sur des données historiques et affiche les métriques de performance : rendement, Max Drawdown, nombre d'ordres, alpha.",
    "bot": "Le **Bot de Trading** propose 4 stratégies : SMA (croisement de moyennes), RSI (surachat/survente), VWAP (prix institutionnel), et Machine Learning (Random Forest). Il génère un rapport narratif avant d'agir.",
    "options": "L'onglet **Options** permet de pricer des options Call/Put avec Black-Scholes et de visualiser une surface 3D du prix en fonction du Strike et de la Maturité.",
    "documentation": "L'onglet **Documentation** contient le mode d'emploi, l'explication détaillée de chaque graphique, la description de chaque stratégie et un cours de finance accéléré.",
    "achat": "Pour faire un **achat** : Portefeuille → sélectionne un actif → saisis la quantité → valide. Une commission de 1% est appliquée automatiquement.",
    "vente": "Pour **vendre** : Portefeuille → section Vendre → sélectionne l'actif → saisis la quantité. Tu ne peux vendre que les actifs que tu possèdes.",

    # Indices
    "cac40": "Le **CAC 40** est l'indice des 40 plus grandes entreprises françaises cotées à Euronext Paris. Il est calculé depuis 1987.",
    "nasdaq": "Le **Nasdaq** est l'indice technologique américain. Il regroupe des géants comme Apple, Microsoft, Nvidia et Amazon. Très corrélé aux taux d'intérêt.",
    "sp500": "Le **S&P 500** est l'indice des 500 plus grandes entreprises américaines. Il est considéré comme le meilleur baromètre de l'économie américaine.",
}

ALL_TOPICS = ["ETF", "Dividende", "PER", "CAC 40", "Nasdaq", "S&P 500", "Bitcoin", "RSI", "SMA", "VWAP", "Sharpe", "Volatilité", "Bollinger", "Alpha", "Drawdown"]

def generate_response(query: str, p) -> str:
    q = query.lower().strip()

    # 1. Calculs mathématiques
    math_match = re.search(r"(\d+(?:[.,]\d+)?)\s*([\+\-\*/xX%])\s*(\d+(?:[.,]\d+)?)", q)
    if math_match:
        try:
            v1_str = math_match.group(1).replace(",", ".")
            v2_str = math_match.group(3).replace(",", ".")
            v1, op, v2 = float(v1_str), math_match.group(2).lower(), float(v2_str)

            if op == "+":   res = v1 + v2
            elif op == "-": res = v1 - v2
            elif op in ["*", "x"]: res = v1 * v2; op = "×"
            elif op == "/":
                res = (v1 / v2) if v2 != 0 else "∞"; op = "÷"
            elif op == "%":
                res = (v1 * v2) / 100; op = "% de"
            return f"🔢 **{v1} {op} {v2}** = **{res}**"
        except: pass

    # 2. Recommandations d'achat
    conseil_triggers = ["meilleur action", "meilleure action", "quoi acheter", "recommandation", "conseil", "acheter quoi"]
    if any(t in q for t in conseil_triggers):
        try:
            import data.data as data_mod
            top_picks = ["Apple Inc.", "Nvidia", "Microsoft", "Amazon", "Tesla, Inc.", "Meta Platforms"]
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
                except: continue
            if best_asset:
                return (f"🤖 D'après le Ratio de Sharpe actuel, **{best_asset}** offre le meilleur "
                        f"rendement ajusté au risque parmi nos valeurs suivies (Sharpe = {best_sharpe:.2f}). "
                        f"Cela dit, ce n'est pas un conseil financier — diversifie toujours tes investissements !")
        except: pass
        return "🤖 **Nvidia** et **Apple** affichent d'excellentes statistiques quantitatives en ce moment. Utilise l'onglet **Statistiques** du Marché pour comparer le Sharpe de chaque actif."

    # 3. Info portefeuille
    portfolio_triggers = ["portefeuille", "solde", "liquidité", "cash", "gain", "perte", "performance", "positions", "combien"]
    if any(w in q for w in portfolio_triggers):
        total_value = p.cash
        for t, info in p.positions.items():
            total_value += info["quantity"] * info["avg_price"]
        perf = ((total_value - p.initial_cash) / p.initial_cash) * 100
        nb_pos = len(p.positions)
        return (f"💼 **Ton Portefeuille**\n"
                f"- 💵 Liquidités : **{p.cash:,.2f} €**\n"
                f"- 📦 Positions ouvertes : **{nb_pos}** actif(s)\n"
                f"- 💰 Valeur Totale : **{total_value:,.2f} €**\n"
                f"- 📈 Performance globale : **{perf:+.2f}%**")

    # 4. Aide contextuelle sur les onglets
    aide_triggers = ["comment", "aide", "comment faire", "comment utiliser", "expliquer", "c'est quoi", "c est quoi"]
    if any(t in q for t in aide_triggers):
        if "bot" in q:
            return ("🤖 **Utiliser le Bot** :\n"
                    "1. Va dans l'onglet **Bot** (menu gauche)\n"
                    "2. Choisis un actif et une stratégie (SMA / RSI / VWAP / ML)\n"
                    "3. Clique sur **Analyser** → le bot produit un rapport complet\n"
                    "4. Si le signal est ACHAT ou VENTE, un bouton d'autorisation apparaît\n"
                    "5. Tu valides ou non — le bot n'agit jamais sans ta permission !")
        if "backtest" in q:
            return ("📊 **Utiliser le Backtesting** :\n"
                    "1. Va dans l'onglet **Backtesting**\n"
                    "2. Choisis l'actif, la stratégie (SMA/RSI/VWAP) et la période\n"
                    "3. Ajuste les paramètres avec les sliders\n"
                    "4. Clique sur **▶️ Lancer le Backtest**\n"
                    "5. Lis l'Alpha : s'il est positif, ta stratégie bat le Buy & Hold !")
        if "graphique" in q or "chart" in q:
            return ("📈 **Lire les graphiques** : Va dans l'onglet **Documentation** → "
                    "**📊 Comprendre les Graphiques** pour une explication détaillée de chaque chart avec des tableaux et des formules !")

    # 5. Base de connaissances (exact puis fuzzy)
    for k, v in KNOWLEDGE_BASE.items():
        if k in q:
            return f"💡 **{k.upper()}** :\n{v}"

    mots_cles = list(KNOWLEDGE_BASE.keys())
    mots_requete = q.split()
    for mot in mots_requete:
        if len(mot) > 3:
            matches = difflib.get_close_matches(mot, mots_cles, n=1, cutoff=0.72)
            if matches:
                k = matches[0]
                return f"💡 *(Tu voulais dire **'{k}'** ?)* \n**{k.upper()}** :\n{KNOWLEDGE_BASE[k]}"

    # 6. Réponse de secours avec suggestions
    topic = random.choice(ALL_TOPICS)
    return (f"❓ Je n'ai pas bien compris ta question.\n\n"
            f"**Ce que je sais faire :**\n"
            f"- Expliquer un concept : *'C'est quoi le VWAP ?'*, *'Explique le Sharpe'*\n"
            f"- Informer sur un onglet : *'Comment utiliser le Bot ?'*, *'C'est quoi le Backtesting ?'*\n"
            f"- Voir ton solde : *'Mon portefeuille'*, *'Combien j'ai ?'*\n"
            f"- Calculer : *'100 * 1.05'*, *'5% de 2000'*\n"
            f"- Conseiller : *'Quoi acheter ?'*, *'Meilleure action ?'*\n\n"
            f"💡 Essaie par exemple : *'C'est quoi le {topic} ?'*")


def render_assistant():
    pass
