# AI-assisted development disclosure

OpenAI Codex assisted with research synthesis, model decomposition, implementation scaffolding, documentation drafting, and test-case generation for the initial `0.1.0` release.

Human review remains required. The maintainer owns the assumptions, domain interpretation, license review, and decision to use or publish results. AI-generated changes are treated as untrusted until tests and an appropriate subject-matter review are complete.

## Verification performed for 0.1.0

- seeded equality and common-random-number sensitivity tests;
- percentile and VaR/CVaR ordering checks;
- invalid and non-finite assumption rejection;
- strict JSON serialization and versioned artifact round-trips;
- byte-for-byte golden report comparison;
- Python 3.9 grammar, wheel-build, install, and console-script smoke tests.

No external project code, market data, or portfolio data was copied. The runtime makes no model or network calls; every bundled value and outcome is synthetic and is not investment advice.
