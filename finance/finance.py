"""
finance.py — Wrapper Python du moteur financier C++ via ctypes
============================================================

Ce module sert d'interface entre Python et la bibliothèque dynamique C++ (engine).
Il implémente :
1. La détection du système d'exploitation et la compilation automatique de engine.cpp.
2. Le chargement dynamique de la bibliothèque via ctypes.
3. Des fonctions wrappers en Python avec un fallback automatique écrit en Python pur
   si le compilateur C++ ou le binaire n'est pas disponible.

Relations avec les autres modules :
----------------------------------
- engine.cpp : le code source C++ compilé par ce module.
- equities.py : utilise les fonctions de coût et de commission pour les portefeuilles.
- Portefeuille.py & Options_3D.py : appellent le pricing d'options Black-Scholes.
"""

import os
import sys
import platform
import subprocess
import ctypes
import math
import warnings

# Détermination du chemin absolu de la bibliothèque partagée C++
dir_path = os.path.dirname(os.path.realpath(__file__))
cpp_path = os.path.join(dir_path, "engine.cpp")

# Nom de fichier de la bibliothèque selon le système d'exploitation
system = platform.system()
if system == "Windows":
    lib_name = "engine.dll"
elif system == "Darwin":  # macOS
    lib_name = "engine.dylib"
else:  # Linux et autres
    lib_name = "engine.so"

lib_path = os.path.join(dir_path, lib_name)

def compile_library():
    """Tente de compiler engine.cpp pour la plateforme actuelle"""
    if not os.path.exists(cpp_path):
        return False
    
    # On cherche un compilateur g++ ou clang++
    compilers = ["g++", "clang++"]
    for compiler in compilers:
        try:
            # -fPIC est requis sur Unix, optionnel/ignoré sur Windows
            cmd = [compiler, "-shared", "-fPIC", "-o", lib_path, cpp_path]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if result.returncode == 0 and os.path.exists(lib_path):
                return True
        except Exception:
            continue
    return False

_lib = None
use_fallback = False

# 1. Tentative de chargement / compilation de la bibliothèque
try:
    if not os.path.exists(lib_path):
        compile_library()
    
    if os.path.exists(lib_path):
        _lib = ctypes.CDLL(lib_path)
    else:
        # Si le fichier compilé pour la plateforme n'existe pas,
        # on tente de charger un éventuel engine.so présent par défaut
        alt_lib_path = os.path.join(dir_path, "engine.so")
        if os.path.exists(alt_lib_path):
            _lib = ctypes.CDLL(alt_lib_path)
        else:
            raise FileNotFoundError("Bibliothèque C++ introuvable et compilation impossible")
except Exception:
    # Si le chargement échoue (ex: mauvaise architecture), on tente une recompilation forcée
    try:
        if os.path.exists(lib_path):
            try:
                os.remove(lib_path)
            except Exception:
                pass
        
        if compile_library():
            _lib = ctypes.CDLL(lib_path)
        else:
            use_fallback = True
    except Exception:
        use_fallback = True

# 2. Configuration des types ctypes ou activation du fallback
if not use_fallback and _lib is not None:
    try:
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

        # 6. black_scholes_pricing_cpp
        _lib.black_scholes_pricing_cpp.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double,
            ctypes.c_double, ctypes.c_double, ctypes.c_int
        ]
        _lib.black_scholes_pricing_cpp.restype = ctypes.c_double
    except Exception:
        use_fallback = True
else:
    use_fallback = True

if use_fallback:
    warnings.warn(
        "Impossible de charger ou de compiler la bibliothèque C++ engine. "
        "Utilisation de la version de secours pure Python.",
        RuntimeWarning
    )

# ── Version de secours en Python Pur (Fallback) ────────────────────────────────

def _normal_cdf_py(x: float) -> float:
    """Calcul de la CDF normale standard avec math.erfc."""
    return 0.5 * math.erfc(-x * math.sqrt(0.5))

