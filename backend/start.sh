#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "→ checking venv..."
if [ ! -d "backend/.venv" ]; then
  echo "→ creating venv..."
  python3 -m venv backend/.venv
fi

echo "→ activating venv..."
source backend/.venv/bin/activate

echo "→ installing dependencies..."
pip install -q -r backend/requirements.txt

echo "→ freeing port 8080..."
lsof -ti tcp:8080 | xargs kill -9 2>/dev/null || true

echo "→ starting server on http://localhost:8080"
uvicorn backend.main:app --port 8080 --reload
