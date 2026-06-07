# WI-1322 Plan

- Suite path: minimal

- Full-suite-artifacts not_applicable: rationale: WI-1322 already has frozen upstream issue contracts and needs a focused implementation plan for gate behavior and fixtures, not a full artifact suite. consumer boundary: review, merge-ready, PR gate, hosted CI, controlled merge, and closeout consume this plan together with targeted validation evidence; they must still require fact-chain, current-head review, PR metadata/readback, release/no-release judgment, and closeout evidence. recheck condition: require a full suite if implementation scope expands into #1323 fixture matrix, #1324 parent closeout, release mechanics, external-visible behavior, runtime provider behavior, review engine behavior, broad merge strategy, or new downstream machine-consumed fields. scope proof: current diff is limited to the #1322 gate behavior slice, targeted tests, contract clarification, runtime copy sync, and WI-1322 carriers. review requirement: current-head implementation review is required.

## Steps

1. Read #1322 and terminalized dependencies #1319/#1316/#1317/#1320/#1321.
2. Add docs-governance lite metadata semantics to the PR metadata and pr-gate consumption layer.
3. Preserve the single merge-ready PR metadata carrier while allowing review/pre-review preflight to consume it early.
4. Add targeted positive and fail-closed fixtures to the CLI contract check.
5. Synchronize source, generated skill runtime copies, and repo-local `.loom/bin` runtime copy.
6. Update WI-1322 carriers, record current-head review, run local gates, open/update PR, wait for hosted checks, controlled merge, and post-merge closeout.

## Validation Mapping

- S1 -> automated validation evidence: `python3 tools/check_cli_contract.py --surface aggregate` docs-governance lite suite/pr-gate fixture.
- S2 -> automated validation evidence: `python3 tools/check_cli_contract.py --surface aggregate` metadata negative fixtures and existing stale review / PR body mismatch / semantic review disposition fixtures.
- S3 -> automated validation evidence: `python3 tools/check_cli_contract.py --surface aggregate` review-surface metadata preflight fixture.
- AC-1 -> test evidence: docs-governance lite suite validate formal-suite bypass and pr-gate positive fixture.
- AC-2 -> test evidence: targeted metadata and pr-gate negative fixtures.
- AC-3 -> test evidence: fact-chain, review/head binding, merge checkpoint, PR metadata preflight, hosted checks, controlled merge, and closeout evidence.
- AC-4 -> test evidence: review-surface metadata preflight consumes the `merge_ready` carrier.
