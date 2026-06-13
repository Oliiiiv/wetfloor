#!/usr/bin/env bash
# =============================================================================
# FinBERT de-risk POC runner (uses plain venv, no uv required).
#
# Behavior:
#   - First run: creates apps/backend/.venv, installs transformers + torch,
#                downloads the FinBERT model (~440 MB), runs the test.
#   - Subsequent runs: reuses the venv, skips install, just runs the test.
#                      (~1-2 seconds startup)
#
# Usage:
#   ./scripts/finbert.sh                 # set up if needed + run
#   ./scripts/finbert.sh --reinstall     # force-reinstall deps
#   source apps/backend/.venv/bin/activate   # if you want the venv in your shell
# =============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/apps/backend"
VENV_DIR="$BACKEND_DIR/.venv"
REQ_FILE="$BACKEND_DIR/poc/requirements-finbert.txt"

# Pick a Python 3.11+ interpreter
PYTHON="${PYTHON:-python3}"
PYTHON_VERSION="$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "$PYTHON_VERSION" < "3.11" ]]; then
  echo "Error: need Python >= 3.11, found $PYTHON_VERSION ($PYTHON)" >&2
  echo "       Try: PYTHON=python3.11 ./scripts/finbert.sh" >&2
  echo "       Or:  brew install python@3.11" >&2
  exit 1
fi

cd "$BACKEND_DIR"

# 1. Create venv if missing
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating venv at $VENV_DIR (using $PYTHON, version $PYTHON_VERSION) ..."
  "$PYTHON" -m venv "$VENV_DIR"
fi

# 2. Activate
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# 3. Install deps if missing (or if --reinstall passed)
NEEDS_INSTALL=0
if [[ "${1:-}" == "--reinstall" ]]; then
  NEEDS_INSTALL=1
elif ! python -c "import torch, transformers" 2>/dev/null; then
  NEEDS_INSTALL=1
fi

if (( NEEDS_INSTALL )); then
  echo "Installing dependencies (first run takes 2-5 minutes — torch is ~2 GB) ..."
  pip install --quiet --upgrade pip
  pip install -r "$REQ_FILE"
  echo
fi

# 4. Run the POC
echo "Running FinBERT POC ..."
python -m poc.test_finbert
