#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
python3 -m venv "$ROOT/.venv"
source "$ROOT/.venv/bin/activate"
pip install -r "$ROOT/server/requirements.txt"
(cd "$ROOT/frontend" && npm install)
trap 'kill 0' EXIT
(cd "$ROOT/server" && uvicorn app:app --reload --port 8000) &
(cd "$ROOT/frontend" && npm run dev -- --host 0.0.0.0) &
wait