def _black_scholes_pricing_py(S: float, K: float, T: float, r: float, sigma: float, is_call: int) -> float:
    """Calcul de secours de Black-Scholes en Python."""
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if is_call != 0:
        return S * _normal_cdf_py(d1) - K * math.exp(-r * T) * _normal_cdf_py(d2)
    else:
        return K * math.exp(-r * T) * _normal_cdf_py(-d2) - S * _normal_cdf_py(-d1)

# ── Wrappers Python Exposés ──────────────────────────────────────────────────

def total_brut(nb_trades: int, prix: float) -> float:
    """Calcul du total brut en euros pour un trade (quantité * prix)"""
    if use_fallback:
        if nb_trades <= 0 or prix <= 0:
            raise ValueError("Paramètres invalides pour le calcul brut (doivent être > 0)")
        return float(nb_trades * prix)
    
    res = _lib.total_brut(nb_trades, float(prix))
    if res == -1.0:
        raise ValueError("Paramètres invalides pour le calcul brut (doivent être > 0)")
    return res

def calculer_commission(prix: float, nb_trades: float) -> float:
    """Calcul de la commission de transaction (1%)"""
    if use_fallback:
        if nb_trades <= 0 or prix <= 0:
            raise ValueError("Paramètres invalides pour le calcul de la commission (doivent être > 0)")
        return float(prix * nb_trades * 0.01)
    
    res = _lib.calculer_commission(float(prix), float(nb_trades))
    if res == -1.0:
        raise ValueError("Paramètres invalides pour le calcul de la commission (doivent être > 0)")
    return res

def total_net_achat(nb_trades: int, prix_achat: float) -> float:
    """Calcul du coût total net d'achat (brut + commission)"""
    if use_fallback:
        if nb_trades <= 0 or prix_achat <= 0:
            raise ValueError("Paramètres invalides pour le calcul net d'achat (doivent être > 0)")
        brut = float(nb_trades * prix_achat)
        commission = float(brut * 0.01)
        return brut + commission
    
    res = _lib.total_net_achat(nb_trades, float(prix_achat))
    if res == -1.0:
        raise ValueError("Paramètres invalides pour le calcul net d'achat (doivent être > 0)")
    return res

def total_net_vente(nb_trades: int, prix_vente: float) -> float:
    """Calcul du montant net reçu après vente (brut - commission)"""
    if use_fallback:
        if nb_trades <= 0 or prix_vente <= 0:
            raise ValueError("Paramètres invalides pour le calcul net de vente (doivent être > 0)")
        brut = float(nb_trades * prix_vente)
        commission = float(brut * 0.01)
        return brut - commission
    
    res = _lib.total_net_vente(nb_trades, float(prix_vente))
    if res == -1.0:
        raise ValueError("Paramètres invalides pour le calcul net de vente (doivent être > 0)")
    return res

def calculer_performance(prix_achat: float, prix_vente: float) -> float:
    """Calcule le ROI en % : ((prix_vente - prix_achat) / prix_achat) * 100"""
    if use_fallback:
        if prix_achat <= 0:
            raise ValueError("Prix d'achat invalide pour le calcul de performance (doit être > 0)")
        return float(((prix_vente - prix_achat) / prix_achat) * 100)
    
    res = _lib.calculer_performance(float(prix_achat), float(prix_vente))
    if res == -1.0:
        raise ValueError("Prix d'achat invalide pour le calcul de performance (doit être > 0)")
    return res

def pricing_option_bs(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """
    Calcule le prix d'une option européenne via le moteur C++ (ou fallback Python).
    S : Cours du sous-jacent
    K : Strike
    T : Maturité (années)
    r : Taux sans risque
    sigma : Volatilité
    option_type : 'call' ou 'put'
    """
    is_call = 1 if option_type.lower() == "call" else 0
    if use_fallback:
        return _black_scholes_pricing_py(S, K, T, r, sigma, is_call)
    
    return _lib.black_scholes_pricing_cpp(float(S), float(K), float(T), float(r), float(sigma), is_call)
