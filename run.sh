#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# Python 3.14's ensurepip is currently broken on this machine; prefer a known-good interpreter.
PY="$(command -v python3.12 || command -v python3.11 || command -v python3)"

if [ ! -d .venv ]; then
  echo "→ creating virtualenv ($PY) + installing deps..."
  "$PY" -m venv .venv
  ./.venv/bin/pip install -q --upgrade pip
  ./.venv/bin/pip install -q -r requirements.txt
fi

echo "→ starting on http://127.0.0.1:8000"
cd backend
exec ../.venv/bin/uvicorn app:app --reload --port 8000
