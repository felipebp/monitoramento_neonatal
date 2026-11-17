@echo off
chcp 65001 >nul
title Monitoramento de Risco Neonatal - UFMS
cd /d "%~dp0"

echo ============================================================
echo   INICIANDO MONITORAMENTO DE RISCO NEONATAL (STREAMLIT)
echo ============================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado no sistema!
    echo Instale o Python 3.10+ em https://www.python.org/downloads/
    echo IMPORTANTE: Marque a opcao "Add Python to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [1/3] Criando ambiente virtual isolado (.venv)...
    python -m venv .venv
) else (
    echo [1/3] Ambiente virtual (.venv) ja configurado.
)

call .venv\Scripts\activate.bat

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo       Instalando pip no ambiente virtual...
    python -m ensurepip --upgrade
)

echo [2/3] Verificando e instalando dependencias...
python -m pip install --upgrade pip --quiet
python -m pip install --prefer-binary -r requirements.txt --quiet

echo [3/3] Abrindo aplicacao no navegador...
echo (Pressione Ctrl+C nesta janela para encerrar o servidor)
echo.
streamlit run app.py

pause