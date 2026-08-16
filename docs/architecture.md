# Architecture

`model.py` validates the versioned portfolio boundary. `engine.py` creates common normal shocks for market, physical, counterparty, and policy conditions, then mixes each common shock with position-specific noise according to explicit correlations.

Each simulation applies:

1. issuance realization;
2. reversal realization;
3. counterparty default;
4. delivery delay and discounting;
5. policy haircut;
6. lognormal price movement.

The engine retains the portfolio distribution long enough to calculate interpolated percentiles, VaR, CVaR, event rates, and expected position values. Sensitivities rerun the identical seed and simulation count with one controlled assumption changed, reducing random comparison noise. Every stressed loss distribution uses the original unstressed baseline: `loss = original baseline value - stressed scenario value`. Consequently the reported CVaR change compares tail losses on one reference, including when a stress changes the stressed portfolio's own baseline.

Input validation checks derived notional and volatility variance before sampling, and every simulated intermediate must remain finite. A policy haircut of `1.0` is an absorbing full-loss boundary. Adverse haircut sensitivities are monotone and capped at `1.0`, so they can never reduce the starting haircut.

The result artifact—not report presentation—is the source of truth. JSON, Markdown, and HTML renderers consume the same dictionary.

## Schema policy

Schema versions are independent from package releases. Readers require exactly the documented portfolio and position fields, reject missing or unknown fields, accept numbers only as finite JSON numbers (never booleans or strings), and require all text fields to be non-empty strings. Backward-incompatible semantic changes require a new major schema version.
