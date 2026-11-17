#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "============================================================"
echo "  INICIANDO MONITORAMENTO DE RISCO NEONATAL (STREAMLIT)"
echo "============================================================"

if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não encontrado. Instale o python3 e python3-venv."
    read -p "Pressione Enter para sair..."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "[1/3] Criando ambiente virtual isolado (.venv)..."
    python3 -m venv .venv
else
    echo "[1/3] Ambiente virtual (.venv) já configurado."
fi

source .venv/bin/activate

if ! python -m pip --version &> /dev/null; then
    echo "      Instalando pip no ambiente virtual..."
    python -m ensurepip --upgrade
fi

echo "[2/3] Verificando e instalando dependências..."
python -m pip install --upgrade pip --quiet
python -m pip install --prefer-binary -r requirements.txt --quiet

echo "[3/3] Abrindo aplicação no navegador..."
streamlit run app.py
