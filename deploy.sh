#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

command -v python3 >/dev/null 2>&1 || { echo "Python3 nao encontrado"; exit 1; }
pip install -e . -q 2>/dev/null || pip install -e .

if [ ! -f .env ]; then
    cp .env.example .env
fi

alembic upgrade head
echo "Deploy concluido. Execute: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"
