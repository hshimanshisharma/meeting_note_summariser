#!/usr/bin/env bash
# Create or refresh the venv using Python 3.14
set -euo pipefail
cd "$(dirname "$0")"

PYTHON=/usr/local/bin/python3.14

if [[ ! -x "$PYTHON" ]]; then
  echo "Error: $PYTHON not found." >&2
  exit 1
fi

echo "Using $($PYTHON --version)"
rm -rf venv
"$PYTHON" -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Done. Activate with: source venv/bin/activate"
