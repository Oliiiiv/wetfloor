#!/usr/bin/env bash
# =============================================================================
# Wrapper around `docker compose` that loads IBKR credentials from macOS
# Keychain (set up via ./scripts/setup-credentials.sh) and exports them as
# environment variables for the duration of the command.
#
# Credentials are NEVER written to disk during this process.
#
# Usage:
#   ./scripts/compose.sh up backend-poc
#   ./scripts/compose.sh logs ib-gateway --tail 200
#   ./scripts/compose.sh down
#   ./scripts/compose.sh ps
# =============================================================================

set -euo pipefail

if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "Error: this wrapper uses macOS Keychain." >&2
  echo "On other platforms, run 'docker compose ...' directly with a .env file." >&2
  exit 1
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
# Port 4004 = paper API via socat in gnzsnz/ib-gateway. Use 4003 for live.
export IB_GATEWAY_PORT="${IB_GATEWAY_PORT:-4004}"
export IB_CLIENT_ID="${IB_CLIENT_ID:-1}"
export READ_ONLY_API="${READ_ONLY_API:-yes}"

exec docker compose "$@"
