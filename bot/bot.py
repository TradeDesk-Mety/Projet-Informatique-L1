""
bot.py — Moteur du robot de trading automatique (SMA, RSI, VWAP et Machine Learning)
=====================================================================================

Ce module définit la classe TradingBot qui exécute périodiquement des algorithmes
de trading automatique sur le portefeuille de l'utilisateur connecté.
Il intègre 4 stratégies :
  1. SMA  : Croisement de Moyennes Mobiles (trend following classique).
  2. RSI  : Oscillateur surachat/survente (mean reversion).
  3. VWAP : Prix Moyen Pondéré par Volume (référence institutionnelle).
  4. ML_RF: Random Forest Classifier avec Grid Search C++ pour l'optimisation.

Relations avec les autres modules :
----------------------------------
- data.data         : Récupère les historiques de prix depuis Yahoo Finance.
- simulation.simulation : Calcule les indicateurs techniques (RSI, SMA).
- equities.equities : Exécute les ordres d'achat/vente sur le portefeuille.
- 4_🤖_Bot.py       : Contrôle l'état du bot dans l'interface Streamlit.
"""

import time
from datetime import datetime
import pandas as pd
import numpy as np
from equities.equities import Portfolio
import data.data as data
import simulation.simulation as sim

class TradingBot:
    def __init__(self, portfolio: Portfolio, strategy: str = "SMA"):
        self.portfolio = portfolio
        self.strategy = strategy  # "SMA", "RSI", "VWAP" ou "ML_RF"
        self.is_running = False
        self.logs = []

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")

    def run_one_iteration(self, ticker_name: str, period: str = "1mo", interval: str = "1d") -> str:
        """
        Exécute une seule décision de trading basée sur les cours actuels et historiques.
        """
        self.log(f"Évaluation du marché pour {ticker_name} avec la stratégie {self.strategy}...")
        
        try:
            # Récupération historique pour calculer l'indicateur
            df = data.recuperer_historique(ticker_name, period, interval)
            if df.empty or len(df) < 10:
                self.log(f"Données insuffisantes pour {ticker_name}.")
                return "Données insuffisantes."
            
            close_prices = df['Close']
            current_price = close_prices.iloc[-1]
            
            # Évaluation des signaux
            signal = 0  # 0 = Hold, 1 = Buy, -1 = Sell
            
            if self.strategy == "SMA":
                # =====================================================================
                # STRATÉGIE SMA (Simple Moving Average / Croisement de Moyennes Mobiles)
                # =====================================================================
                # Cette stratégie classique repose sur le suivi de tendance (trend following).
                # Elle utilise deux moyennes mobiles de durées différentes :
                # 1. Une Moyenne Mobile Courte (ici 5 périodes) : Très réactive aux prix récents.
                # 2. Une Moyenne Mobile Longue (ici 15 périodes) : Plus lente, elle indique la tendance de fond.
                #
                # Le principe de décision (Signaux de trading) :
                # - Signal d'ACHAT (1) : Lorsque la SMA courte croise la SMA longue à la hausse. 
                #   Cela indique une dynamique haussière à court terme qui prend le dessus sur la tendance de fond.
                # - Signal de VENTE (-1) : Lorsque la SMA courte croise la SMA longue à la baisse. 
                #   Cela indique un essoufflement et une dynamique baissière.
                # =====================================================================
                sma_short = sim.calculate_sma(close_prices, 5).iloc[-1]
                sma_long = sim.calculate_sma(close_prices, 15).iloc[-1]
                self.log(f"SMA(5): {sma_short:.2f} | SMA(15): {sma_long:.2f} | Cours: {current_price:.2f}")
                if sma_short > sma_long:
                    signal = 1
                elif sma_short < sma_long:
                    signal = -1
                    
            elif self.strategy == "RSI":
                # =====================================================================
                # STRATÉGIE RSI (Relative Strength Index / Indice de Force Relative)
                # =====================================================================
                # Le RSI est un oscillateur borné entre 0 et 100 qui mesure la vélocité 
                # et l'ampleur des mouvements directionnels des prix. 
                # Il sert principalement à repérer les zones de surachat et de survente.
                #
                # Le principe de décision (Signaux de trading) :
                # - Zone de SURVENTE (RSI < 35) : Le marché a subi une forte pression vendeuse. 
                #   L'actif est statistiquement "sous-évalué" temporairement. Signal d'ACHAT (1) pour jouer le rebond.
                # - Zone de SURACHAT (RSI > 65) : Le marché a subi une forte pression acheteuse. 
                #   L'actif est potentiellement "surévalué" temporairement. Signal de VENTE (-1) pour sécuriser les gains.
                # =====================================================================
                rsi_val = sim.calculate_rsi(close_prices, 7).iloc[-1]
                self.log(f"RSI(7): {rsi_val:.2f} | Cours: {current_price:.2f}")
                if rsi_val < 35:
                    signal = 1
                elif rsi_val > 65:
                    signal = -1

            elif self.strategy == "VWAP":
                # =====================================================================
                # STRATÉGIE VWAP (Volume Weighted Average Price / Prix Moyen Pondéré)
                # =====================================================================
                # Le VWAP est LA référence d'exécution des traders institutionnels.
                # Il représente le prix moyen auquel un actif a été échangé sur une
                # période, pondéré par le volume de chaque transaction.
                #
                # Formule : VWAP = Σ(Prix_Typique × Volume) / Σ(Volume)
                # avec Prix_Typique = (High + Low + Close) / 3
                #
                # Le principe de décision (Signaux de trading) :
                # - Signal d'ACHAT (1) : Si le cours est SOUS le VWAP de plus de 2%.
                #   L'actif est sous-évalué par rapport au prix moyen de consensus.
                #   Les acheteurs institutionnels utilisent ce signal pour rentrer.
                # - Signal de VENTE (-1) : Si le cours est AU-DESSUS du VWAP de plus de 2%.
                #   L'actif est surévalué. C'est le moment de prendre ses bénéfices.
                # - NEUTRE (0) : Si le cours est dans la bande ±2% autour du VWAP.
                #   Le prix est équitable, aucun avantage statistique à agir.
                # =====================================================================
                window_vwap = 20  # Fenêtre glissante de 20 jours
                if "High" in df.columns and "Low" in df.columns and "Volume" in df.columns:
                    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
                    cum_tp_vol = (typical_price * df["Volume"]).rolling(window_vwap).sum()
                    cum_vol    = df["Volume"].rolling(window_vwap).sum()
                    vwap_series = cum_tp_vol / cum_vol
                    vwap_val    = vwap_series.iloc[-1]
                else:
                    # Fallback : pas de données de volume, on utilise la SMA20
                    vwap_val = sim.calculate_sma(close_prices, window_vwap).iloc[-1]
                
                deviation_pct = ((current_price - vwap_val) / vwap_val) * 100
                self.log(f"VWAP(20j): {vwap_val:.2f} | Cours: {current_price:.2f} | Écart: {deviation_pct:+.2f}%")
                
                if current_price < vwap_val * 0.98:   # Cours > 2% sous le VWAP
                    signal = 1
                elif current_price > vwap_val * 1.02:  # Cours > 2% au-dessus du VWAP
                    signal = -1
                else:
                    signal = 0
                    
            elif self.strategy == "ML_RF":
                # =====================================================================
                # STRATÉGIE MACHINE LEARNING (Random Forest Classifier)
                # =====================================================================
                # Cette stratégie avancée utilise l'intelligence artificielle pour prédire
                # la direction future des prix (ici, à un horizon de 3 jours).
                #
                # 1. Feature Engineering (Création des variables explicatives) :
                #    L'algorithme ingère plusieurs indicateurs techniques : 
                #    - Rendements à 1, 3, et 5 jours (ret1, ret3, ret5).
                #    - Le ratio entre la SMA(5) et la SMA(15) pour capter la tendance.
                #    - Le RSI (14 périodes) pour capter les niveaux de surachat/survente.
                #    - La volatilité sur 10 jours (vol10) pour mesurer le risque actuel.
                # 
                # 2. Variable Cible (Target) :
                #    On veut prédire si le cours de clôture dans 3 jours sera strictement 
                #    supérieur au cours actuel (1 = Hausse, 0 = Baisse/Stagnation).
                #
                # 3. Entraînement du Modèle :
                #    Un modèle Random Forest (forêt aléatoire) est entraîné sur ces données 
                #    historiques (1 an). Il est robuste, évite le surapprentissage (max_depth=5),
                #    et combine les résultats de 50 arbres de décision (n_estimators=50).
                #
                # 4. Prise de Décision (Seuil Asymétrique) :
                #    Le modèle calcule la probabilité (prob_up) que le marché monte.
                #    - ACHAT (1) : Si le modèle prédit une hausse avec une conviction forte (prob > 55%).
                #    - VENTE (-1) : Si le modèle prédit une baisse avec une conviction forte (prob < 45%).
                #    - NEUTRE (0) : En cas d'incertitude (entre 45% et 55%), on ne fait rien pour éviter le bruit.
                # =====================================================================
                self.log("Entraînement du modèle Random Forest sur l'historique 1 an...")
                # On utilise un historique plus large pour l'entraînement
                df_ml = data.recuperer_historique(ticker_name, "1y", "1d")
                if len(df_ml) < 40:
                    self.log("Historique 1 an insuffisant pour entraîner le modèle (min 40 jours requis).")
                    return "Données insuffisantes."
                
                close_ml = df_ml['Close']
                returns_1d = close_ml.pct_change()
                returns_3d = close_ml.pct_change(3)
                returns_5d = close_ml.pct_change(5)
                
                # ── Grid Search C++ : SMA & RSI ─────────────────────────────────────────────
                prices_list = close_ml.tolist()
                best_short, best_long, ret_sma = fin.grid_search_sma(prices_list)
                best_rsi_w, best_os, best_ob, ret_rsi = fin.grid_search_rsi(prices_list)
                self.log(f"SMA opt: {best_short}/{best_long} | RSI opt: w={best_rsi_w} (S:{best_os}, A:{best_ob})")

                # ── Grid Search Python : Fenêtre VWAP optimale ────────────────────────
                # Cherche la fenêtre VWAP (5←60j) maximisant la corrélation de Pearson
                # entre la distance relative au VWAP et le rendement futur à 3 jours.
                best_vwap_w    = 20
                best_vwap_corr = -1.0
                future_ret3    = close_ml.pct_change(3).shift(-3)
                import numpy as np
                for vw in range(5, 61, 5):
                    try:
                        if "High" in df_ml.columns and "Volume" in df_ml.columns:
                            tp_c = (df_ml["High"] + df_ml["Low"] + df_ml["Close"]) / 3
                            vwap_c = (
                                (tp_c * df_ml["Volume"]).rolling(vw).sum()
                                / df_ml["Volume"].rolling(vw).sum()
                            )
                        else:
                            vwap_c = close_ml.rolling(vw).mean()
                        dist_c = ((close_ml - vwap_c) / vwap_c).dropna()
                        corr   = abs(float(dist_c.corr(future_ret3)))
                        if corr > best_vwap_corr and not np.isnan(corr):
                            best_vwap_corr = corr
                            best_vwap_w    = vw
                    except Exception:
                        continue
                self.log(f"VWAP opt: fenêtre={best_vwap_w}j (corr Pearson={best_vwap_corr:.3f})")

                # ── Feature Engineering (7 features) ─────────────────────────────────
                sma_short_opt = sim.calculate_sma(close_ml, best_short)
                sma_long_opt  = sim.calculate_sma(close_ml, best_long)
                sma_ratio     = sma_short_opt / sma_long_opt
                rsi_opt       = sim.calculate_rsi(close_ml, best_rsi_w)
                vol_10        = returns_1d.rolling(10).std()

                # Distance relative au VWAP optimal
                if "High" in df_ml.columns and "Volume" in df_ml.columns:
                    tp_opt   = (df_ml["High"] + df_ml["Low"] + df_ml["Close"]) / 3
                    vwap_opt = (
                        (tp_opt * df_ml["Volume"]).rolling(best_vwap_w).sum()
                        / df_ml["Volume"].rolling(best_vwap_w).sum()
                    )
                else:
                    vwap_opt = close_ml.rolling(best_vwap_w).mean()
                vwap_dist = (close_ml - vwap_opt) / vwap_opt

                # Construction de la matrice de features X (7 features)
                features = pd.DataFrame({
                    "ret1":      returns_1d,
                    "ret3":      returns_3d,
                    "ret5":      returns_5d,
                    "sma_ratio": sma_ratio,
                    "rsi":       rsi_opt,
                    "vwap_dist": vwap_dist,  # ← feature VWAP optimisée
                    "vol10":     vol_10,
                })
                
                # Target : est-ce que le cours est supérieur dans 3 jours (Horizon de 3 jours) ?
                target = (close_ml.shift(-3) > close_ml).astype(int)
                
                # Préparation du dataset
                dataset = features.copy()
                dataset["target"] = target
                dataset = dataset.dropna()
                
                if len(dataset) < 25:
                    self.log("Données nettoyées insuffisantes après retrait des NaNs.")
                    return "Données insuffisantes."
                
                # Séparation des variables
                X_train = dataset.drop(columns=["target"])
                y_train = dataset["target"]
                
                # Dernière ligne pour la prédiction en direct (on remplit les NaNs éventuels par précaution)
                latest_features = features.iloc[[-1]].ffill().fillna(0.0)
                
                # Importation des modules pour l'évaluation et la calibration
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.model_selection import cross_val_score, StratifiedKFold
                from sklearn.calibration import CalibratedClassifierCV
                
                # 3.1. Modèle de base
                clf_base = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
                
                # 3.2. Vérification de l'Overfitting par Cross-Validation
                # On utilise un StratifiedKFold pour s'assurer que la répartition des hausses/baisses est respectée
                cv_folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                scores = cross_val_score(clf_base, X_train, y_train, cv=cv_folds, scoring='accuracy')
                acc_mean = scores.mean() * 100
                acc_std = scores.std() * 100
                self.log(f"Verification Overfitting (CV 5-Folds): Précision moyenne = {acc_mean:.1f}% (+/- {acc_std:.1f}%)")
                
                # 3.3. Algorithme de Calibration (Platt Scaling)
                # CalibratedClassifierCV vérifie et ajuste la distribution des probabilités du modèle 
                # pour s'assurer qu'un score de 60% correspond réellement à 60% de chances empiriques.
                clf_calibrated = CalibratedClassifierCV(estimator=clf_base, method='sigmoid', cv=5)
                
                # Entraînement final du modèle calibré sur l'ensemble des données
                clf_calibrated.fit(X_train, y_train)
                
                # 4. Prédiction et probabilités associées (Fiabilisées par la calibration)
                pred = clf_calibrated.predict(latest_features)[0]
                prob = clf_calibrated.predict_proba(latest_features)[0]
                prob_up = prob[1] * 100
                
                self.log(f"ML RF: Probabilité de hausse à 3j = {prob_up:.1f}%")
                
                # Seuil de décision asymétrique (éviter le bruit)
                if pred == 1 and prob_up > 55.0:
                    signal = 1
                elif pred == 0 or prob_up < 45.0:
                    signal = -1
                else:
                    signal = 0
            
            # Application des ordres
            if signal == 1:
                # Signal d'achat : on achète autant que possible
                cash_dispo = self.portfolio.cash
                if cash_dispo < 10:
                    self.log("Fonds insuffisants pour placer un ordre d'achat.")
                    return "Fonds insuffisants."
                
                prix_avec_comm = current_price * 1.01
                qty_to_buy = int(cash_dispo // prix_avec_comm)
                
                if qty_to_buy > 0:
                    self.log(f"Signal ACHAT généré. Achat de {qty_to_buy} unités de {ticker_name} à {current_price:.2f} €.")
                    msg = self.portfolio.buy(ticker_name, qty_to_buy, current_price)
                    self.log(f"Résultat ordre : {msg}")
                    return msg
                else:
                    self.log("Fonds insuffisants pour acheter 1 unité.")
                    return "Fonds insuffisants pour acheter 1 unité."
                    
            elif signal == -1:
                # Signal de vente : on vend tout ce qu'on détient sur cet actif
                if ticker_name in self.portfolio.positions:
                    qty_to_sell = self.portfolio.positions[ticker_name]["quantity"]
                    self.log(f"Signal VENTE généré. Vente de {qty_to_sell} unités de {ticker_name} à {current_price:.2f} €.")
                    msg = self.portfolio.sell(ticker_name, qty_to_sell, current_price)
                    self.log(f"Résultat ordre : {msg}")
                    return msg
                else:
                    self.log(f"Signal VENTE généré mais aucun actif {ticker_name} détenu.")
                    return "Rien à vendre."
            else:
                self.log("Signal NEUTRE. Aucune transaction effectuée.")
                return "Pas de signal."
                
        except Exception as e:
            msg_err = f"Erreur lors de l'exécution du bot : {e}"
            self.log(msg_err)
            return msg_err
