#!/usr/bin/env bash
# =============================================================================
# Store IBKR credentials in macOS Keychain (replacement for .env approach).
#
# Why Keychain instead of .env:
#   - Credentials are encrypted at rest by the OS
#   - Never sit in a plaintext file on disk
#   - Access can be audited / revoked through Keychain Access app
#   - Survives accidental `rm -rf` of the project folder
#
# Re-run this script anytime to rotate / update credentials.
# =============================================================================

set -euo pipefail

if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "Error: this script requires macOS (uses the 'security' CLI)." >&2
  echo "On other platforms, copy .env.example -> .env and fill it in." >&2
  exit 1
fi

SERVICE_USER="cautiouswetfloor.ibkr_username"
SERVICE_PASS="cautiouswetfloor.ibkr_password"
ACCOUNT="${IBKR_KEYCHAIN_ACCOUNT:-ibkr_paper}"

echo "Storing IBKR credentials in macOS Keychain."
echo "Account label: ${ACCOUNT} (override with IBKR_KEYCHAIN_ACCOUNT env var)"
echo

read -rp "IBKR username: " IBKR_USERNAME
read -rsp "IBKR password: " IBKR_PASSWORD
echo

if [[ -z "$IBKR_USERNAME" || -z "$IBKR_PASSWORD" ]]; then
  echo "Error: username or password is empty. Aborting." >&2
  exit 1
fi

# Delete any existing entries so we can overwrite cleanly
security delete-generic-password -a "$ACCOUNT" -s "$SERVICE_USER" >/dev/null 2>&1 || true
security delete-generic-password -a "$ACCOUNT" -s "$SERVICE_PASS" >/dev/null 2>&1 || true

security add-generic-password -a "$ACCOUNT" -s "$SERVICE_USER" -w "$IBKR_USERNAME"
security add-generic-password -a "$ACCOUNT" -s "$SERVICE_PASS" -w "$IBKR_PASSWORD"

echo
echo "Done. Credentials stored encrypted in macOS Keychain."
echo
echo "Next steps:"
echo "  Start the stack:   ./scripts/compose.sh up backend-poc"
echo "  Rotate:            re-run this script"
echo "  Manual inspection: open 'Keychain Access' app, search for 'cautiouswetfloor'"
echo "  Delete:"
echo "    security delete-generic-password -a ${ACCOUNT} -s ${SERVICE_USER}"
echo "    security delete-generic-password -a ${ACCOUNT} -s ${SERVICE_PASS}"
echo
echo "You can now safely delete the .env file (if you have one with credentials):"
echo "    rm .env"
