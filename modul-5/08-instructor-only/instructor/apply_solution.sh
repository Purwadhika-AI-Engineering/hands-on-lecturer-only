#!/usr/bin/env bash
# Copy the reference guards over the starter (for Demo 2 / dry runs). Backs up your current files first.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .starter_backup/guards
cp app/prompts.py .starter_backup/prompts.py
cp app/guards/*.py .starter_backup/guards/
cp instructor/solution/app/prompts.py app/prompts.py
cp instructor/solution/app/guards/*.py app/guards/
echo "Reference solution applied. Restart the app:  docker compose up -d --build   (originals saved in .starter_backup/)"
