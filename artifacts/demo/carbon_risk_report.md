# Carbon Risk Lab report

> **Synthetic only:** This portfolio and every simulated issuance&#44; reversal&#44; price&#44; delivery&#44; counterparty&#44; and policy outcome are synthetic demonstration data&#46; They are not current market facts&#44; forecasts&#44; valuations&#44; or investment advice&#46;

- Portfolio: `synthetic&#45;diversified&#45;carbon&#45;book`
- Seed: `2026`
- Simulations: `1,000`
- Artifact schema: `1.0.0`

## Distribution and tail risk

| Metric | Synthetic value |
|---|---:|
| Baseline | 1,136,315.00 |
| Expected value | 870,468.62 |
| P05 / P50 / P95 | 306,289.73 / 876,024.26 / 1,352,845.44 |
| Loss VaR 95 | 830,025.27 |
| Loss CVaR 95 | 943,085.33 |
| Loss VaR 99 | 1,028,883.19 |
| Loss CVaR 99 | 1,136,315.00 |
| Probability of loss | 81.50% |

## Sensitivities

| Stress | Expected value change | Change % | CVaR95 change vs original baseline |
|---|---:|---:|---:|
| `reversal&#95;probability&#95;plus&#95;25pct` | -17,169.62 | -1.97% | 10,943.57 |
| `counterparty&#95;default&#95;plus&#95;25pct` | -9,424.09 | -1.08% | 9,690.41 |
| `policy&#95;haircut&#95;plus&#95;5pp` | -46,557.51 | -5.35% | 10,635.84 |
| `price&#95;volatility&#95;plus&#95;25pct` | -2,889.40 | -0.33% | 11,948.06 |

## Interpretation boundary

These outputs validate software behavior under explicitly synthetic assumptions. They are not prices, forecasts, ratings, verification outcomes, or investment advice.
