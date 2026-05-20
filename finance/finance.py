import os
import ctypes

# Détermination du chemin absolu de la bibliothèque partagée C++
dir_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.join(dir_path, "engine.so")

try:
    # Chargement de la bibliothèque partagée
    _lib = ctypes.CDLL(lib_path)
    
    # 1. total_brut
    _lib.total_brut.argtypes = [ctypes.c_int, ctypes.c_double]
    _lib.total_brut.restype = ctypes.c_double
    
    # 2. calculer_commission
    _lib.calculer_commission.argtypes = [ctypes.c_double, ctypes.c_double]
    _lib.calculer_commission.restype = ctypes.c_double
    
    # 3. total_net_achat
    _lib.total_net_achat.argtypes = [ctypes.c_int, ctypes.c_double]
    _lib.total_net_achat.restype = ctypes.c_double
    
    # 4. total_net_vente
    _lib.total_net_vente.argtypes = [ctypes.c_int, ctypes.c_double]
    _lib.total_net_vente.restype = ctypes.c_double
    
    # 5. calculer_performance
    _lib.calculer_performance.argtypes = [ctypes.c_double, ctypes.c_double]
    _lib.calculer_performance.restype = ctypes.c_double
    
except Exception as e:
    raise RuntimeError(f"Impossible de charger la bibliothèque C++ engine.so à {lib_path}. Erreur : {e}")

def total_brut(nb_trades: int, prix: float) -> float:
    """Calcul du total brut en euros pour un trade (quantité * prix)"""
    res = _lib.total_brut(nb_trades, float(prix))
    if res == -1.0:
        raise ValueError("Paramètres invalides pour le calcul brut (doivent être > 0)")
    return res

def calculer_commission(prix: float, nb_trades: float) -> float:
    """Calcul de la commission de transaction (1%)"""
    res = _lib.calculer_commission(float(prix), float(nb_trades))
    if res == -1.0:
        raise ValueError("Paramètres invalides pour le calcul de la commission (doivent être > 0)")
    return res

def total_net_achat(nb_trades: int, prix_achat: float) -> float:
    """Calcul du coût total net d'achat (brut + commission)"""
    res = _lib.total_net_achat(nb_trades, float(prix_achat))
    if res == -1.0:
        raise ValueError("Paramètres invalides pour le calcul net d'achat (doivent être > 0)")
    return res

def total_net_vente(nb_trades: int, prix_vente: float) -> float:
    """Calcul du montant net reçu après vente (brut - commission)"""
    res = _lib.total_net_vente(nb_trades, float(prix_vente))
    if res == -1.0:
        raise ValueError("Paramètres invalides pour le calcul net de vente (doivent être > 0)")
    return res

def calculer_performance(prix_achat: float, prix_vente: float) -> float:
    """Calcule le ROI en % : ((prix_vente - prix_achat) / prix_achat) * 100"""
    res = _lib.calculer_performance(float(prix_achat), float(prix_vente))
    if res == -1.0:
        raise ValueError("Prix d'achat invalide pour le calcul de performance (doit être > 0)")
    return res
