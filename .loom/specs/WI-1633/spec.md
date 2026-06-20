# WI-1633 Spec

## Suite Path

- Suite path: not_applicable

- Formal-suite not_applicable: rationale: WI-1633 is a bounded PR4 CLI surface cleanup slice whose acceptance is carried by the Work Item, PR metadata, CLI contract checks, command help output, and current-head implementation review; creating a full spec/plan/implementation-contract suite would restate those runtime checks without adding a separate product contract. consumer boundary: this decision only skips formal suite artifacts; fact-chain/status carriers, current-head review, PR metadata/readback, hosted checks, PR gate, release judgment, controlled merge, and post-merge closeout remain required. recheck condition: require a minimal or full suite if this PR starts changing npm package payload contents, host verify global provider semantics, legacy residue gate behavior, migration playbook, or v0.17.0 release mechanics. scope proof: `git diff origin/main...HEAD` must stay limited to issues #1633/#1639 implementation, CLI contract tests, command docs, and WI-1633/PR4 carrier evidence. review requirement: current-head review must consume the final host/skills command surface, no-target-repo-write proof, CLI contract evidence, and command matrix documentation.
