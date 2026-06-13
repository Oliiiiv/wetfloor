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

## Quick Start (Phase 0 — POC stage)

The current code only validates that we can connect to IBKR paper trading from inside Docker.

### Prerequisites
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
2. An [IBKR paper trading account](https://www.interactivebrokers.com/en/trading/free-trial.php) (free)
3. API access enabled in your IBKR Account Management → Settings → API → Settings

### Run the de-risk POC

```bash
cp .env.example .env
# Edit .env and fill in your IBKR paper account credentials

docker compose up backend-poc
```

You should see your paper account net value and positions printed to the terminal.

---

## License

MIT — see [`LICENSE`](./LICENSE). Not affiliated with Interactive Brokers LLC.
