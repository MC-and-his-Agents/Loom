# WI-1240-1242 Spec

## Suite Contract

- Suite path: minimal
- Work Item / FR locator: #1240 / #1241 / #1242
- Path decision provenance: #1239 froze the runtime provider contract, and #1240/#1241/#1242 bound this first implementation batch to installed-state, doctor/verify, and executable fact-chain/status/story-carrier entrypoints.
- Full-suite-artifacts not_applicable: rationale: this batch has a frozen parent contract, issue-scoped acceptance, targeted CLI/runtime smoke evidence, and no migration repair or release closeout implementation; consumer boundary: build, review, PR gate, hosted checks, release judgment, and parent closeout consume this minimal suite plus Work Item and build evidence; recheck condition: promote to full suite if the batch expands into #1243/#1244 migration repair/fixtures, #1245/#1246 docs/release closeout, destructive runtime repair, or a new provider selection taxonomy.

## Scope

Implement the first global-cli runtime provider executable support batch so repositories without `.loom/bin` can be accepted only when the `global-cli` provider contract is satisfied, while repo-local wrapper behavior remains compatible and stale `.loom/bin` is not misclassified as current success.

## Scenarios

- S1: Installed-state validation accepts metadata-only global-cli runtime provider records with explicit provider requirements and fails closed on malformed provider data.
- S2: Detect/doctor/verify accept no-`.loom/bin` repositories only when global-cli provider requirements are satisfied.
- S3: Stale `.loom/bin` paths are classified as repairable retained runtime residue instead of current executable truth.
- S4: Fact-chain, status, and story-carrier entrypoints report current execution through global `loom ... --json` commands for global-cli provider repositories.
- S5: Governance command-prefix behavior uses bare `loom` for global-cli provider state and preserves repo-local wrapper fallback for existing repositories.
- S6: Runtime copies, manifest/demo fixture surfaces, and targeted checks stay in parity with the shared provider behavior.

## Acceptance Criteria

- AC-1: `tools/loom.py` models `global-cli` and `repo-local-wrapper` runtime providers consistently in installed-state, detect, doctor, verify, and repair classification.
- AC-2: No-`.loom/bin` success requires satisfied global-cli provider requirements; malformed provider records and stale `.loom/bin` old paths do not produce false success.
- AC-3: Fact-chain/status/story-carrier entrypoints expose global `loom` commands for global-cli provider state and do not point to stale `.loom/bin` executables.
- AC-4: Repo-local wrapper compatibility is preserved for existing provider or fallback state.
- AC-5: Governance surface command-prefix parity is applied to source, generated skill runtime copies, and demo bootstrap fixtures.
- AC-6: Regression evidence covers installed-state validation, doctor/verify, fact-chain/status/story-carrier, stale bin residue, malformed provider fail-closed, governance prefix parity, demo fixture sync, `git diff --check`, py_compile, skills check, PR gate, and hosted checks.
- AC-7: Release impact is recorded for downstream release evidence handling; release execution and docs/release closeout stay outside this batch.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: this first implementation batch is bounded to runtime provider executable support and required parity fixtures/carriers; consumer boundary: no separate research, migration repair, or release-publication artifact is required to review the code and carrier behavior; recheck condition: require additional suite artifacts if provider selection semantics conflict with #1239, downstream no-`.loom/bin` evidence cannot be reproduced, runtime/admission failure types cannot be classified, or the work expands into #1243/#1244/#1245/#1246.
