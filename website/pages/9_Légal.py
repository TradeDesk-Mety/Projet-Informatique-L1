import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from website.components.ui_config import set_global_ui

set_global_ui()

st.title("Informations Légales")
st.caption("TradeDesk — Simulateur boursier pédagogique · 2026")

#Sélection via les query params ou navigation par défaut
params = st.query_params
section_default = params.get("section", "confidentialite")

tab_conf, tab_cgu, tab_mentions = st.tabs([
    "Politique de Confidentialité",
    "Conditions d'Utilisation",
    "Mentions Légales",
])

#TAB 1 — Politique de Confidentialité
with tab_conf:
    st.header("Politique de Confidentialité")
    st.caption("Dernière mise à jour : 1er janvier 2026")

    st.markdown("""
## 1. Responsable du traitement

TradeDesk est un projet pédagogique développé dans le cadre du cursus L1 Informatique.
Le responsable du traitement des données est l'équipe de développement de TradeDesk
(ci-après « nous »).

---

## 2. Données collectées

Dans le cadre de l'utilisation de TradeDesk, nous collectons les données suivantes :

| Type de donnée | Finalité | Durée de conservation |
|---|---|---|
| Nom d'utilisateur | Identification · Connexion | Durée du compte |
| Mot de passe (haché PBKDF2-SHA256) | Authentification sécurisée | Durée du compte |
| Date de création du compte | Gestion interne | Durée du compte |
| Données de portefeuille | Simulation de trading | Durée du compte |
| Historique des transactions | Suivi pédagogique | Durée du compte |

**Nous ne collectons pas :**
- Adresse e-mail ou numéro de téléphone
- Données bancaires ou financières réelles
- Données de localisation
- Cookies tiers à des fins publicitaires

---

## 3. Sécurité des mots de passe

Vos mots de passe ne sont **jamais stockés en clair**. Ils sont protégés par :
- Algorithme : **PBKDF2-HMAC-SHA256**
- Sel aléatoire : **16 octets** généré à chaque inscription
- Itérations : **100 000** (standard recommandé par NIST)

Même les administrateurs de la plateforme ne peuvent pas lire votre mot de passe.

---

## 4. Base légale du traitement

Le traitement de vos données est fondé sur **votre consentement** au moment de la création
de votre compte (art. 6(1)(a) RGPD) et sur l'**intérêt légitime** de fournir un service
pédagogique fonctionnel.

---

## 5. Hébergement des données

Les données sont hébergées sur **Supabase Cloud** (infrastructure PostgreSQL)
conforme aux standards de sécurité SOC 2 et ISO 27001.

---

## 6. Vos droits (RGPD)

Conformément au Règlement Général sur la Protection des Données, vous disposez des droits :

- **Droit d'accès** : consulter vos données (onglet Paramètres)
- **Droit de rectification** : modifier votre nom d'utilisateur
- **Droit à l'effacement** : supprimer votre compte et toutes vos données (onglet Paramètres → Supprimer le Compte)
- **Droit à la portabilité** : exporter votre historique (onglet Portefeuille → Télécharger CSV)

---

## 7. Contact

Pour toute question relative à la protection de vos données, contactez l'équipe
via le dépôt GitHub du projet.
""")

