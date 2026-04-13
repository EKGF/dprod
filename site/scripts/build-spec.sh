#!/usr/bin/env bash
# Build the DPROD ontology spec into ../dist/ for sync-spec to pick up.
#
# Purpose: the root-level build.sh pins Python to an exact 3.13 match, which
# doesn't work on Vercel's build image (ships Python 3.12). This script uses
# whatever python3 is available and creates a throwaway venv just for the
# spec generator's pip install step.
#
# Run from anywhere; it finds the repo root relative to its own location.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "[build-spec] repo=$REPO_ROOT python=$(python3 --version 2>&1)"

VENV_DIR=".venv-spec"
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

python spec-generator/main.py

echo "[build-spec] generated $(find dist -type f | wc -l | tr -d ' ') files in dist/"
