#!/usr/bin/env bash
# Stop publisher, plot latest CSV on the host (reliable on Pi), then tear down the stack.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if [[ -x "${ROOT}/venv/bin/python" ]]; then
  PYTHON="${ROOT}/venv/bin/python"
else
  PYTHON="$(command -v python3)"
fi

echo "Stopping mqtt-publisher..."
docker compose stop mqtt-publisher

if compgen -G "exports/*.csv" > /dev/null; then
  "${ROOT}/scripts/fix_visualize_output_permissions.sh"
  echo "Cleaning latest CSV and writing charts..."
  "${PYTHON}" scripts/DataPipe/fullPipe/cs2_luis_testunit.py \
    || echo "WARNING: Cleanup plot failed; check venv (pip install -r requirements.txt)." >&2
else
  echo "No active CSV in exports/ to plot."
fi

echo "Stopping remaining services..."
docker compose down "$@"
