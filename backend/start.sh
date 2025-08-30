#!/usr/bin/env bash
set -euo pipefail
echo "[boot] starting FastAPI + creating tables if missing…"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
