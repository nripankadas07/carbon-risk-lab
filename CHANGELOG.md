# Changelog

## 0.1.0 - 2026-08-16

- Preserve the exact 100% policy-haircut boundary and monotone adverse haircut sensitivities.
- Reject non-finite derived exposure, volatility variance, and simulation intermediates.
- Require exact artifact schemas, strict JSON types, non-empty text, and no boolean-as-number or string coercion.
- Define all stressed tail losses against the original unstressed baseline so CVaR sensitivity changes are comparable.
- Return stable CLI validation errors and neutralize all Markdown image, link, and autolink delimiters in untrusted report text.
- Initial correlated synthetic portfolio simulator.
- VaR, CVaR, percentiles, event rates, and sensitivities.
- Versioned JSON input and JSON/Markdown/HTML report artifacts.
