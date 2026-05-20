import streamlit as st
import random
import re
import difflib

KNOWLEDGE_BASE = {
    "action": "Une **action** est un titre de propriété représentant une fraction d'une entreprise.",
    "etf": "Un **ETF** est un fonds indiciel coté répliquant la performance d'un indice boursier.",
    "option": "Une **option** donne le droit d'acheter (Call) ou de vendre (Put) un actif sous-jacent à un prix fixé.",
    "call": "Un **Call** est une option d'achat, pariant sur une hausse.",
    "put": "Un **Put** est une option de vente, pariant sur une baisse.",
    "dividende": "Un **dividende** est la part des bénéfices reversée aux actionnaires.",
    "bitcoin": "Le **Bitcoin** est la première cryptomonnaie décentralisée.",
    "crypto": "Les **cryptomonnaies** sont des actifs numériques décentralisés.",
    "indice": "Un **indice boursier** est un panier de valeurs (ex: CAC 40, S&P 500).",
    "rsi": "Le **RSI** (Relative Strength Index) mesure la force du marché (surachat > 70, survente < 30).",
    "sma": "La **SMA** (Moyenne Mobile Simple) lisse les prix pour identifier les tendances.",
    "vwap": "Le **VWAP** est le prix moyen pondéré par le volume d'échanges intraday.",
    "sharpe": "Le **ratio de Sharpe** mesure la rentabilité ajustée au risque (>1 = bon).",
    "volatilite": "La **volatilité** mesure l'amplitude des variations de prix d'un actif.",
    "beta": "Le **bêta (β)** mesure la sensibilité d'un actif par rapport à l'indice de référence.",
    "per": "Le **PER** mesure la valorisation (Prix de l'action / Bénéfice par action).",
    "drawdown": "Le **drawdown** mesure la perte maximale d'un portefeuille depuis un sommet.",
    "rendement": "Le **rendement** est le pourcentage de gain sur un investissement.",
    "risque": "Le **risque** financier se mesure par la volatilité, le bêta et le drawdown.",
    "diversification": "La **diversification** réduit le risque en répartissant les investissements.",
    "cac40": "Le **CAC 40** est l'indice des 40 plus grandes entreprises françaises.",
    "nasdaq": "Le **Nasdaq** est l'indice technologique américain.",
    "sp500": "Le **S&P 500** est l'indice des 500 plus grandes entreprises américaines.",
    "stop loss": "Un **stop loss** limite les pertes en vendant automatiquement sous un seuil.",
    "leverage": "Le **levier** amplifie les gains et les pertes.",
    "backtesting": "Le **backtesting** teste une stratégie sur des données historiques.",
    "algo": "Le bot utilise : SMA (Moyennes Mobiles), RSI (Surachat/Survente) et Random Forest (Machine Learning).",
    "bot": "Le **bot de trading** recommande automatiquement des achats ou ventes selon la stratégie choisie dans l'onglet 'Bot'. Il t'explique pourquoi avant que tu valides.",
    "marché": "L'onglet **Marché** sert à afficher le cours en temps réel, l'historique et le niveau de risque de l'action.",
    "portefeuille": "L'onglet **Portefeuille** te permet d'acheter ou de vendre des actions, et de suivre l'évolution de tes gains.",
    "backtest": "L'onglet **Backtesting** te permet de simuler une stratégie de trading dans le passé pour voir si elle aurait été rentable.",
    "backtesting": "L'onglet **Backtesting** te permet de tester les performances passées d'une stratégie (SMA ou RSI).",
    "documentation": "L'onglet **Documentation** contient un mode d'emploi du site complet et un cours de finance accéléré.",
    "achat": "Pour faire un **achat**, rends-toi dans l'onglet Portefeuille, sélectionne une action, choisis la quantité et valide l'ordre.",
    "vente": "Pour **vendre** une action, rends-toi dans le Portefeuille. Attention, tu ne peux vendre que les actions que tu possèdes déjà.",
}

