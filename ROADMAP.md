# Roadmap

Carbon Risk Lab is at `0.1.0`. The immediate goal is stronger model transparency and validation, not more synthetic precision.

## 0.2 — Assumption diagnostics

- user-supplied correlation matrices with positive-semidefinite validation;
- convergence diagnostics and Monte Carlo standard errors;
- versioned CSV export for distributions and position attribution;
- stable validation codes for every rejected assumption.

Exit criterion: users can tell whether a change is model risk, sampling noise, or a portfolio effect.

## 0.3 — Scenario and attribution depth

- named policy/market scenario sets with provenance metadata;
- marginal and component tail-risk attribution;
- deterministic chunked simulation for larger runs;
- back-to-back scenario comparison reports.

Exit criterion: every portfolio-level tail change can be traced to scenario inputs and positions.

## 1.0 — Governed analytical contract

- documented schema migration and reproducibility policy;
- reference calculations for VaR/CVaR and event frequencies;
- external calibration adapters that keep source licensing and as-of dates explicit;
- independent review of numerical methods and financial interpretation language.

## Non-goals

Project verification, live pricing, credit ratings, registry reconciliation, legal conclusions, and investment recommendations remain out of scope.
