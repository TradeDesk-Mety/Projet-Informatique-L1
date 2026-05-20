"""
5_💬_Assistant.py — Assistant financier et chatbot interactif
============================================================

Cette page propose un agent conversationnel financier.
Il répond de manière autonome et personnalisée à deux types de questions :
1. Les questions sur le portefeuille actuel de l'utilisateur (solde, valeur, positions, PnL).
2. Les questions sur les notions financières et l'utilisation de la plateforme.

Relations avec les autres modules :
----------------------------------
- equities.equities (Portfolio) : lit l'état actuel pour répondre aux questions sur le portefeuille.
- website/web.py : s'appuie sur la session de l'utilisateur connecté.
"""

import streamlit as st
import random
import os
import sys
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# ── Garde d'authentification ──────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

p = st.session_state.portfolio
user_email = st.session_state.user_email

st.title("💬 Assistant Financier Virtuel")
st.caption(
    "Pose des questions sur ton portefeuille ou sur les concepts financiers "
    "(ex : RSI, ETF, CAC 40, Bitcoin, Sharpe, dividende, stop loss…)."
)

# ── Base de connaissances ─────────────────────────────────────────────────────
KNOWLEDGE_BASE = {
    # ── Produits & instruments ────────────────────────────────────────────────
    "action": (
        "Une **action** est un titre de propriété représentant une fraction d'une entreprise. "
        "En la détenant, tu deviens actionnaire : tu as droit aux bénéfices distribués (dividendes) "
        "et parfois au droit de vote lors des assemblées générales. "
        "Sur cette plateforme, tu peux acheter ou vendre des actions depuis l'onglet **Portefeuille**."
    ),
    "etf": (
        "Un **ETF** (Exchange-Traded Fund, ou fonds indiciel coté) est un fonds qui réplique la performance "
        "d'un indice boursier (CAC 40, S&P 500, Nasdaq…). "
        "Il offre une diversification immédiate avec des frais de gestion très faibles (souvent < 0,5 % par an). "
        "Idéal pour les débutants souhaitant investir sans choisir des titres individuels."
    ),
    "option": (
        "Une **option** est un produit dérivé qui donne le droit (et non l'obligation) d'acheter (Call) "
        "ou de vendre (Put) un actif sous-jacent à un prix fixé (Strike) à ou avant une date donnée. "
        "Tu peux en simuler sur cette plateforme depuis la page **Portefeuille**."
    ),
    "call": (
        "Un **Call** est une option d'achat. Il prend de la valeur lorsque le cours du sous-jacent monte. "
        "L'acheteur d'un Call anticipe une hausse du marché."
    ),
    "put": (
        "Un **Put** est une option de vente. Il prend de la valeur lorsque le cours du sous-jacent baisse. "
        "L'acheteur d'un Put anticipe une baisse du marché ou cherche à se couvrir."
    ),
    "dividende": (
        "Un **dividende** est la part des bénéfices d'une entreprise reversée à ses actionnaires. "
        "Le **rendement du dividende** se calcule ainsi : dividende annuel / prix de l'action. "
        "Par exemple, une action à 100 € versant 4 € de dividende a un rendement de 4 %. "
        "Ce sont des revenus passifs très prisés des investisseurs long terme."
    ),
    "bitcoin": (
        "Le **Bitcoin (BTC)** est la première cryptomonnaie décentralisée, créée en 2009 par Satoshi Nakamoto. "
        "Il fonctionne sur une blockchain sans autorité centrale. Très volatile, il peut varier de ±10 % "
        "en une seule journée. Il est disponible comme actif dans le simulateur de cette plateforme."
    ),
    "crypto": (
        "Les **cryptomonnaies** sont des monnaies numériques décentralisées reposant sur la technologie blockchain. "
        "Elles sont très volatiles et présentent un risque élevé. Le Bitcoin est le plus connu, "
        "suivi d'Ethereum, Solana, etc. Tu peux simuler des positions crypto dans cette plateforme."
    ),
    "indice": (
        "Un **indice boursier** est un panier de valeurs mesurant la performance globale d'un marché ou d'un secteur. "
        "Exemples : CAC 40 (France), S&P 500 (USA), Nasdaq (tech US), Nikkei (Japon). "
        "Les indices servent de référence ('benchmark') pour évaluer la performance d'un portefeuille."
    ),
    # ── Indicateurs & ratios ──────────────────────────────────────────────────
    "rsi": (
        "Le **RSI** (Relative Strength Index) est un indicateur de momentum oscillant entre 0 et 100. "
        "• RSI < 30–35 → actif **survendu** (opportunité d'achat potentielle).\n"
        "• RSI > 65–70 → actif **suracheté** (opportunité de vente potentielle).\n"
        "Sur cette plateforme, le bot utilise un RSI(7) avec des seuils à 35 / 65."
    ),
    "sma": (
        "La **SMA** (Simple Moving Average, Moyenne Mobile Simple) est la moyenne du cours de clôture "
        "sur N jours glissants. Elle lisse les variations et identifie les tendances. "
        "Le bot compare SMA(5) et SMA(15) : si SMA(5) > SMA(15), la tendance est haussière → signal ACHAT."
    ),
    "vwap": (
        "Le **VWAP** (Volume Weighted Average Price) est le prix moyen pondéré par le volume d'échanges. "
        "Il sert de référence aux traders intraday : si le cours est au-dessus du VWAP, le marché est "
        "haussier sur la journée. Tu peux visualiser le VWAP dans l'onglet **Marché**."
    ),
    "sharpe": (
        "Le **ratio de Sharpe** mesure la performance d'un investissement ajustée au risque. "
        "Formule : (Rendement – Taux sans risque) / Volatilité. "
        "• Sharpe > 1 → bon\n• > 2 → excellent\n• < 0 → sous-performance vs l'actif sans risque."
    ),
    "volatilite": (
        "La **volatilité** mesure l'amplitude des variations de prix d'un actif. "
        "Une volatilité élevée = risque accru, mais aussi des opportunités de gains (et de pertes) plus importantes. "
        "Elle est calculée sur les rendements journaliers annualisés (× √252)."
    ),
    "beta": (
        "Le **bêta (β)** mesure la sensibilité d'un actif par rapport à un indice de référence (S&P 500). "
        "• β = 1 → évolue comme le marché\n• β > 1 → plus volatil (ex: Nvidia ≈ 1,8)\n"
        "• β < 1 → plus stable (ex: Berkshire ≈ 0,8)."
    ),
    "per": (
        "Le **PER** (Price-to-Earnings Ratio, ou ratio cours/bénéfice) mesure la valorisation d'une entreprise. "
        "Formule : Prix de l'action / Bénéfice net par action. "
        "Un PER élevé (ex: 40) suggère que le marché anticipe une forte croissance. "
        "Un PER faible peut indiquer une action sous-évaluée ou une entreprise en difficulté."
    ),
    "p/e": (
        "Le **P/E** (Price-to-Earnings) est synonyme du PER. Voir la définition du PER pour plus de détails."
    ),
    "drawdown": (
        "Le **drawdown** (ou recul maximal) mesure la baisse maximale d'un portefeuille depuis son dernier sommet. "
        "C'est une mesure clé du risque : un drawdown de –30 % signifie qu'à un moment, "
        "tu aurais perdu 30 % si tu avais acheté au plus haut. "
        "Visible dans les résultats de backtesting de la plateforme."
    ),
    "rendement": (
        "Le **rendement** est le gain réalisé sur un investissement, exprimé en pourcentage. "
        "Formule simple : (Valeur finale – Valeur initiale) / Valeur initiale × 100. "
        "On distingue le rendement total (plus-value + dividendes) et le rendement annualisé."
    ),
    "risque": (
        "Le **risque** en finance est la probabilité de subir une perte. Il se mesure par :\n"
        "• La **volatilité** (amplitude des variations)\n"
        "• Le **bêta** (sensibilité au marché)\n"
        "• Le **drawdown maximal** (pire perte historique)\n"
        "• La **Value at Risk (VaR)** (perte maximale probable sur une période)."
    ),
    "diversification": (
        "La **diversification** consiste à répartir ses investissements sur différents actifs, secteurs "
        "ou zones géographiques pour réduire le risque global. "
        "L'idée : si un actif baisse, les autres compensent. "
        "Un ETF est un excellent outil de diversification automatique."
    ),
    "market cap": (
        "La **capitalisation boursière** (market cap) est la valeur totale d'une entreprise en bourse. "
        "Formule : Nombre d'actions × Cours de l'action. "
        "Exemples : Apple ≈ 3 000 Md$, LVMH ≈ 350 Md€."
    ),
    "capitalisation": (
        "La **capitalisation boursière** est la valeur totale d'une entreprise en bourse. "
        "Voir 'market cap' pour plus de détails."
    ),
    # ── Indices ───────────────────────────────────────────────────────────────
    "cac40": (
        "Le **CAC 40** est l'indice boursier de référence de la Bourse de Paris (Euronext). "
        "Il regroupe les 40 plus grandes entreprises françaises par capitalisation boursière "
        "(LVMH, TotalEnergies, Airbus, BNP Paribas, L'Oréal…). "
        "Il est considéré comme le baromètre de l'économie française."
    ),
    "cac 40": (
        "Le **CAC 40** regroupe les 40 plus grandes capitalisations boursières françaises. "
        "Voir 'cac40' pour plus de détails."
    ),
    "nasdaq": (
        "Le **Nasdaq** est le principal indice boursier technologique américain. "
        "Il regroupe des géants de la tech comme Apple, Microsoft, Nvidia, Amazon, Alphabet, Meta, Tesla. "
        "Plus volatil que le S&P 500 en raison de sa concentration sectorielle dans la technologie."
    ),
    "sp500": (
        "Le **S&P 500** regroupe les 500 plus grandes entreprises cotées aux États-Unis. "
        "C'est la référence mondiale de la performance du marché actions. "
        "La plupart des ETF l'utilisent comme benchmark. Rendement historique : ~10 % par an en moyenne."
    ),
    "s&p": (
        "Le **S&P 500** regroupe les 500 plus grandes entreprises américaines. "
        "Référence mondiale pour évaluer la performance d'un portefeuille. Voir 'sp500'."
    ),
    # ── Stratégies & outils ───────────────────────────────────────────────────
    "stop loss": (
        "Un **stop loss** est un ordre de vente automatique qui se déclenche si le cours descend "
        "sous un seuil défini. Il permet de **limiter les pertes** sans avoir à surveiller le marché en permanence. "
        "Exemple : tu achètes à 100 € et poses un stop loss à 90 € → vente automatique si le cours touche 90 €."
    ),
    "stoploss": (
        "Un **stop loss** limite les pertes en vendant automatiquement quand le cours descend sous un seuil. "
        "Voir 'stop loss' pour plus de détails."
    ),
    "leverage": (
        "Le **levier** (leverage) amplifie les gains ET les pertes en permettant d'investir plus que son capital. "
        "Un levier ×5 sur 1 000 € permet de contrôler 5 000 € de position. "
        "⚠️ Très risqué pour les débutants : une baisse de 20 % avec levier ×5 = perte totale du capital."
    ),
    "levier": (
        "Le **levier financier** amplifie les gains et les pertes. "
        "Voir 'leverage' pour plus de détails."
    ),
    "backtesting": (
        "Le **backtesting** consiste à tester une stratégie de trading sur des données historiques "
        "pour évaluer sa rentabilité passée. Sur cette plateforme, l'onglet **Backtesting** "
        "permet de simuler les stratégies SMA et RSI et d'afficher les résultats (rendement, drawdown, Sharpe)."
    ),
    "backtest": (
        "Le **backtesting** évalue une stratégie sur l'historique des prix. "
        "Voir 'backtesting' ou rends-toi dans l'onglet **Backtesting** de la plateforme."
    ),
    "algo": (
        "Le simulateur intègre trois stratégies de trading automatique :\n"
        "1. **SMA** (croisement de moyennes mobiles rapides/lentes)\n"
        "2. **RSI** (détection des excès de marché : surachat/survente)\n"
        "3. **Machine Learning** (Random Forest Classifier prédisant la hausse à 3 jours).\n"
        "Accède-y depuis l'onglet **Bot**."
    ),
    "bot": (
        "Le **bot de trading automatique** analyse le marché et génère un signal (Achat / Vente / Neutre) "
        "en utilisant la stratégie choisie (SMA, RSI ou Machine Learning). "
        "Il affiche un rapport complet avant de demander ton autorisation pour exécuter un ordre. "
        "Rends-toi dans l'onglet **Bot** pour l'utiliser."
    ),
    "black-scholes": (
        "La formule de **Black-Scholes** (1973) est un modèle mathématique d'évaluation des options européennes. "
        "Elle estime la prime d'une option à partir de 5 paramètres : cours (S), strike (K), "
        "temps restant (T), taux sans risque (r) et volatilité (σ)."
    ),
    "medallion": (
        "L'architecture **Medallion** organise les données en trois couches :\n"
        "• **Bronze** : données brutes extraites des API\n"
        "• **Silver** : données nettoyées, standardisées, dédupliquées\n"
        "• **Gold** : données enrichies d'indicateurs techniques, prêtes à analyser."
    ),
    # ── Navigation plateforme ─────────────────────────────────────────────────
    "order": (
        "Pour **passer un ordre** sur la plateforme :\n"
        "1. Rends-toi dans l'onglet **Portefeuille**.\n"
        "2. Sélectionne le type d'ordre (Achat ou Vente).\n"
        "3. Choisis l'actif et la quantité souhaitée.\n"
        "4. Confirme — la transaction est exécutée immédiatement au cours actuel."
    ),
    "ordre": (
        "Pour **passer un ordre** : rends-toi dans l'onglet **Portefeuille**, "
        "sélectionne le type (Achat/Vente), l'actif et la quantité, puis confirme."
    ),
    "marché": (
        "L'onglet **Marché** te permet de :\n"
        "• Consulter l'historique de cours de n'importe quel actif disponible\n"
        "• Visualiser les indicateurs techniques (SMA, RSI, VWAP)\n"
        "• Analyser la volatilité et les tendances en temps réel."
    ),
    "portefeuille": (
        "L'onglet **Portefeuille** centralise :\n"
        "• Tes **liquidités disponibles** (cash)\n"
        "• Tes **positions** (actifs détenus, quantité, prix moyen)\n"
        "• Ta **performance globale** (gains/pertes latents)\n"
        "• Les formulaires pour **passer des ordres** d'achat ou de vente."
    ),
}

