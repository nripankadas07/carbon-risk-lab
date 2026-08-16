# Changelog

## 0.1.1 - 2026-08-16

- Make interpolated percentiles return the exact plateau value when adjacent order statistics are equal, preventing empty VaR/CVaR tails caused by one-ULP overshoot.
- Validate percentile inputs as finite numbers, avoid opposite-sign interpolation overflow, and add a full Monte Carlo regression for a repeated maximum-loss distribution.
- Clarify runtime-scoped replayability and the stronger cross-supported-runtime guarantee for the checked-in golden demo.
- Publish report bundles through a staged, symlink-safe writer that rejects linked destinations and restores the complete prior set after a mid-commit failure.
- Serialize cooperating report writers with an exclusive advisory lock on the verified output directory, recheck target identities immediately before publication, and reconcile rename outcomes before rollback when a filesystem wrapper raises after completing the operation.
- Close fallback temporary descriptors when text-stream setup fails, while removing the abandoned staged file.
- Ship examples, golden artifacts, documentation, and the release checker in the source distribution; CI now extracts the sdist and reruns its full suite on Python 3.9 and 3.12.
- Migrate package license metadata to the SPDX form.

## 0.1.0 - 2026-08-16

- Preserve the exact 100% policy-haircut boundary and monotone adverse haircut sensitivities.
- Reject non-finite derived exposure, volatility variance, and simulation intermediates.
- Require exact artifact schemas, strict JSON types, non-empty text, and no boolean-as-number or string coercion.
- Define all stressed tail losses against the original unstressed baseline so CVaR sensitivity changes are comparable.
- Return stable CLI validation errors and neutralize all Markdown image, link, and autolink delimiters in untrusted report text.
- Initial correlated synthetic portfolio simulator.
- VaR, CVaR, percentiles, event rates, and sensitivities.
- Versioned JSON input and JSON/Markdown/HTML report artifacts.
