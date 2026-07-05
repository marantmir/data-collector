#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

MODE="${1:-dev}"

case "$MODE" in
    docker)
        command -v docker >/dev/null 2>&1 || { echo "Docker nao encontrado"; exit 1; }
        echo "Subindo stack completa com Docker..."
        docker compose up -d --build
        echo "API:       http://localhost:8000"
        echo "Docs:      http://localhost:8000/docs"
        echo "Grafana:   http://localhost:3000 (admin/admin)"
        echo "Popular:   docker compose exec api python scripts/seed_from_api.py 33000167000101"
        echo "Parar:     docker compose down"
        ;;

    dev|*)
        echo "Modo desenvolvimento (sem Docker)..."
        pip install -e ".[dev]" -q 2>/dev/null || true
        alembic upgrade head 2>/dev/null || echo "Migrations falharam (DB configurado?)"
        python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
esac
