# Current Status

## Derived Fact Chain View

- Item ID: WI-783
- Goal: Record the .loom surfaces version-control policy for adoption/install safety
- Scope: Add the canonical adoption policy, link it from adoption and install docs, mirror it into the generated skills surface, and validate skills/loom checks
- Execution Path: docs/adoption
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-783.md
- Review Entry: .loom/reviews/WI-783.json
- Validation Entry: make skills-check; make loom-check
- Closing Condition: #783 is implemented, validated, reviewed, merged, and the policy is available to installed skills
- Current Checkpoint: merge checkpoint
- Current Stop: #783 implementation, docs, generated skill surface, and installer version bump are ready for PR gate consumption.
- Next Step: Merge PR #785 after CI and Loom PR gate pass, then close issue #783.
- Blockers: None recorded.
- Latest Validation Summary: make skills-check -> OK; make loom-check -> OK; installer package version bumped to 0.1.110 for generated skills payload change.
- Recovery Boundary: #783 is bounded to .loom surfaces version-control policy documentation, installed skills reference propagation, generated skills surface refresh, and required PR gate metadata.
- Current Lane: PR #785

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-783.md
- Dynamic Truth: .loom/progress/WI-783.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
