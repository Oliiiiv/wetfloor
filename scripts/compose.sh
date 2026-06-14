#!/usr/bin/env bash
# =============================================================================
# Wrapper around `docker compose` that loads IBKR credentials from macOS
# Keychain (set up via ./scripts/setup-credentials.sh) and exports them as
# environment variables for the duration of the command.
#
# Credentials are NEVER written to disk during this process.
#
# Usage:
#   ./scripts/compose.sh up                       # paper mode (default)
#   ./scripts/compose.sh --live up                # live mode (real money)
#   ./scripts/compose.sh --paper up               # explicit paper
#   ./scripts/compose.sh --live logs ib-gateway   # any sub-command works
#   ./scripts/compose.sh down                     # stop (mode-agnostic)
#
# Mode flag effects:
#   --live   : TRADING_MODE=live, keychain entry = ibkr_live,  port = 4003
#   --paper  : TRADING_MODE=paper, keychain entry = ibkr_paper, port = 4004
# Without a flag, paper is assumed (safe default).
# =============================================================================

set -euo pipefail

if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "Error: this wrapper uses macOS Keychain." >&2
  echo "On other platforms, run 'docker compose ...' directly with a .env file." >&2
  exit 1
fi

# --- Parse our own flags (anywhere in argv); leave the rest for docker compose ---
MODE_OVERRIDE=""
DEV_MODE=""
REMAINING=()
for arg in "$@"; do
  case "$arg" in
    --live)  MODE_OVERRIDE="live"  ;;
    --paper) MODE_OVERRIDE="paper" ;;
    --dev)   DEV_MODE="1"          ;;
    *)       REMAINING+=("$arg")   ;;
  esac
done
# Replace argv with non-flag args so the rest of the script sees a clean $@.
set -- "${REMAINING[@]+"${REMAINING[@]}"}"

if [[ -n "$MODE_OVERRIDE" ]]; then
  export TRADING_MODE="$MODE_OVERRIDE"
  # When flag is set, also default the keychain account to match (unless
  # the caller explicitly pinned IBKR_KEYCHAIN_ACCOUNT).
  if [[ -z "${IBKR_KEYCHAIN_ACCOUNT:-}" ]]; then
    if [[ "$MODE_OVERRIDE" == "live" ]]; then
      export IBKR_KEYCHAIN_ACCOUNT="ibkr_live"
    else
      export IBKR_KEYCHAIN_ACCOUNT="ibkr_paper"
    fi
  fi
fi

SERVICE_USER="cautiouswetfloor.ibkr_username"
SERVICE_PASS="cautiouswetfloor.ibkr_password"
ACCOUNT="${IBKR_KEYCHAIN_ACCOUNT:-ibkr_paper}"

if ! security find-generic-password -a "$ACCOUNT" -s "$SERVICE_USER" >/dev/null 2>&1; then
  echo "Error: IBKR credentials not found in macOS Keychain." >&2
  echo "       Run ./scripts/setup-credentials.sh first." >&2
  exit 1
fi

# Fetch credentials (-w prints just the password value, no metadata)
IBKR_USERNAME=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE_USER" -w)
IBKR_PASSWORD=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE_PASS" -w)

# Export for docker compose to pick up (matches keys used in docker-compose.yml)
export IBKR_USERNAME IBKR_PASSWORD

# Sensible defaults; override by exporting before invocation.
export TRADING_MODE="${TRADING_MODE:-paper}"
# Auto-pick the socat port based on trading mode unless the caller pinned one.
# In the gnzsnz/ib-gateway image: paper = 4004, live = 4003.
if [[ -z "${IB_GATEWAY_PORT:-}" ]]; then
  if [[ "$TRADING_MODE" == "live" ]]; then
    export IB_GATEWAY_PORT=4003
  else
    export IB_GATEWAY_PORT=4004
  fi
fi
export IB_CLIENT_ID="${IB_CLIENT_ID:-1}"
# READ_ONLY_API=yes is a safety net for live trading — keep it on unless you
# explicitly want order-placement capability. Even with this on, you should
# also set IBKR Account Management → API → Read-Only API for belt-and-suspenders.
export READ_ONLY_API="${READ_ONLY_API:-yes}"

# --- Startup banner (visible mode indicator) ---
# Only show on commands that "do something" (up/run/exec) to avoid noise on ps/logs.
DEV_SUFFIX=""
if [[ -n "$DEV_MODE" ]]; then
  DEV_SUFFIX="  [DEV: hot-reload enabled]"
fi
case "${1:-}" in
  up|run|exec|start|restart)
    if [[ "$TRADING_MODE" == "live" ]]; then
      # ANSI red bold for live; loud on purpose.
      printf "\033[1;31m"
      echo "==============================================================="
      echo "  LIVE TRADING MODE  --  real money at stake${DEV_SUFFIX}"
      echo "  keychain : $IBKR_KEYCHAIN_ACCOUNT"
      echo "  port     : $IB_GATEWAY_PORT"
      echo "  read-only: $READ_ONLY_API   (also verify in IBKR Account Mgmt)"
      echo "==============================================================="
      printf "\033[0m"
    else
      printf "\033[1;32m"
      echo "Paper mode (keychain=$IBKR_KEYCHAIN_ACCOUNT port=$IB_GATEWAY_PORT)${DEV_SUFFIX}"
      printf "\033[0m"
    fi
    ;;
esac

# --- Compose file list (override stack when --dev is active) ---
COMPOSE_FILES=(-f docker-compose.yml)
if [[ -n "$DEV_MODE" ]]; then
  COMPOSE_FILES+=(-f docker-compose.dev.yml)
fi

exec docker compose "${COMPOSE_FILES[@]}" "$@"