#TAB 2 — Conditions d'Utilisation
with tab_cgu:
    st.header("Conditions Générales d'Utilisation")
    st.caption("Dernière mise à jour : 1er janvier 2026")

    st.markdown("""
## 1. Objet

TradeDesk est un **simulateur boursier pédagogique** permettant aux utilisateurs
de s'initier aux marchés financiers dans un environnement fictif, sans risque financier réel.
En créant un compte, vous acceptez les présentes Conditions Générales d'Utilisation (CGU).

---

## 2. Nature du service

TradeDesk est un outil de **paper trading** (trading fictif) :

- Toutes les transactions sont simulées avec de l'argent virtuel
- Aucune transaction financière réelle n'est effectuée
- Les cours sont fournis par **Yahoo Finance** (yfinance) avec un léger décalage
- Les données de marché sont fournies à titre informatif uniquement

---

## 3. Absence de conseil financier

> ⚠️ **TradeDesk ne fournit PAS de conseils en investissement financier.**

Les informations, analyses, indicateurs et recommandations affichés sur TradeDesk
sont fournis **à titre pédagogique uniquement**. Ils ne constituent pas :
- Des conseils en investissement au sens de la directive MiFID II
- Des recommandations personnalisées d'achat ou de vente
- Une garantie de performance future

**Toute décision d'investissement réel est de votre entière responsabilité.**
Consultez un conseiller financier agréé (CIF) pour vos placements réels.

---

## 4. Compte utilisateur

- Vous êtes responsable de la confidentialité de vos identifiants
- Un compte par personne est autorisé
- Tout usage abusif, frauduleux ou malveillant entraînera la suppression du compte

---

## 5. Limites de responsabilité

TradeDesk ne saurait être tenu responsable :
- Des décisions financières prises sur la base de la simulation
- D'interruptions temporaires du service (maintenance, pannes)
- D'inexactitudes dans les données de marché fournies par Yahoo Finance
- De toute perte financière résultant d'un mauvais usage du simulateur

---

## 6. Propriété intellectuelle

Le code source de TradeDesk est soumis aux droits d'auteur des développeurs.
La reproduction ou distribution sans autorisation est interdite.

---

## 7. Modification des CGU

Nous nous réservons le droit de modifier ces conditions à tout moment.
Les utilisateurs seront informés via la plateforme lors de leur prochaine connexion.

---

## 8. Droit applicable

Les présentes CGU sont régies par le **droit français**.
Tout litige relève de la compétence exclusive des tribunaux français.
""")

#TAB 3 — Mentions Légales
with tab_mentions:
    st.header("Mentions Légales")
    st.caption("Conformément à la loi n° 2004-575 du 21 juin 2004 (LCEN)")

    st.markdown("""
## 1. Éditeur du site

**TradeDesk** est un projet développé dans le cadre pédagogique du cursus
**L1 Informatique** — année académique 2025–2026.

- **Nature** : Application web pédagogique (simulateur boursier)
- **Statut** : Projet étudiant non commercial
- **Hébergement** : Streamlit Community Cloud — [streamlit.io](https://streamlit.io)

---

## 2. Hébergeur

**Streamlit Inc.**
651 N. Broad St., Suite 201
Middletown, Delaware 19709
États-Unis

**Supabase Inc.** (base de données)
970 Toa Payoh North #07-04
Singapore 318992

---

## 3. Technologies utilisées

| Technologie | Usage |
|---|---|
| Python 3.11 | Langage principal |
| Streamlit | Interface web |
| PostgreSQL / Supabase | Base de données cloud |
| yfinance | Données de marché (Yahoo Finance) |
| Plotly | Visualisations graphiques |
| scikit-learn | Machine Learning (Bot trading) |
| C++ / ctypes | Moteur de calcul haute performance |
| PBKDF2-SHA256 | Hachage des mots de passe |

---

## 4. Données de marché

Les cours boursiers et données financières sont fournis par **Yahoo Finance**
via la bibliothèque open-source `yfinance`. Ces données peuvent présenter :
- Un décalage de 15 à 20 minutes par rapport aux marchés réels
- Des interruptions lors de la fermeture des marchés
- Des inexactitudes ponctuelles

TradeDesk décline toute responsabilité quant à l'exactitude de ces données.

---

## 5. Cookies

TradeDesk n'utilise **aucun cookie tiers** à des fins publicitaires ou de tracking.
Les seules données de session sont stockées localement par Streamlit pour maintenir
votre connexion (cookies de session techniques, nécessaires au fonctionnement).

---

## 6. Accessibilité

Ce projet vise à respecter les bonnes pratiques d'accessibilité web.
Toute suggestion d'amélioration est la bienvenue via le dépôt GitHub.

---

## 7. Signalement de vulnérabilité

Si vous découvrez une faille de sécurité, merci de la signaler
de façon responsable via le dépôt GitHub (issue privée ou contact direct).
""")

    #Séparateur et retour
    st.divider()
    st.info("Pour revenir à l'application, utilisez le menu de navigation à gauche.")
