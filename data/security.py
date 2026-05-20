"""
security.py — Outils de sécurité pour l'authentification (Hachage de mot de passe)
=============================================================================

Ce module fournit des fonctions pour hacher et vérifier les mots de passe de manière
sécurisée en utilisant PBKDF2-HMAC-SHA256, disponible nativement en Python.
Il évite l'utilisation de dépendances C externes (comme bcrypt ou argon2) qui pourraient
être difficiles à compiler sur certaines plateformes.

Relations avec les autres modules :
----------------------------------
- database.py : Stocke les hachages générés par ce module dans la table `users`.
- web.py : Appelle ces fonctions lors de l'inscription et de la connexion des utilisateurs.
"""

import hashlib
import hmac
import os

def hash_password(password: str) -> str:
    """
    Génère un sel de 16 octets et hache le mot de passe avec PBKDF2-HMAC-SHA256.
    Retourne une chaîne formatée : 'sel_hex:hachage_hex'.
    """
    salt = os.urandom(16)
    # 100 000 itérations est le standard recommandé pour PBKDF2 avec SHA-256
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{key.hex()}"

def verify_password(stored_hash: str, provided_password: str) -> bool:
    """
    Vérifie si le mot de passe fourni correspond au hachage stocké en base de données.
    """
    try:
        if not stored_hash or ":" not in stored_hash:
            return False
        salt_hex, key_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        # compare_digest évite les timing attacks (temps constant quelle que soit la différence)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False
