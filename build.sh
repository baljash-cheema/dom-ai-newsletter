#!/usr/bin/env bash
# Build a newsletter issue to HTML + PDF using the project's virtual environment.
#   ./build.sh            # builds the most recent issue
#   ./build.sh 2026-07    # builds issues/2026-07
#   ./build.sh 2026-07 --final   # only succeeds if every source is verified
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x ".venv/bin/python" ]; then
  echo "✗ No virtual environment found. Run:  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi
exec .venv/bin/python build.py "$@"
