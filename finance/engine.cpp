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
    /* Calcul SMA rapide en C++ */
    void calculate_sma_cpp(const double* prices, int n, int window, double* out_sma) {
        for (int i = 0; i < n; i++) {
            if (i < window - 1) {
                out_sma[i] = 0.0;
            } else {
                double sum = 0.0;
                for (int j = 0; j < window; j++) {
                    sum += prices[i - j];
                }
                out_sma[i] = sum / window;
            }
        }
    }

    /* 
       Optimisation Grid Search pour les hyperparamètres (SMA) en C++ 
       Cette fonction génère l'Equity Curve pour des centaines de combinaisons
       et retourne le meilleur rendement absolu tout en renseignant best_short et best_long.
    */
    double grid_search_sma_cpp(const double* prices, int n, int* best_short, int* best_long) {
        double max_return = -999999.0;
        int opt_short = 5;
        int opt_long = 15;

        double* sma_s = new double[n];
        double* sma_l = new double[n];

        // Grid search: tester SMA courte [5 à 20] et SMA longue [21 à 60]
        for (int sw = 5; sw <= 20; sw++) {
            calculate_sma_cpp(prices, n, sw, sma_s);
            for (int lw = 21; lw <= 60; lw++) {
                calculate_sma_cpp(prices, n, lw, sma_l);

                // Simulation de l'Equity Curve
                double initial_cash = 10000.0;
                double cash = initial_cash;
                double position = 0.0;
                double commission_rate = 0.01; // 1%

                for (int i = lw; i < n; i++) {
                    if (sma_s[i] > sma_l[i] && position == 0.0) {
                        // Signal d'Achat
                        double brut_val = cash / (1.0 + commission_rate);
                        position = brut_val / prices[i];
                        cash = 0.0;
                    } else if (sma_s[i] < sma_l[i] && position > 0.0) {
                        // Signal de Vente
                        double brut_val = position * prices[i];
                        double commission = brut_val * commission_rate;
                        cash = brut_val - commission;
                        position = 0.0;
                    }
                }
                
                // Valeur finale du portefeuille
                double final_value = cash + (position * prices[n-1]);
                double ret = ((final_value - initial_cash) / initial_cash) * 100.0;

                if (ret > max_return) {
                    max_return = ret;
                    opt_short = sw;
                    opt_long = lw;
                }
            }
        }

        delete[] sma_s;
        delete[] sma_l;

        if (best_short) *best_short = opt_short;
        if (best_long) *best_long = opt_long;

        return max_return;
    }

    /* Calcul du RSI rapide en C++ (méthode de moyenne mobile simple pour coller au Python) */
    void calculate_rsi_cpp(const double* prices, int n, int window, double* out_rsi) {
        if (n <= window) {
            for (int i = 0; i < n; i++) out_rsi[i] = 50.0;
            return;
        }
        for (int i = 0; i < window; i++) out_rsi[i] = 50.0;
        
        for (int i = window; i < n; i++) {
            double gain = 0.0, loss = 0.0;
            for (int j = 0; j < window; j++) {
                double diff = prices[i - j] - prices[i - j - 1];
                if (diff > 0) gain += diff;
                else loss -= diff;
            }
            gain /= window;
            loss /= window;
            
            if (loss == 0.0) out_rsi[i] = 100.0;
            else {
                double rs = gain / loss;
                out_rsi[i] = 100.0 - (100.0 / (1.0 + rs));
            }
        }
    }

    /* Grid Search Optimisation pour l'hyperparamètre RSI en C++ */
    double grid_search_rsi_cpp(const double* prices, int n, int* best_window, int* best_oversold, int* best_overbought) {
        double max_return = -999999.0;
        int opt_w = 14;
        int opt_os = 30;
        int opt_ob = 70;
        
        double* rsi = new double[n];
        
        // Tester fenêtre [5 à 21], Survente [20 à 40], Surachat [60 à 80]
        for (int w = 5; w <= 21; w++) {
            calculate_rsi_cpp(prices, n, w, rsi);
            
            for (int os = 20; os <= 40; os += 5) {
                for (int ob = 60; ob <= 80; ob += 5) {
                    double initial_cash = 10000.0;
                    double cash = initial_cash;
                    double position = 0.0;
                    double commission_rate = 0.01;
                    
                    for (int i = w; i < n; i++) {
                        if (rsi[i] < os && position == 0.0) {
                            // Achat
                            double brut_val = cash / (1.0 + commission_rate);
                            position = brut_val / prices[i];
                            cash = 0.0;
                        } else if (rsi[i] > ob && position > 0.0) {
                            // Vente
                            double brut_val = position * prices[i];
                            double commission = brut_val * commission_rate;
                            cash = brut_val - commission;
                            position = 0.0;
                        }
                    }
                    double final_value = cash + (position * prices[n-1]);
                    double ret = ((final_value - initial_cash) / initial_cash) * 100.0;
                    
                    if (ret > max_return) {
                        max_return = ret;
                        opt_w = w;
                        opt_os = os;
                        opt_ob = ob;
                    }
                }
            }
        }
        delete[] rsi;
        if (best_window) *best_window = opt_w;
        if (best_oversold) *best_oversold = opt_os;
        if (best_overbought) *best_overbought = opt_ob;
        return max_return;
    }
}
