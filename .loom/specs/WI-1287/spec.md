# WI-1287 Suite Path Decision

- Suite path: not_applicable

- Formal-suite not_applicable:
  - rationale: WI-1287/WI-1288 are bounded gate/runtime enforcement changes for the already frozen #1286 contract, implemented in existing repo-local CLI surfaces with focused contract fixtures rather than a new product/user behavior spec suite. The work does not introduce #1289/#1291 merge check/run behavior, companion/guardian adapter fixtures, downstream repository policy, release mechanics, or a new scenario workflow beyond pr-gate review-head binding enforcement.
  - consumer boundary: suite validate consumes this locator only as the formal suite decision; implementation review, fact-chain, generated runtime parity, CLI contract tests, PR body machine carrier, current-head review record, pr-gate dry check, CI, release/no-release evidence, and merge-ready remain required.
  - recheck condition: require a full or minimal suite if this branch starts changing merge check/run, controlled merge, companion/guardian adapter behavior, downstream repository rules, release behavior, user-facing workflow semantics outside pr-gate, or any consumer beyond #1287/#1288 disposition/head-binding enforcement.
  - scope proof: `git diff origin/main...HEAD` must remain limited to #1287/#1288 carriers, review disposition/head-binding runtime logic, generated skill runtime copies, repo-local runtime copy, and focused CLI contract fixtures.
  - review requirement: `.loom/reviews/WI-1287.json` must be authored only after code, generated runtime, carrier, and PR body are stable, and its `reviewed_head` must equal the current PR head consumed by pr-gate.
