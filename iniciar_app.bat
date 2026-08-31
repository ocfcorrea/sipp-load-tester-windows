@echo off
setlocal enabledelayedexpansion
title SIPp Load Tester Pro — Inicializador
cd /d "%~dp0"

echo ============================================================
echo   SIPp Load Tester Pro - Verificando Ambiente Python...
echo ============================================================

REM 1. Verifica ou cria o ambiente virtual .venv
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Ambiente virtual .venv nao encontrado.
    echo       Criando ambiente virtual Python...
    python -m venv .venv
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo [ERRO] Falha ao criar ambiente virtual. Certifique-se de que o Python 3.9+ esta instalado e no PATH.
        echo Baixe em: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado com sucesso.
)

REM 2. Verifica se as dependencias estao instaladas no .venv
".venv\Scripts\python.exe" -c "import customtkinter, dotenv, PIL, packaging, darkdetect" 2>nul
if !ERRORLEVEL! NEQ 0 (
    echo [2/3] Instalando dependencias necessarias (customtkinter, pillow, python-dotenv...)...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo [ERRO] Falha ao instalar dependencias do requirements.txt.
        echo Tente executar instalar_dependencias.bat manualmente.
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas com sucesso.
)

REM 3. Inicia a aplicacao
echo [3/3] Iniciando interface grafica...
echo.
".venv\Scripts\python.exe" app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo [ERRO] A aplicacao encerrou com erro (Codigo: %ERRORLEVEL%).
    echo Verifique os logs acima ou execute via terminal para mais detalhes.
    echo ============================================================
    pause
)
