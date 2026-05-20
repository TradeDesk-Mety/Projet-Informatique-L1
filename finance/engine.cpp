/*
================================================================================
engine.cpp — Moteur financier performant en C++ (Calculs financiers et pricing)
================================================================================

Ce module contient les fonctions mathématiques de base et de pricing d'options,
compilées en bibliothèque partagée dynamique (.dll, .so ou .dylib) pour être
exécutées de manière ultra-rapide via ctypes en Python.

Relations avec les autres modules :
----------------------------------
- finance.py : Charge ce fichier compilé sous forme de bibliothèque dynamique,
  définit les types d'arguments et de retour, et offre des fonctions d'accès Python.
- equities.py : Utilise les calculs de coûts et commissions pour le portefeuille.
- Portefeuille.py & Options_3D.py : Utilisent le pricing Black-Scholes pour évaluer les options.
*/

#include <iostream>
#include <cmath>

constexpr double ERROR_CODE = -1.0;
constexpr double COMMISSION = 0.01; // Commission fixe de 1%

// Fonction auxiliaire pour calculer la CDF de la distribution normale standard : N(x)
// Utilise la fonction d'erreur complémentaire (erfc) de la bibliothèque standard <cmath>
inline double normal_cdf(double x) {
    return 0.5 * std::erfc(-x * std::sqrt(0.5));
}

extern "C" {

    /* Calcul du montant brut total (quantité * prix) */
    double total_brut(int nb_trades, double prix) {
        if (nb_trades <= 0 || prix <= 0) {
            return ERROR_CODE;
        }
        return nb_trades * prix;
    }

    /* Calcul de la commission de courtage (1%) */
    double calculer_commission(double prix, double nb_trades) {
        if (nb_trades <= 0 || prix <= 0) {
            return ERROR_CODE;
        }
        double montant = prix * nb_trades;
        return montant * COMMISSION;
    }

    /* Calcul du coût total net lors d'un achat (brut + commission) */
    double total_net_achat(int nb_trades, double prix_achat) {
        if (nb_trades <= 0 || prix_achat <= 0) {
            return ERROR_CODE;
        }
        double brut = total_brut(nb_trades, prix_achat);
        double commission = calculer_commission(prix_achat, nb_trades);
        return brut + commission;
    }
    
    /* Calcul du montant net perçu lors d'une vente (brut - commission) */
    double total_net_vente(int nb_trades, double prix_vente) {
        if (nb_trades <= 0 || prix_vente <= 0) {
            return ERROR_CODE;
        }
        double brut = total_brut(nb_trades, prix_vente);
        double commission = calculer_commission(prix_vente, nb_trades);
        return brut - commission;
    }

    /* Calcul de la performance (ROI en %) */
    double calculer_performance(double prix_achat, double prix_vente) {
        if (prix_achat <= 0) {
            return ERROR_CODE;
        }
        return ((prix_vente - prix_achat) / prix_achat) * 100.0;
    }

    /* 
       Pricing d'une option européenne via la formule de Black-Scholes (1973) 
       S : Cours du sous-jacent
       K : Strike (Prix d'exercice)
       T : Maturité (temps restant en années, ex: 0.25 pour 3 mois)
       r : Taux d'intérêt sans risque (ex: 0.03 pour 3%)
       sigma : Volatilité sous-jacente (ex: 0.20 pour 20%)
       is_call : 1 si option d'achat (Call), 0 si option de vente (Put)
    */
    double black_scholes_pricing_cpp(double S, double K, double T, double r, double sigma, int is_call) {
        if (S <= 0 || K <= 0 || T <= 0 || sigma <= 0) {
            return 0.0;
        }
        
        double d1 = (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * std::sqrt(T));
        double d2 = d1 - sigma * std::sqrt(T);
        
        if (is_call != 0) {
            return S * normal_cdf(d1) - K * std::exp(-r * T) * normal_cdf(d2);
        } else {
            return K * std::exp(-r * T) * normal_cdf(-d2) - S * normal_cdf(-d1);
        }
    }
}