# ── Réponses de salutation ────────────────────────────────────────────────────
GREETINGS = [
    "Bonjour ! Comment puis-je t'aider dans tes analyses de marché ?",
    "Salut ! Je suis ton assistant de trading. Pose-moi une question sur ton portefeuille ou sur les marchés.",
    "Bienvenue ! Que souhaites-tu analyser ou comprendre aujourd'hui ?",
    "Bonsoir ! Je suis là pour répondre à toutes tes questions financières.",
]

THANKS = [
    "Avec plaisir ! N'hésite pas si tu as d'autres questions.",
    "De rien ! Je suis là pour t'aider à mieux comprendre les marchés.",
    "Ravi d'avoir pu t'aider ! Pose-moi d'autres questions quand tu veux.",
]

BYES = [
    "À bientôt ! Bon trading ! 📈",
    "Au revoir ! N'oublie pas de surveiller tes positions. 💼",
    "Bonne journée ! Et n'oublie pas : diversifie tes risques ! 🎯",
]

# ── Sujets disponibles (pour le fallback) ─────────────────────────────────────
ALL_TOPICS = [
    "ETF", "Dividende", "PER / P/E", "CAC 40", "Nasdaq", "S&P 500",
    "Bitcoin / Crypto", "Action", "Indice boursier", "Passer un ordre",
    "Marché (cours & indicateurs)", "Bot de trading", "Backtesting / Backtest",
    "VWAP", "Stop Loss", "Levier (Leverage)", "Rendement", "Risque",
    "Drawdown", "Diversification", "Market Cap / Capitalisation",
    "Portefeuille (solde, positions)", "RSI", "SMA", "Sharpe",
    "Volatilité", "Bêta", "Black-Scholes", "Option / Call / Put",
]

