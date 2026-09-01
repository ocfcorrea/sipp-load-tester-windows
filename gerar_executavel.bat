@echo off
chcp 65001 >nul
title SIPp Load Tester Pro - Gerador de Executavel Windows Versionado

echo ============================================================
echo   COMPILANDO EXECUTAVEL UNICO .EXE VERSIONADO (PyInstaller)
echo ============================================================
echo.

:: 1. Verifica Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao foi encontrado no PATH do Windows.
    echo Instale o Python 3.9+ e marque 'Add Python to PATH'.
    pause
    exit /b 1
)

:: 2. Verifica / Instala PyInstaller
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Instalando PyInstaller no ambiente...
    pip install pyinstaller
)

:: 3. Registra e extrai versao dinamica da release (Git Commit Count)
for /f "delims=" %%i in ('python -c "from core.version import save_version_file; print(save_version_file())"') do set "APP_VERSION=%%i"
if not defined APP_VERSION set "APP_VERSION=v2.0.0"

echo [INFO] Versao detectada para este build: %APP_VERSION%
echo [INFO] Empacotando aplicacao, scripts, PCAPs e cenarios em arquivo unico...
pyinstaller --noconfirm SIPp_Load_Tester_Pro.spec

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Ocorreu uma falha durante a compilacao do executavel.
    pause
    exit /b 1
)

:: 4. Salva copia versionada da release
if exist "dist\SIPp_Load_Tester_Pro.exe" (
    copy /y "dist\SIPp_Load_Tester_Pro.exe" "dist\SIPp_Load_Tester_Pro_%APP_VERSION%.exe" >nul
)

echo.
echo ============================================================
echo   [SUCESSO] EXECUTAVEL VERSIONADO GERADO COM EXITO!
echo ============================================================
echo.
echo Executaveis gerados em dist\:
echo   [1] dist\SIPp_Load_Tester_Pro_%APP_VERSION%.exe  (Release Versionada)
echo   [2] dist\SIPp_Load_Tester_Pro.exe              (Standalone Geral)
echo.
echo Voce pode distribuir qualquer um dos arquivos acima para
echo computadores Windows sem necessidade de instalar Python ou SIPp!
echo.
pause
