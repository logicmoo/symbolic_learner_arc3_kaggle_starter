#!/usr/bin/env bash
set -euo pipefail

WORKBENCH_ROOT="$(cd "$(dirname "$0")" && pwd)"

if [[ ! -x "$WORKBENCH_ROOT/.venv/bin/python" ]]; then
  python3 -m venv "$WORKBENCH_ROOT/.venv"
fi

echo "Normalizing workspace JSON resource kinds and filenames..."
"$WORKBENCH_ROOT/.venv/bin/python" "$WORKBENCH_ROOT/scripts/normalize_workspace_json.py" --write

"$WORKBENCH_ROOT/.venv/bin/python" -m pip install \
  --disable-pip-version-check -q \
  -r "$WORKBENCH_ROOT/server/requirements.txt"

if [[ ! -x "$WORKBENCH_ROOT/frontend/node_modules/.bin/vite" ]]; then
  (cd "$WORKBENCH_ROOT/frontend" && npm install)
fi

trap 'jobs -p | xargs -r kill' EXIT INT TERM
(cd "$WORKBENCH_ROOT/server" && "$WORKBENCH_ROOT/.venv/bin/python" -m uvicorn app:app --reload --host 127.0.0.1 --port 8000) &
(cd "$WORKBENCH_ROOT/frontend" && npm run dev) &

echo "MeTTaSymbolicLearnerWorkbench: http://127.0.0.1:5173/"
echo "API documentation: http://127.0.0.1:8000/docs"
wait