ALL_TOPICS = ["ETF", "Dividende", "PER", "CAC 40", "Nasdaq", "S&P 500", "Bitcoin", "RSI", "SMA", "Sharpe", "Volatilité"]

def generate_response(query: str, p) -> str:
    q = query.lower().strip()

    # 1. Calculs mathématiques
    math_match = re.search(r"(\d+(?:[.,]\d+)?)\s*([\+\-\*/xX])\s*(\d+(?:[.,]\d+)?)", q)
    if math_match:
        try:
            v1_str = math_match.group(1).replace(",", ".")
            v2_str = math_match.group(3).replace(",", ".")
            v1, op, v2 = float(v1_str), math_match.group(2).lower(), float(v2_str)
            
            if op == "+": res = v1 + v2
            elif op == "-": res = v1 - v2
            elif op in ["*", "x"]: res = v1 * v2; op = "×"
            elif op == "/": res = (v1 / v2) if v2 != 0 else "∞"; op = "÷"
            return f"🔢 **{v1} {op} {v2}** = **{res}**"
        except: pass

    # 2. Recommandations d'achat
    conseil_triggers = ["meilleur action", "meilleure action", "quoi acheter", "recommandation"]
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
                return f"🤖 L'action **{best_asset}** a le meilleur Ratio de Sharpe actuel ({best_sharpe:.2f}) parmi nos valeurs suivies."
        except: pass
        return "🤖 Nvidia (NVDA) et Apple (AAPL) affichent d'excellentes statistiques quantitatives actuelles."

    # 3. Portefeuille
    portfolio_triggers = ["portefeuille", "solde", "liquidité", "cash", "gain", "perte", "performance", "positions"]
    if any(w in q for w in portfolio_triggers):
        total_value = p.cash
        for t, info in p.positions.items():
            total_value += info["quantity"] * info["avg_price"]
        perf = ((total_value - p.initial_cash) / p.initial_cash) * 100
        return f"💼 **Portefeuille**\n- Liquidités : {p.cash:,.2f} €\n- Valeur Totale : {total_value:,.2f} €\n- Perf : {perf:+.2f}%"

    # 4. Connaissances exactes ou approximatives (Fuzzy Matching)
    import difflib
    
    # Recherche exacte d'abord
    for k, v in KNOWLEDGE_BASE.items():
        if k in q: return f"💡 **{k.upper()}** :\n{v}"
        
    # Si non trouvé, recherche avec tolérance aux fautes (Fuzzy Matching)
    mots_cles = list(KNOWLEDGE_BASE.keys())
    mots_requete = q.split()
    for mot in mots_requete:
        if len(mot) > 3:
            matches = difflib.get_close_matches(mot, mots_cles, n=1, cutoff=0.7)
            if matches:
                k = matches[0]
                return f"💡 *(Tu voulais dire '{k}' ?)* \n**{k.upper()}** :\n{KNOWLEDGE_BASE[k]}"

    return "Je n'ai pas compris. Tu peux me poser des questions sur les notions de finance (RSI, ETF, Sharpe), demander un conseil d'achat, interroger ton solde ou me demander un calcul mathématique."

def render_assistant():
    st.sidebar.divider()
    st.sidebar.subheader("💬 Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Container for messages in sidebar
    chat_container = st.sidebar.container(height=300)
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if user_input := st.sidebar.chat_input("Pose une question..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container.chat_message("user"):
            st.markdown(user_input)

        # Bug 4 fix : garde si portefeuille absent (utilisateur non connecté)
        portfolio = st.session_state.get("portfolio")
        if portfolio is None:
            response = "🔒 Connecte-toi pour accéder aux fonctionnalités du portefeuille et des recommandations."
        else:
            response = generate_response(user_input, portfolio)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with chat_container.chat_message("assistant"):
            st.markdown(response)
