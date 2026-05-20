import os
import yfinance as yf
from finance import finance as fin

def run_grid_search_console():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("========================================================")
    print("      🔍 OPTIMISATION GRID SEARCH (MOTEUR C++) 🔍      ")
    print("========================================================")
    print("\nCet outil simule des milliers de combinaisons pour trouver")
    print("les meilleurs paramètres de trading sur l'historique d'un actif.")
    
    ticker = input("\nEntrez le symbole boursier (ex: AAPL, TSLA, ^FCHI) : ").upper()
    if not ticker:
        return
        
    print(f"\n[1/3] Téléchargement de l'historique 1 an pour {ticker}...")
    try:
        data = yf.download(ticker, period="1y", interval="1d", progress=False)
        if data.empty:
            print("Erreur : Aucune donnée trouvée.")
            return
            
        prices = data['Close'].values.flatten().tolist()
        
        print("\n[2/3] Optimisation Grid Search (SMA) en cours en C++...")
        best_short, best_long, ret_sma = fin.grid_search_sma(prices)
        print(f"✅ Optimum SMA trouvé : Fenêtre Courte={best_short}, Longue={best_long}")
        print(f"   --> Rendement simulé : {ret_sma:+.2f}%")
        
        print("\n[3/3] Optimisation Grid Search (RSI) en cours en C++...")
        best_w, best_os, best_ob, ret_rsi = fin.grid_search_rsi(prices)
        print(f"✅ Optimum RSI trouvé : Fenêtre={best_w}, Survente=<{best_os}, Surachat=>{best_ob}")
        print(f"   --> Rendement simulé : {ret_rsi:+.2f}%")
        
    except Exception as e:
        print(f"Erreur lors de l'optimisation : {e}")

if __name__ == "__main__":
    run_grid_search_console()
    input("\nAppuyez sur Entrée pour retourner au menu...")
