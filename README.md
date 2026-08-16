# Carbon Risk Lab

Carbon Risk Lab is a deterministic, standard-library Monte Carlo engine for examining synthetic carbon-credit portfolio risk under correlated issuance, reversal, price, delivery, counterparty, and policy scenarios.

> **Data boundary:** every bundled portfolio and simulated outcome is synthetic. Outputs are not current prices, climate facts, verification results, forecasts, valuations, or investment advice.

## Problem

Simple portfolio demos multiply units by a spot price and hide the path risks that determine delivery and value. Carbon Risk Lab makes those assumptions explicit, correlates them through common scenario factors, and reports the whole distribution rather than a single estimate.

## Proof

- Dedicated `random.Random(seed)` streams make runs replayable.
- Common market, physical, policy, and counterparty factors create correlated rather than independent scenarios.
- Reports include percentiles, loss VaR/CVaR at 95% and 99%, event rates, position expectations, and four controlled sensitivities.
- Inputs and outputs use stable `1.0.0` schemas.
- Portfolio readers require exact root and position fields, strict JSON types, and non-empty identifiers and labels; they never coerce booleans, strings, arrays, or objects into numbers or text.
- JSON, Markdown, and single-file HTML are emitted from the same artifact.
- Runtime and tests use only Python 3.9+ standard-library modules.

## 60-second demo

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
carbon-risk-lab demo --seed 2026 --simulations 5000 --output-dir reports
open reports/carbon_risk_report.html
```

Without installation:

```bash
PYTHONPATH=src python -m carbon_risk_lab demo --simulations 1000
```

Run the checked-in portfolio:

```bash
carbon-risk-lab run --portfolio examples/synthetic_portfolio.json --seed 42
```

Sensitivity loss VaR/CVaR is defined as `original unstressed baseline value - stressed scenario value`. Keeping one baseline makes adverse-value stresses comparable to the base run; it is not a claim about market loss.

## Architecture

```text
versioned portfolio
       |
common factors + position-specific shocks
       |
issuance / reversal / delay / default / haircut / price
       |
portfolio distribution -> VaR/CVaR/percentiles -> controlled stresses
       |
JSON / Markdown / self-contained HTML
```

See [architecture](docs/architecture.md) and [limitations](docs/limitations.md).

## Release materials

- [Research and differentiation](docs/research.md)
- [Roadmap](ROADMAP.md)
- [AI-assisted development disclosure](AI_ASSISTED.md)
- [Citation metadata](CITATION.cff)
- Golden demo: [HTML](artifacts/demo/carbon_risk_report.html), [Markdown](artifacts/demo/carbon_risk_report.md), [JSON](artifacts/demo/carbon_risk_report.json)

## Limits

This is a transparent scenario laboratory, not a valuation, registry, verification, or market-data system. The bundled distributions are deliberately simplified; no calibration to current projects or markets is implied. Tail estimates depend on the chosen seed, simulation count, probability model, and user-supplied assumptions. See [docs/limitations.md](docs/limitations.md) for the full boundary.

## Development

```bash
make test
make demo
make golden
```

MIT licensed.
