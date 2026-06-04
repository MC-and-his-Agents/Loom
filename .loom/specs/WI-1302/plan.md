# Plan

- Suite path: full

## Implementation

- Extend the shared `loom_flow.py` suite-ready result set to include the canonical formal-suite NA result.
- In `spec_review_gate_payload`, consume a canonical `suite validate` formal-suite NA result as formal spec-review non-applicability.
- Keep implementation review status independent from the suite path decision.
- Regenerate managed skill runtime copies after changing the shared runtime.
- Add CLI contract coverage for legal formal-suite NA, invalid rationale, and implementation review non-bypass.

## Validation

- S1 -> automated validation evidence: focused docs-contract suite NA gate contract assertion.
- S2 -> automated validation evidence: invalid-rationale branch in the focused docs-contract suite NA gate contract assertion.
- S3 -> automated validation evidence: implementation review block assertion in the focused docs-contract suite NA gate contract assertion.
- AC-1 -> test evidence: `SPEC_REVIEW_SUITE_READY_RESULTS` includes the legal formal-suite NA result.
- AC-2 -> test evidence: spec gate payload returns the formal-suite NA result and no fallback for legal suite decision.
- AC-3 -> test evidence: blocked suite validation keeps spec gate blocked.
- AC-4 -> test evidence: implementation review still reports missing review artifact.
