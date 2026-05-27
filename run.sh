#!/usr/bin/env bash
# Run the app with Python 3.14
set -euo pipefail
cd "$(dirname "$0")"

PYTHON=/usr/local/bin/python3.14

if [[ ! -x "$PYTHON" ]]; then
  echo "Error: $PYTHON not found. Install Python 3.14 first." >&2
  exit 1
fi

if [[ ! -d venv ]]; then
  echo "Creating virtual environment with Python 3.14..."
  "$PYTHON" -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

exec python app.py
