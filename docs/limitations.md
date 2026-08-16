# Limitations

- Inputs and outputs are synthetic and must not be described as current market or climate facts.
- The model is illustrative, not calibrated to a registry, methodology, project, counterparty, jurisdiction, or traded instrument.
- Gaussian copula-style dependence cannot represent every tail relationship.
- Event probabilities are stationary within a run.
- A reversal or default reduces the affected position to zero; recovery, buffers, insurance, replacement credits, and legal seniority are omitted.
- Liquidity, bid/ask spread, vintage, additionality, leakage, verification quality, basis, FX, tax, and transaction costs are omitted.
- VaR and CVaR are model outputs, not guarantees.
- A fixed seed is reproducible with identical inputs and an identical Python runtime. The checked-in golden demo is verified byte-for-byte on Python 3.9 and 3.12, but arbitrary portfolios can differ in the least-significant reported decimal across runtimes because the engine uses platform floating-point math. Record the runtime with material analyses.
- Sensitivities are local scenario comparisons, not causal estimates.
- Stressed loss VaR/CVaR uses the original unstressed baseline, not the stressed portfolio's recalculated baseline. This is a deliberate comparable-loss metric; it is not an accounting, valuation, or regulatory definition.
- Finite inputs that would overflow notional, volatility variance, or simulated intermediates are rejected rather than converted into non-finite risk metrics.
- Policy haircuts are bounded to `[0, 1]`; `1.0` means complete loss of value and remains complete under every random draw and adverse haircut stress.
- Artifact readers reject unknown or missing fields, coercive types, booleans used as numbers, and blank text. Markdown reports conservatively encode punctuation in untrusted labels, including image, link, and autolink delimiters.
- Report output path components and pre-existing artifacts must be real directories and regular files, not symbolic links. The three report formats are staged before commit and restored as one prior set if publication fails partway through. Cooperating writers serialize publication with an advisory lock on the verified output directory; locking fails closed when unavailable, but cannot coordinate non-cooperating writers or filesystems that ignore `flock`-style locks.

Do not use this software for investment, verification, procurement, compliance, or climate-impact decisions without independently validated data, domain review, and a fit-for-purpose model.
