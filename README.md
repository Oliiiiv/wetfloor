# CautiousWetfloor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
![Status](https://img.shields.io/badge/status-phase%200%20de--risking-orange)

**Status: Phase 0 — Under heavy development.** Not yet usable.

---

## What is CautiousWetfloor?

CautiousWetfloor unifies in one self-hosted Docker compose:

- **Portfolio tracking** across IBKR accounts
- **AI-assisted news sentiment** via FinBERT
- **Tax-aware compliance** for international students (W-8BEN, 1042-S, residency tracking)
- **Household co-investment planning** for couples with independent accounts
- **Excel-native workflows** via xlwings (live cell formulas to your portfolio)
- **Institutional-grade risk analytics** (VaR, Black-Litterman, factor models, HRP)
- **Algorithmic trading** (template library → backtesting → visual editor)

---

## Quick Start

### Prerequisites

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
2. An IBKR account. [Paper trading](https://www.interactivebrokers.com/en/trading/free-trial.php) is recommended for first run.
3. API access enabled in IBKR Account Management → Settings → API → Settings → Enable ActiveX and Socket Clients
4. For **live** mode only: IB Key activated on IBKR Mobile (the only 2FA method that works for headless containers)
5. macOS recommended (credentials go in Keychain). Other platforms can fall back to a `.env` file.

### One-time credential setup

```bash
# Paper credentials (default keychain entry: ibkr_paper)
./scripts/setup-credentials.sh

# Live credentials (optional, stored under a separate entry so both can coexist)
IBKR_KEYCHAIN_ACCOUNT=ibkr_live ./scripts/setup-credentials.sh
```

Credentials are stored encrypted in the macOS Keychain. **No plaintext on disk.**

### Run the stack

```bash
# Paper mode (default; safe for development)
./scripts/compose.sh up

# Live mode (real money; requires IB Key push approval on first connect)
./scripts/compose.sh --live up
```

Open http://localhost:3000 once all three containers are up.

### Mode flags

| Flag      | TRADING_MODE | Keychain entry | API port | Banner |
|-----------|--------------|----------------|----------|--------|
| (none)    | paper        | `ibkr_paper`   | 4004     | green  |
| `--paper` | paper        | `ibkr_paper`   | 4004     | green  |
| `--live`  | live         | `ibkr_live`    | 4003     | red    |

Live mode prints a red warning banner on startup. `READ_ONLY_API=yes` is the default safety net; for belt-and-suspenders also enable the read-only flag in IBKR Account Management → Settings → API.

### Common commands

```bash
./scripts/compose.sh ps                          # service status
./scripts/compose.sh logs backend -f             # follow backend logs
./scripts/compose.sh logs ib-gateway -f          # follow Gateway logs (auth, 2FA, connection)
./scripts/compose.sh down                        # stop everything

# Any subcommand accepts --live / --paper:
./scripts/compose.sh --live logs backend -f
./scripts/compose.sh --live down

# Phase 0 de-risk POC (still available as a regression harness):
./scripts/compose.sh up backend-poc
```

---

## License

MIT — see [`LICENSE`](./LICENSE). Not affiliated with Interactive Brokers LLC.
