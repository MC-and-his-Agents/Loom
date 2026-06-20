# WI-1626-1631-1634-1635 Spec

## Suite Path

- Suite path: not_applicable

- Formal-suite not_applicable: rationale: WI-1626-1631-1634-1635 is a bounded PR5 convergence slice whose acceptance is carried by Work Item scope, CLI/package contract tests, npm dry-run package surface, migration documentation, current-head review, PR metadata, hosted checks, and closeout. consumer boundary: this decision only skips formal suite artifacts; fact-chain/status carriers, current-head review, PR metadata/readback, hosted checks, PR gate, release/no-release judgment, controlled merge, and post-merge closeout remain required. recheck condition: require a minimal or full suite if this PR starts changing VERSION, release workflow execution, tag/npm/GitHub Release mechanics, external permissions, or milestone final closeout. scope proof: `git diff origin/main...HEAD` must stay limited to issues #1626/#1631/#1634/#1635 implementation, tests, docs, and PR5 carrier evidence. review requirement: current-head review must consume final host verify behavior, package payload contents, legacy residue hard gate, migration doc, and aggregate validation evidence.
