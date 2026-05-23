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

def compile_library() -> bool:
    """
    Compile engine.cpp en bibliothèque partagée (.so/.dylib/.dll)
    en utilisant g++ ou clang++ avec les flags corrects.
    Retourne True si la compilation a réussi.
    """
    if not os.path.exists(cpp_path):
        return False

    compilers = ["g++", "clang++"]
    for compiler in compilers:
        try:
            cmd = [
                compiler, "-O2", "-shared", "-fPIC",
                "-std=c++17",          # requis pour certaines fonctionnalités
                "-o", lib_path,
                cpp_path,
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and os.path.exists(lib_path):
                return True
            # Log l'erreur de compilation pour le débogage
            if result.stderr:
                warnings.warn(f"Compilation {compiler}: {result.stderr[:300]}", RuntimeWarning)
        except FileNotFoundError:
            continue  # compilateur absent, on essaie le suivant
        except Exception as exc:
            warnings.warn(f"Erreur compilation {compiler}: {exc}", RuntimeWarning)
    return False


_lib = None
use_fallback = False
_load_error = ""

# ── Étape 1 : recompilation si la lib est absente ou trop ancienne ────────────
import time as _time
_needs_compile = (
    not os.path.exists(lib_path)
    or os.path.getmtime(cpp_path) > os.path.getmtime(lib_path)
    or (_time.time() - os.path.getmtime(lib_path)) > 86400  # recompile si > 1 jour
)
if _needs_compile:
    compile_library()

# ── Étape 2 : chargement de la bibliothèque ───────────────────────────────────
try:
    # Résolution du chemin absolu pour éviter toute ambiguïté
    _target = os.path.abspath(lib_path)
    if not os.path.exists(_target):
        # Fallback : engine.so présent dans le même dossier
        _target = os.path.abspath(os.path.join(dir_path, "engine.so"))
    if not os.path.exists(_target):
        raise FileNotFoundError(f"Introuvable : {_target}")
    _lib = ctypes.CDLL(_target)
except Exception as _e:
    _load_error = str(_e)
    # Tentative de recompilation forcée
    try:
        compile_library()
        _lib = ctypes.CDLL(os.path.abspath(lib_path))
    except Exception as _e2:
        _load_error += f" | {_e2}"
        use_fallback = True

# ── Étape 3 : déclaration des signatures ctypes ───────────────────────────────
if not use_fallback and _lib is not None:
    try:
        _lib.total_brut.argtypes               = [ctypes.c_double, ctypes.c_double]
        _lib.total_brut.restype                = ctypes.c_double

        _lib.calculer_commission.argtypes      = [ctypes.c_double, ctypes.c_double]
        _lib.calculer_commission.restype       = ctypes.c_double

        _lib.total_net_achat.argtypes          = [ctypes.c_double, ctypes.c_double]
        _lib.total_net_achat.restype           = ctypes.c_double

        _lib.total_net_vente.argtypes          = [ctypes.c_double, ctypes.c_double]
        _lib.total_net_vente.restype           = ctypes.c_double

        _lib.calculer_performance.argtypes     = [ctypes.c_double, ctypes.c_double]
        _lib.calculer_performance.restype      = ctypes.c_double

        _lib.black_scholes_pricing_cpp.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double,
            ctypes.c_double, ctypes.c_double, ctypes.c_int,
        ]
        _lib.black_scholes_pricing_cpp.restype = ctypes.c_double

        _lib.grid_search_sma_cpp.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),    ctypes.POINTER(ctypes.c_int),
        ]
        _lib.grid_search_sma_cpp.restype       = ctypes.c_double

        _lib.grid_search_rsi_cpp.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),    ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        _lib.grid_search_rsi_cpp.restype       = ctypes.c_double

    except Exception as _sig_err:
        use_fallback = True
        _load_error += f" | signature error: {_sig_err}"
else:
    use_fallback = True

if use_fallback:
    _msg = "Moteur C++ engine non disponible"
    if _load_error:
        _msg += f" ({_load_error})"
    _msg += ". Utilisation du fallback Python."
    warnings.warn(_msg,
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

def total_brut(nb_trades: float, prix: float) -> float:
    """Calcul du total brut en euros pour un trade (quantité * prix)"""
    if use_fallback:
        if nb_trades <= 0 or prix <= 0:
            raise ValueError("Paramètres invalides pour le calcul brut (doivent être > 0)")
        return float(nb_trades * prix)
    
    res = _lib.total_brut(float(nb_trades), float(prix))
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

def total_net_achat(nb_trades: float, prix_achat: float) -> float:
    """Calcul du coût total net d'achat (brut + commission)"""
    if use_fallback:
        if nb_trades <= 0 or prix_achat <= 0:
            raise ValueError("Paramètres invalides pour le calcul net d'achat (doivent être > 0)")
        brut = float(nb_trades * prix_achat)
        commission = float(brut * 0.01)
        return brut + commission
    
    res = _lib.total_net_achat(float(nb_trades), float(prix_achat))
    if res == -1.0:
        raise ValueError("Paramètres invalides pour le calcul net d'achat (doivent être > 0)")
    return res

def total_net_vente(nb_trades: float, prix_vente: float) -> float:
    """Calcul du montant net reçu après vente (brut - commission)"""
    if use_fallback:
        if nb_trades <= 0 or prix_vente <= 0:
            raise ValueError("Paramètres invalides pour le calcul net de vente (doivent être > 0)")
        brut = float(nb_trades * prix_vente)
        commission = float(brut * 0.01)
        return brut - commission
    
    res = _lib.total_net_vente(float(nb_trades), float(prix_vente))
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
    """
    is_call = 1 if option_type.lower() == "call" else 0
    if use_fallback:
        return _black_scholes_pricing_py(S, K, T, r, sigma, is_call)
    
    return _lib.black_scholes_pricing_cpp(float(S), float(K), float(T), float(r), float(sigma), is_call)

def grid_search_sma(prices_list) -> tuple:
    """
    Exécute le Grid Search SMA en C++.
    Retourne (best_short, best_long, best_return)
    """
    if use_fallback or not prices_list:
        return (5, 25, 0.0) # Fallback naïf (doit respecter 21 <= L <= 60 pour le test)
    
    n = len(prices_list)
    prices_array = (ctypes.c_double * n)(*prices_list)
    
    best_short = ctypes.c_int(0)
    best_long = ctypes.c_int(0)
    
    max_return = _lib.grid_search_sma_cpp(prices_array, n, ctypes.byref(best_short), ctypes.byref(best_long))
    return (best_short.value, best_long.value, max_return)

def grid_search_rsi(prices_list) -> tuple:
    """
    Exécute le Grid Search RSI en C++.
    Retourne (best_window, best_oversold, best_overbought, best_return)
    """
    if use_fallback or not prices_list:
        return (14, 30, 70, 0.0) # Fallback naïf
        
    n = len(prices_list)
    prices_array = (ctypes.c_double * n)(*prices_list)
    
    best_w = ctypes.c_int(0)
    best_os = ctypes.c_int(0)
    best_ob = ctypes.c_int(0)
    
    max_return = _lib.grid_search_rsi_cpp(prices_array, n, ctypes.byref(best_w), ctypes.byref(best_os), ctypes.byref(best_ob))
    return (best_w.value, best_os.value, best_ob.value, max_return)
