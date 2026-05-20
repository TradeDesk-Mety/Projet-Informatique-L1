import os
import sys
import time

# Ajouter le dossier parent au chemin d'importation
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from data.database import BRONZE_DB_PATH, SILVER_DB_PATH, GOLD_DB_PATH, PORTFOLIO_DB_PATH, init_db
import data.medallion as med

def main():
    print("============================================================")
    print("   Initialisation & Remplissage des Bases de Données SQL   ")
    print("============================================================")
    print(f"  Bronze   : {BRONZE_DB_PATH}")
    print(f"  Silver   : {SILVER_DB_PATH}")
    print(f"  Gold     : {GOLD_DB_PATH}")
    print(f"  Portfolio: {PORTFOLIO_DB_PATH}")
    print("============================================================")
    
    start_time = time.time()
    
    # 1. Initialiser les schémas des bases de données
    print("\n1. Initialisation des tables SQLite (4 bases)...")
    init_db()
    print("   -> Tables initialisées avec succès (bronze.db, silver.db, gold.db, portfolio.db)")
    
    # 2. Lancer la mise à jour Medallion multi-threadée
    print("\n2. Téléchargement des données de marché en parallèle (Multi-thread)...")
    print("   ⚠️  ~1000 actifs : prévoir 2-5 minutes selon la connexion...")
    
    # Lancement du pipeline sur 20 threads (augmenté pour 1000 actifs)
    resultats = med.run_full_pipeline_multithreaded(period="1y", interval="1d", max_workers=20)
    
    success = sum(1 for v in resultats.values() if v)
    total = len(resultats)
    failed = total - success
    
    elapsed = time.time() - start_time
    
    print("\n============================================================")
    print("                        BILAN                               ")
    print("============================================================")
    print(f"Statut           : Terminé")
    print(f"Actifs réussis   : {success} / {total}")
    if failed > 0:
        print(f"Actifs échoués   : {failed} (tickers invalides ou hors réseau)")
    print(f"Temps écoulé     : {elapsed:.1f}s ({elapsed/60:.1f} min) ⚡")
    print("============================================================")
    
    if success == total:
        print("🎉 Base de données SQL entièrement prête !")
    elif success > total * 0.9:
        print("✅ Base de données prête (>90% des actifs chargés).")
    else:
        print("⚠️  Vérifiez votre connexion internet, plusieurs actifs n'ont pas pu être récupérés.")

if __name__ == "__main__":
    main()

