#!/usr/bin/env python3
import unittest
import sys
import os

def run_all_tests():
    print("=" * 60)
    print("   Lancement de la suite de tests complète (Projet L1)   ")
    print("=" * 60)
    
    # Chemin vers le dossier tests
    start_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tests")
    
    # Découverte automatique des tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Rapport final
    print("\n" + "=" * 60)
    print("                      BILAN DES TESTS                       ")
    print("=" * 60)
    print(f"Tests exécutés : {result.testsRun}")
    print(f"Échecs         : {len(result.failures)}")
    print(f"Erreurs        : {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 FÉLICITATIONS ! Tout fonctionne parfaitement. Aucun bug détecté.")
        sys.exit(0)
    else:
        print("\n❌ ATTENTION : Certains tests ont échoué ou produit des erreurs.")
        sys.exit(1)

if __name__ == '__main__':
    run_all_tests()
