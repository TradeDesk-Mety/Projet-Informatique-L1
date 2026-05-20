import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui
set_global_ui()
render_assistant()

import streamlit as st

st.title("📚 Documentation & Apprentissage")
st.caption("Mode d'emploi complet de la plateforme et cours de finance interactif.")

tab_mode_emploi, tab_cours = st.tabs(["📖 Mode d'Emploi", "🎓 Cours de Finance (Bases)"])

with tab_mode_emploi:
    st.header("Mode d'Emploi de la Plateforme")
    
    with st.expander("1. Présentation Globale", expanded=True):
        st.write(
            "Bienvenue sur TradeDesk. Cette plateforme vous permet de simuler des investissements "
            "en conditions réelles, sans risquer de véritable capital.\n\n"
            "**Les grandes étapes :**\n"
            "1. Consultez l'onglet **Marché** pour analyser les cours.\n"
            "2. Passez des ordres dans l'onglet **Portefeuille**.\n"
            "3. Laissez le **Bot** analyser le marché pour vous.\n"
            "4. Vérifiez vos stratégies via le **Backtesting**."
        )

    with st.expander("2. Onglet Marché", expanded=False):
        st.write(
            "L'onglet **Marché** est votre centre d'analyse en direct.\n"
            "- Sélectionnez un actif dans la barre supérieure.\n"
            "- **Temps Réel** : Observez les variations intraday avec le VWAP et la jauge de force.\n"
            "- **Historique** : Un graphique interactif (cliquez et glissez pour zoomer) vous montre l'évolution sur plusieurs mois/années.\n"
            "- **Statistiques** : Découvrez le niveau de risque de l'action grâce au Ratio de Sharpe et à la volatilité annualisée."
        )

    with st.expander("3. Onglet Portefeuille (Passer un ordre)", expanded=False):
        st.write(
            "C'est ici que vous gérez votre capital virtuel.\n"
            "- **Acheter** : Choisissez un actif, saisissez la quantité et validez. Une commission standard de 1% est appliquée.\n"
            "- **Vendre** : Vous ne pouvez vendre que les actifs que vous possédez.\n"
            "- **Positions** : Suivez vos gains et pertes (G/P) latents en temps réel. Les valeurs s'actualisent automatiquement."
        )

    with st.expander("4. Onglet Bot de Trading & Algorithmes", expanded=False):
        st.write(
            "Le **Bot** est une intelligence artificielle qui analyse les graphiques à votre place.\n"
            "Choisissez une stratégie :\n"
            "- **SMA** : Achète si la moyenne à court terme dépasse la moyenne à long terme (tendance haussière).\n"
            "- **RSI** : Achète si l'action a trop baissé (survente) et vend si elle a trop monté (surachat).\n"
            "- **Machine Learning** : Utilise l'historique de l'action pour deviner la probabilité de hausse à 3 jours.\n\n"
            "Le bot vous fera un **rapport narratif complet** avec son explication avant de vous demander l'autorisation d'agir."
        )

    with st.expander("5. Formules & Indicateurs", expanded=False):
        st.write(
            "Voici les indicateurs utilisés sur la plateforme :\n\n"
            "- **Moyenne Mobile Simple (SMA)** : Lisse les prix sur une période donnée pour faire ressortir la tendance.\n"
            "- **RSI (Relative Strength Index)** : Oscille entre 0 et 100. Au-dessus de 70, l'actif est surévalué. En dessous de 30, il est sous-évalué.\n"
            "- **VWAP** : Le prix moyen payé par les investisseurs au cours de la journée, pondéré par le volume.\n"
            "- **Ratio de Sharpe** : Renseigne sur la rentabilité par rapport au risque pris. Supérieur à 1, c'est un excellent investissement."
        )

with tab_cours:
    st.header("Les Bases de la Finance et de l'Investissement")
    st.write("Ce mini-cours vous donnera toutes les clés pour comprendre les marchés financiers avant d'investir virtuellement.")

    st.subheader("1. Qu'est-ce qu'une Action ?")
    st.write(
        "Une **action** représente une fraction du capital d'une entreprise. En l'achetant, vous devenez actionnaire.\n"
        "- **Plus-value** : Si l'entreprise se développe, l'action prend de la valeur et vous pouvez la revendre plus cher.\n"
        "- **Dividendes** : Certaines entreprises reversent une partie de leurs bénéfices annuels directement à leurs actionnaires."
    )

    st.subheader("2. Le Risque et la Volatilité")
    st.write(
        "Sur les marchés financiers, **le risque et le rendement sont liés**. "
        "Plus un actif peut vous rapporter gros, plus il risque de vous faire perdre de l'argent.\n"
        "- La **volatilité** mesure l'instabilité du cours. Une cryptomonnaie a une forte volatilité.\n"
        "- L'objectif d'un bon investisseur n'est pas de ne prendre aucun risque, mais d'**optimiser son rendement pour un niveau de risque donné** (c'est ce que mesure le Ratio de Sharpe)."
    )

    st.subheader("3. Les Indices et les ETF")
    st.write(
        "- Un **Indice Boursier** (comme le CAC 40 en France ou le S&P 500 aux États-Unis) regroupe les plus grandes entreprises d'un marché pour en mesurer la santé globale.\n"
        "- Un **ETF** (Exchange Traded Fund) est un 'panier' d'actions qui copie exactement les performances d'un indice. Acheter un ETF S&P 500 revient à acheter une petite part des 500 plus grandes entreprises américaines d'un seul coup. C'est idéal pour **diversifier**."
    )

    st.subheader("4. Comment analyser le marché ?")
    st.write(
        "Il existe deux grandes écoles :\n"
        "1. **L'Analyse Fondamentale** : Étudier les bilans financiers de l'entreprise, ses projets, et l'économie mondiale pour déduire sa 'vraie' valeur.\n"
        "2. **L'Analyse Technique** : Étudier les graphiques et les mathématiques (ce que fait cette plateforme avec le RSI, les SMA et le Machine Learning) pour repérer des tendances psychologiques des investisseurs."
    )
