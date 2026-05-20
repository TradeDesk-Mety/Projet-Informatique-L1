#!/bin/bash

# TRADEDESK v1.2 - Linux/macOS Launch Script (With Auto-Kill & Browser Choice)
# Inspiré de SportsBetting

ROOT_DIR=$(pwd)
PORT=8502

show_menu() {
    clear
    echo "========================================================"
    echo "       📈 TRADEDESK - CONTROL CENTER 📈"
    echo "========================================================"
    echo ""
    echo " [1] Lancer le Site Web (Streamlit)"
    echo " [2] Récupérer / Mettre à jour les données (yfinance SQL)"
    echo " [3] Installer les bibliothèques / Dépendances"
    echo " [4] Lancer la suite de tests unitaires"
    echo " [5] Lancer l'optimisation Grid Search (C++)"
    echo " [6] Quitter"
    echo ""
    echo "========================================================"
    read -p "Choisissez une option (1-6) : " choice
}

choose_browser() {
    clear
    echo "========================================================"
    echo "        🌐 CHOIX DU NAVIGATEUR WEB 🌐"
    echo "========================================================"
    echo ""
    echo " [1] Google Chrome / Chromium"
    echo " [2] Mozilla Firefox"
    echo " [3] Brave Browser"
    echo " [4] Navigateur par défaut du système (xdg-open)"
    echo ""
    echo "========================================================"
    read -p "Choisissez votre navigateur (1-4) : " browser_choice

    case $browser_choice in
        1) BROWSER_CMD="google-chrome" ;;
        2) BROWSER_CMD="firefox" ;;
        3) BROWSER_CMD="brave-browser" ;;
        *) BROWSER_CMD="xdg-open" ;;
    esac
}

setup_venv() {
    if [ ! -d ".venv" ]; then
        echo "[1/2] Création de l'environnement virtuel..."
        python3 -m venv .venv
    fi
    echo "[2/2] Vérification des dépendances..."
    ./.venv/bin/pip install --upgrade pip --quiet
    ./.venv/bin/pip install -r requirements.txt --quiet
}

kill_port() {
    echo "[INFO] Vérification du port $PORT..."
    if command -v lsof >/dev/null 2>&1; then
        PID=$(lsof -t -i:$PORT)
        if [ ! -z "$PID" ]; then
            echo "[NETTOYAGE] Processus de fond trouvé (PID: $PID) sur le port $PORT. Libération..."
            kill -9 $PID
            sleep 1
        fi
    fi
}

launch_website() {
    echo ""
    kill_port
    echo "[INFO] Préparation du Site..."
    setup_venv

    echo "[INFO] Ouverture du navigateur..."
    # On attend 1 seconde en arrière-plan pour laisser Streamlit s'initialiser, puis on ouvre l'URL
    (sleep 1 && $BROWSER_CMD "http://localhost:$PORT" >/dev/null 2>&1) &

    echo "[INFO] Lancement de Streamlit..."
    # Le --server.headless true dit à Streamlit de ne pas essayer d'ouvrir un navigateur de son côté
    ./.venv/bin/streamlit run website/TradeDesk.py --server.port $PORT --server.headless true
}

while true; do
    show_menu
    case $choice in
        1)
            choose_browser
            launch_website
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        2)
            echo ""
            echo "[INFO] Lancement de la récupération des données..."
            setup_venv
            ./.venv/bin/python populate_db.py
            echo ""
            echo "[SUCCÈS] Pipeline terminé."
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        3)
            echo ""
            echo "[INFO] Installation des bibliothèques..."
            setup_venv
            echo "[SUCCÈS] Toutes les dépendances sont installées."
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        4)
            echo ""
            echo "[INFO] Lancement des tests unitaires..."
            setup_venv
            ./.venv/bin/python run_tests.py
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        5)
            echo ""
            echo "[INFO] Lancement de l'outil Grid Search C++..."
            setup_venv
            ./.venv/bin/python run_grid_search.py
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        6)
            exit 0
            ;;
        *)
            echo "Option invalide."
            sleep 1
            ;;
    esac
done