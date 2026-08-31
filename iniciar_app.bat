@echo off
setlocal enabledelayedexpansion
title SIPp Load Tester Pro — Inicializador Offline
cd /d "%~dp0"

echo ============================================================
echo   SIPp Load Tester Pro - Inicializando (Modo 100%% Offline)
echo ============================================================

REM 1. Se o ambiente virtual .venv ja existe e funciona, executa diretamente
if exist ".venv\Scripts\python.exe" (
    echo [OK] Ambiente virtual .venv encontrado.
    ".venv\Scripts\python.exe" app.py
    if !ERRORLEVEL! EQU 0 exit /b 0
)

REM 2. Tenta criar o .venv e instalar pacotes a partir da pasta offline wheels/
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Python nao encontrado no PATH do sistema.
    echo Certifique-se de que o Python 3.9+ esta instalado e marcado 'Add to PATH'.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [*] Configurando ambiente local...
    python -m venv .venv >nul 2>nul
    if exist ".venv\Scripts\python.exe" (
        if exist "wheels" (
            echo [*] Instalando dependencias locais da pasta offline 'wheels/'...
            ".venv\Scripts\python.exe" -m pip install --no-index --find-links=wheels -r requirements.txt >nul 2>nul
        )
    )
)

REM 3. Execucao principal: prioriza .venv, com fallback automatico para Python global com lib/ embutida
if exist ".venv\Scripts\python.exe" (
    echo [*] Iniciando aplicacao via .venv...
    ".venv\Scripts\python.exe" app.py
) else (
    echo [*] Iniciando aplicacao com bibliotecas embutidas (lib/)...
    python app.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo [ERRO] A aplicacao encerrou com codigo %ERRORLEVEL%.
    echo ============================================================
    echo.
    pause
)
