@echo off
setlocal enabledelayedexpansion
title SIPp Load Tester Pro — Instalador de Dependências
cd /d "%~dp0"

echo ============================================================
echo   SIPp Load Tester Pro - Instalador de Dependencias Python
echo ============================================================
echo.

REM Verifica presenca do Python no sistema
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado no PATH do sistema.
    echo Por favor, instale o Python 3.9 ou superior (marcando a opcao "Add Python to PATH").
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/4] Detectando versao do Python...
python --version
echo.

REM Cria ou recria o venv se solicitado
if not exist ".venv\Scripts\python.exe" (
    echo [2/4] Criando ambiente virtual (.venv)...
    python -m venv .venv
    if !ERRORLEVEL! NEQ 0 (
        echo [ERRO] Falha ao criar ambiente virtual .venv.
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual .venv criado com sucesso.
) else (
    echo [2/4] Ambiente virtual .venv ja existe.
)
echo.

echo [3/4] Atualizando pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo.
echo [4/4] Instalando pacotes do requirements.txt...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha na instalacao dos pacotes.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [SUCESSO] Todas as dependencias foram instaladas com exito!
echo Para iniciar o aplicativo, execute: iniciar_app.bat
echo ============================================================
echo.
pause
