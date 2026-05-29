# Implementation Contract

- Work Item: WI-1143
- Parent FR: #1136
- Phase: #1107
- Contract consumed: docs/methodology/harness/full-spec-suite-cli-surface.md; docs/methodology/harness/gate-chain.md; docs/methodology/harness/task-carrier-contract.md
- Source truth boundary: reconciliation findings consume suite gate validation as evidence and do not replace Work Item, review, merge-ready, closeout, Project, or docs/source truth.
- Host write boundary: suite drift findings are blocking audit evidence; `reconciliation sync` must not invent host writes for unsupported suite drift kinds.
- Validation boundary: focused CLI contract, generated skills surface check, source contract-only loom_check, and release/package/version checks according to touched surfaces.
