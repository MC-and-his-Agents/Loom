# WI-1683 Suite Path Decision

- Suite path: minimal

- Minimal suite rationale: WI-1683 changes runtime gate semantics and focused CLI fixtures for governance intensity classification. It needs a real implementation and contract-test path, but not the full research/readiness suite because the acceptance is bounded by issue #1683 and existing metadata contracts from WI-1682.
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: this PR generalizes an existing gate rather than defining a new public workflow or host mutation surface. consumer boundary: suite validate, review, PR gate, controlled merge, and closeout may consume this minimal spec, plan, evidence map, task carrier, and focused validation output. recheck condition: require full suite artifacts if scope expands into `loom ship`, host mutation, release mechanics, PR backlink repair, concise diagnostics, workflow changes, or public CLI command design.
- Consumer boundary: suite validate, review, merge-ready, PR gate, controlled merge, and closeout may consume this locator as the suite path decision for #1683 only. Current-head review, PR metadata readback, hosted checks, release/no-release judgment, and closeout remain required.
- Recheck condition: require expanded suite or separate implementation Work Items if the PR adds `loom ship`, host mutation behavior, release packaging, workflow enforcement, or metadata repair behavior.
- Scope proof: `git diff origin/main...HEAD` must remain limited to the WI-1683 carriers, governance intensity gate implementation, generated runtime mirrors, and focused CLI contract fixtures.
- Review requirement: `.loom/reviews/WI-1683.json` must review the current PR head before merge-ready.
