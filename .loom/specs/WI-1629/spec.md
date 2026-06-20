# WI-1629 Spec

## Suite Path

- Suite path: not_applicable

- Formal-suite not_applicable: rationale: WI-1629 is a bounded PR3 runtime installation slice whose acceptance is carried by the Work Item, PR metadata, CLI contract checks, temporary HOME install/register smoke tests, and current-head implementation review; creating a full spec/plan/implementation-contract suite would restate those runtime checks without adding a separate product contract. consumer boundary: this decision only skips formal suite artifacts; fact-chain/status carriers, current-head review, PR metadata/readback, hosted checks, PR gate, release judgment, controlled merge, and post-merge closeout remain required. recheck condition: require a minimal or full suite if this PR starts removing CLI modes/help, changing package surface, changing migration gates, changing release mechanics, or executing v0.17.0 release work. scope proof: `git diff origin/main...HEAD` must stay limited to issue #1629 implementation, CLI contract tests, and WI-1629/PR3 carrier evidence. review requirement: current-head review must consume the final install/register behavior, no-target-repo-write proof, CLI contract evidence, hosted-gate carrier changes, and PR2 terminal carrier sync.
