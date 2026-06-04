# Contracts

- A canonical `suite validate` JSON formal-suite NA result means the formal suite path is explicitly non-required and has passed suite-level rationale validation.
- Spec-review gate may consume that result as a formal-suite NA gate result.
- This contract does not replace implementation review, PR head binding, fact-chain, CI/checks, release/no-release evidence, or closeout evidence.
- If suite validation blocks because the rationale is missing or invalid, spec-review gate must also block.
