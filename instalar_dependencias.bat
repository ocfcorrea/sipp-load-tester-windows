@echo off
setlocal enabledelayedexpansion
title SIPp Load Tester Pro — Instalador de Dependências Offline
cd /d "%~dp0"

echo ============================================================
echo   SIPp Load Tester Pro - Instalador Offline de Dependencias
echo ============================================================
echo.

REM Verifica presenca do Python no sistema
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado no PATH do sistema.
    echo Por favor, instale o Python 3.9 ou superior (marcando a opcao "Add Python to PATH").
    echo.
    pause
    exit /b 1
)

echo [1/3] Detectando versao do Python...
python --version
echo.

REM Cria ou recria o venv se solicitado
if not exist ".venv\Scripts\python.exe" (
    echo [2/3] Criando ambiente virtual (.venv)...
    python -m venv .venv
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo [AVISO] Falha ao criar .venv. O aplicativo utilizara a pasta de bibliotecas embutidas 'lib/'.
    ) else (
        echo [OK] Ambiente virtual .venv criado com sucesso.
    )
) else (
    echo [2/3] Ambiente virtual .venv ja existe.
)
echo.

REM Instala dependencias a partir da pasta wheels offline (sem conexao com a internet)
if exist ".venv\Scripts\python.exe" (
    if exist "wheels" (
        echo [3/3] Instalando pacotes a partir da pasta local 'wheels/' (100%% Offline)...
        ".venv\Scripts\python.exe" -m pip install --no-index --find-links=wheels -r requirements.txt
        if !ERRORLEVEL! EQU 0 (
            echo.
            echo ============================================================
            echo [SUCESSO] Dependencias instaladas no .venv com exito!
            echo Para iniciar o aplicativo, execute: iniciar_app.bat
            echo ============================================================
            echo.
            pause
            exit /b 0
        )
    )
)

echo.
echo ============================================================
echo [INFO] O projeto ja contem todas as bibliotecas embutidas em 'lib/'.
echo O aplicativo pode ser executado offline imediatamente via:
echo   iniciar_app.bat  ou  python app.py
echo ============================================================
echo.
pause
