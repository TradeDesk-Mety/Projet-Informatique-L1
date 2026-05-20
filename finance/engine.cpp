#include <iostream>

constexpr double ERROR_CODE = -1.0;
constexpr double COMMISSION=0.01;

extern "C"{

    /*Calcul du total en euros du nombre d'actions acheté = total_brut*/
    double total_brut(int nb_trades, double prix){
        if(nb_trades<=0 || prix <=0){
            return ERROR_CODE;
        }
        return nb_trades * prix;
    }
    /*Calcul de la commission*/
    double calculer_commission(double prix, double nb_trades){
         if(nb_trades<=0 || prix <=0){
            return ERROR_CODE;
        }
        double montant = prix * nb_trades;
        return montant * COMMISSION;
    }

    /*Calcul du total net d'achat  = brut + commission*/
    double total_net_achat(int nb_trades, double prix_achat){
         if(nb_trades<=0 || prix_achat <=0){
            return ERROR_CODE;
        }
        double brut = total_brut(nb_trades,prix_achat);
        double commission = calculer_commission(prix_achat,nb_trades);
        return brut + commission;
    }
    
    /*Calcul du total net de vente = brut - commission*/
    double total_net_vente(int nb_trades, double prix_vente){
        if(nb_trades<=0 || prix_vente<=0){
            return ERROR_CODE;
        }
        double brut = total_brut(nb_trades, prix_vente);
        double commission = calculer_commission(prix_vente,nb_trades);
        return brut - commission;
    }


    /*Calcul le ROI : Return On Investissement*/
    double calculer_performance(double prix_achat, double prix_vente){
        if(prix_achat<=0){
            return ERROR_CODE;
        }
        return ((prix_vente-prix_achat)/prix_achat)*100;
    }
}
