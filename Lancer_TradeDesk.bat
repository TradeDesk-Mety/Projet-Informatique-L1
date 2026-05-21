@echo off
setlocal EnableExtensions
title TRADEDESK v1.2
cd /d "%~dp0"

:: Configuration du port ici
set PORT=8502

:MENU
cls
color 0A
echo ========================================================
echo        📈 TRADEDESK - CONTROL CENTER 📈
echo ========================================================
echo.
echo  [1] Lancer le Site Web (Streamlit)
echo  [2] Recuperer / Mettre a jour les donnees (yfinance SQL)
echo  [3] Installer les bibliotheques / Dependances
echo  [4] Lancer la suite de tests unitaires
echo  [5] Lancer l'optimisation Grid Search (C++)
echo  [6] Quitter
echo.
echo ========================================================
set /p choice="Choisissez une option (1-6) : "

if "%choice%"=="1" goto CHOOSE_BROWSER
if "%choice%"=="2" goto FETCH
if "%choice%"=="3" goto DEPENDENCIES
if "%choice%"=="4" goto TESTS
if "%choice%"=="5" goto GRID_SEARCH
if "%choice%"=="6" goto EXIT
goto MENU

:CHOOSE_BROWSER
cls
echo ========================================================
echo        🌐 CHOIX DU NAVIGATEUR WEB 🌐
echo ========================================================
echo.
echo  [1] Google Chrome
echo  [2] Microsoft Edge
echo  [3] Mozilla Firefox
echo  [4] Navigateur par defaut de Windows
echo.
echo ========================================================
set /p browser_choice="Choisissez votre navigateur (1-4) : "

if "%browser_choice%"=="1" set BROWSER_CMD=chrome
if "%browser_choice%"=="2" set BROWSER_CMD=msedge
if "%browser_choice%"=="3" set BROWSER_CMD=firefox
if "%browser_choice%"=="4" set BROWSER_CMD=start

goto WEBSITE

:WEBSITE
echo.
echo [INFO] Verification du port %PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo [NETTOYAGE] Processus de fond trouve (PID: %%a) sur le port %PORT%. Liberation...
        taskkill /F /PID %%a >nul 2>&1
        timeout /t 1 >nul
    )
)

echo [INFO] Preparation du Site...
call :SETUP_VENV

echo [INFO] Ouverture du navigateur...
:: On attend 2 secondes en tâche de fond pour laisser Streamlit démarrer, puis on ouvre l'URL
if "%BROWSER_CMD%"=="start" (
    start "" "http://localhost:%PORT%"
) else (
    start %BROWSER_CMD% "http://localhost:%PORT%"
)

echo [INFO] Lancement de Streamlit...
:: On ajoute --server.headless true pour empêcher Streamlit de tenter d'ouvrir son propre browser buggé
.venv\Scripts\python -m streamlit run website\TradeDesk.py --server.port %PORT% --server.headless true
pause
goto MENU

:FETCH
echo.
echo [INFO] Remplissage et mise a jour des bases de donnees SQL...
call :SETUP_VENV
.venv\Scripts\python populate_db.py
echo.
echo [SUCCÈS] Recuperation terminee.
pause
goto MENU

:DEPENDENCIES
echo.
echo [INFO] Installation des bibliotheques...
call :SETUP_VENV
echo [SUCCÈS] Toutes les dependances sont installees.
pause
goto MENU

:TESTS
echo.
echo [INFO] Lancement des tests unitaires...
call :SETUP_VENV
.venv\Scripts\python run_tests.py
pause
goto MENU

:GRID_SEARCH
echo.
echo [INFO] Lancement de l'outil Grid Search C++...
call :SETUP_VENV
.venv\Scripts\python run_grid_search.py
pause
goto MENU

:SETUP_VENV
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH.
    echo Installez Python sur https://www.python.org/
    pause
    exit /b
)
if not exist ".venv" (
    echo [1/2] Creation de l'environnement virtuel...
    python -m venv .venv
)
echo [2/2] Mise a jour des dependances...
.venv\Scripts\python -m pip install --upgrade pip --quiet
.venv\Scripts\python -m pip install -r requirements.txt --quiet
exit /b

:EXIT
exit /b
