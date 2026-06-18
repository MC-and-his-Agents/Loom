# WI-1515 Suite Decision

## Suite Path Decision

- Suite path: not_applicable

- Formal-suite not_applicable: rationale: WI-1515 is the milestone/12 release-required closeout lane. It records release evidence, version authority, host readback, and terminal closeout consumption for already-merged milestone/12 work; it does not define new product behavior, runtime semantics, gate schema, or implementation acceptance scenarios. consumer boundary: this decision skips only formal spec-suite artifacts for #1515; release-required evidence, review, PR metadata, fact-chain, hosted checks, target branch readback, closeout reconciliation, shadow freshness, and #1505/#1515 terminal carrier sync remain required. recheck condition: require a minimal or full suite if #1515 expands beyond release/version evidence and terminal closeout into new CLI/runtime behavior, gate behavior, schema changes, fixture semantics, generated skill payload changes beyond version metadata, or external-visible release mechanics. scope proof: code behavior changes were delivered by the milestone/12 child issues; this lane only bumps the Loom CLI release version, records release readiness evidence, and prepares final closeout evidence. review requirement: current-head review must consume the release/version diff and closeout evidence before merge-ready or release PR merge.
