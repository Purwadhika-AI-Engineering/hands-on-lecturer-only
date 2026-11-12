#!/usr/bin/env bash
# Undo apply_solution.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d .starter_backup ] || { echo "no .starter_backup/ found"; exit 1; }
cp .starter_backup/prompts.py app/prompts.py
cp .starter_backup/guards/*.py app/guards/
echo "Starter restored. Restart the app:  docker compose up -d --build"