# ── Fonction principale de réponse ────────────────────────────────────────────
def generate_response(query: str) -> str:
    q = query.lower().strip()

    # ── 1. Calculs arithmétiques ──────────────────────────────────────────────
    math_match = re.search(r"(\d+(?:\.\d+)?)\s*([\+\-\*/])\s*(\d+(?:\.\d+)?)", q)
    if math_match:
        try:
            v1, op, v2 = float(math_match.group(1)), math_match.group(2), float(math_match.group(3))
            if op == "+":   res = v1 + v2
            elif op == "-": res = v1 - v2
            elif op == "*": res = v1 * v2
            elif op == "/": res = (v1 / v2) if v2 != 0 else "∞ (division par zéro)"
            return f"🔢 **{v1} {op} {v2}** = **{res}**"
        except Exception:
            pass

    # ── 2. Salutations ────────────────────────────────────────────────────────
    if any(g in q for g in ["bonjour", "bonsoir", "salut", "hello", "hey", "hi", "coucou"]):
        return random.choice(GREETINGS)
    if any(t in q for t in ["merci", "thanks", "thank you", "super merci"]):
        return random.choice(THANKS)
    if any(b in q for b in ["bye", "au revoir", "à bientôt", "bonne journée", "ciao", "adieu"]):
        return random.choice(BYES)

    # ── 3. Recommandation d'achat (analyse Sharpe live) ───────────────────────
    conseil_triggers = [
        "meilleur action", "meilleure action", "quoi acheter", "que faut-il acheter",
        "conseil d'achat", "quelle action", "action a acheter", "action à acheter",
        "recommandation", "que recommandes", "que recommande",
    ]
    if any(t in q for t in conseil_triggers):
        try:
            import data.data as data_mod
            top_picks = ["Apple Inc.", "Nvidia", "Microsoft", "Amazon", "Tesla, Inc."]
            best_sharpe, best_asset = -999.0, None
            for asset in top_picks:
                try:
                    df = data_mod.recuperer_historique(asset, "1y", "1d")
                    if not df.empty:
                        ret = df["Close"].pct_change().dropna()
                        import numpy as np
                        s_ratio = (ret.mean() / (ret.std() + 1e-9)) * (252 ** 0.5)
                        if s_ratio > best_sharpe:
                            best_sharpe, best_asset = s_ratio, asset
                except Exception:
                    pass
            if best_asset and best_sharpe != -999.0:
                return (
                    f"🤖 **Analyse quantitative en direct** :\n\n"
                    f"Sur un historique de 1 an, **{best_asset}** présente le meilleur profil "
                    f"rendement/risque parmi nos actifs phares avec un **Ratio de Sharpe de {best_sharpe:.2f}**.\n\n"
                    f"*(Un Sharpe > 1 indique un bon rendement par unité de risque. "
                    f"Tu peux activer le Bot de trading sur cet actif depuis l'onglet **Bot** !)*"
                )
        except Exception:
            pass
        return (
            "🤖 D'après les indicateurs quantitatifs, des actions comme **Nvidia** (NVDA) ou **Apple** (AAPL) "
            "sont souvent bien positionnées. Analyse-les dans l'onglet **Marché** et teste le bot dans l'onglet **Bot**."
        )

    # ── 4. Questions sur le portefeuille ──────────────────────────────────────
    portfolio_triggers = [
        "portefeuille", "portfolio", "mon capital", "mes positions", "valeur totale",
        "roi", "gain", "perte", "performance", "solde", "liquidité", "liquidités",
        "cash", "combien j'ai", "combien ai-je", "mon compte",
    ]
    if any(w in q for w in portfolio_triggers):
        total_value = p.cash
        positions_summary = []
        for t, info in p.positions.items():
            val_pos = info["quantity"] * info["avg_price"]
            positions_summary.append(
                f"- **{t}** : {info['quantity']} unité(s) @ {info['avg_price']:.2f} € (valeur estimée : {val_pos:,.2f} €)"
            )
            total_value += val_pos
        perf = ((total_value - p.initial_cash) / p.initial_cash) * 100
        perf_icon = "📈" if perf >= 0 else "📉"

        resp = (
            f"Voici l'état de ton portefeuille en direct :\n\n"
            f"- 💵 **Liquidités disponibles** : {p.cash:,.2f} €\n"
            f"- 📦 **Valeur des actifs détenus** : {(total_value - p.cash):,.2f} €\n"
            f"- 🏢 **Valeur totale du compte** : {total_value:,.2f} €\n"
            f"- {perf_icon} **Performance globale** : {perf:+.2f} % "
            f"(capital initial : {p.initial_cash:,.2f} €)\n\n"
        )
        if positions_summary:
            resp += "**Positions actuellement détenues :**\n" + "\n".join(positions_summary)
        else:
            resp += (
                "Tu ne détiens actuellement aucune position. "
                "Passe un ordre depuis l'onglet **Portefeuille** pour commencer !"
            )
        return resp

    # ── 5. Recherche dans la base de connaissances ────────────────────────────
    # 5a. Multi-mots en priorité (clés de 2–3 mots)
    multi_word_keys = sorted(
        [k for k in KNOWLEDGE_BASE if " " in k or "/" in k],
        key=lambda k: -len(k)
    )
    for key in multi_word_keys:
        if key in q:
            return f"💡 **{key.upper()}** :\n\n{KNOWLEDGE_BASE[key]}"

    # 5b. Clés simples
    single_keys = [k for k in KNOWLEDGE_BASE if " " not in k and "/" not in k]
    for key in single_keys:
        if key in q:
            return f"💡 **{key.upper()}** :\n\n{KNOWLEDGE_BASE[key]}"

    # ── 6. Fallback enrichi ───────────────────────────────────────────────────
    topics_str = "\n".join(f"• {t}" for t in ALL_TOPICS)
    return (
        "Je n'ai pas trouvé de réponse précise à ta question. "
        "Je suis capable de t'aider sur les sujets suivants :\n\n"
        + topics_str
        + "\n\n"
        "💡 **Astuce** : Tu peux aussi me demander :\n"
        "- L'état de ton portefeuille (*'Quel est mon solde ?'*)\n"
        "- Des calculs simples (*'150 × 1.05'*)\n"
        "- Une recommandation (*'Quelle action acheter ?'*)"
    )

# ── Initialisation de l'historique ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                f"Bonjour **{user_email}** ! 👋\n\n"
                "Je suis ton assistant financier virtuel. Je peux t'aider sur :\n"
                "- **Ton portefeuille** : solde, positions, performance\n"
                "- **Les marchés** : cours, indices (CAC 40, Nasdaq, S&P 500…)\n"
                "- **Les instruments** : actions, ETF, options, Bitcoin…\n"
                "- **Les indicateurs** : RSI, SMA, VWAP, Sharpe, Bêta…\n"
                "- **La plateforme** : comment passer un ordre, utiliser le bot, faire du backtesting…\n\n"
                "Pose-moi ta question ! 💬"
            ),
        }
    ]

# ── Affichage des messages ────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Saisie utilisateur ────────────────────────────────────────────────────────
if user_input := st.chat_input("Pose une question ici… (ex : Qu'est-ce qu'un ETF ?)"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = generate_response(user_input)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
