# Research and differentiation

Research reviewed on 2026-08-16. These primary sources informed the risk categories and reporting contract. No source code, data, project ratings, market observations, or model parameters were copied.

## Primary sources

| Source | What informed this project |
|---|---|
| [ICVCM Core Carbon Principles Assessment Framework](https://icvcm.org/assessment-framework/) | Integrity is multi-dimensional; a portfolio tool should expose assumptions rather than collapse project quality into a hidden number. |
| [Verra VCS Program Details](https://verra.org/programs/verified-carbon-standard/vcs-program-details/) | Issuance, monitoring/verification, registry processes, and reversal treatment are distinct lifecycle concerns. |
| [World Bank State and Trends of Carbon Pricing](https://www.worldbank.org/en/publication/state-and-trends-of-carbon-pricing) | Carbon pricing instruments and crediting mechanisms exist in heterogeneous policy and market contexts; price should be a scenario input, not a universal constant. |
| [Rockafellar and Uryasev publication list](https://uryasev.ams.stonybrook.edu/publications/) | VaR describes a quantile threshold while CVaR/expected shortfall summarizes loss beyond a tail threshold; both should be reported with clear confidence levels. |

## Deliberate differentiation

Carbon Risk Lab is a portable scenario engine, not a registry, verifier, pricing service, quality rating, or investment product.

- issuance, reversal, delivery delay, default, policy haircut, and price are explicit stochastic mechanisms;
- shared latent factors create correlated scenarios instead of a misleading sum of independent risks;
- a dedicated seed and common random numbers make base/stress comparisons replayable;
- position expectations, event rates, percentiles, VaR, CVaR, and sensitivities remain auditable in one artifact;
- all assumptions are supplied locally and the runtime has no data-provider dependency.

The engine intentionally does not infer project integrity from a standard, label, methodology, or geography. A future integration may map externally reviewed inputs into the schema, but the provenance and judgment must remain visible.

## Data boundary

Every bundled position, geography, price, probability, delay, correlation, and simulated outcome is synthetic. The linked sources motivate risk separation only and do not calibrate the demo.
