# WI-1323 Plan

- Suite path: minimal

- Full-suite-artifacts not_applicable: rationale: WI-1323 has a narrow fixture/test-helper implementation plan and consumes frozen upstream contracts and completed #1321/#1322 behavior; extra full-suite artifacts would not add decision value for this regression matrix. consumer boundary: review, merge-ready, PR gate, hosted CI, controlled merge, and closeout consume this minimal plan plus targeted fixture evidence; they must still require fact-chain, current-head review, PR metadata/readback, no-release judgment, PR gate, controlled merge, and closeout evidence. recheck condition: require a full suite if scope expands into gate contract/schema redesign, runtime behavior, release mechanics, external-visible behavior, permissions, or #1324 parent/final closeout. scope proof: current diff is limited to targeted regression fixtures/test helper code and WI-1323 carriers. review requirement: current-head implementation review is required.

## Steps

1. Read issue #1323 and terminalized #1319/#1320/#1321/#1322 carriers, plus #1316/#1317 gate contract and current fixture/gate entrypoints.
2. Extend targeted CLI contract fixtures for docs-governance light suite-bypass positive coverage and high-risk/mismatch fail-closed cases.
3. Keep fixture assertions bound to real `loom_flow.py pr-metadata`, `suite validate`, and `pr-gate check` behavior.
4. Record WI-1323 carriers, no-release evidence, current-head review, PR metadata, hosted checks, controlled merge, and post-merge closeout.
5. Preserve #1324 as follow-up parent/final closeout scope.

## Validation Mapping

- Scenario S1 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py` docs-governance lite positive suite/pr-gate fixture.
- Scenario S2 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py` metadata and pr-gate negative fixtures for runtime/code, fixture, release-impacting docs, missing rationale, blocking release judgment, and suite mismatch.
- Scenario S3 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py` PR body readback drift, carrier/head mismatch, PR branch mismatch, and stale review/head binding fixtures.
- Acceptance AC-1 -> test evidence: targeted fixture test evidence plus suite validate result.
- Acceptance AC-2 -> test evidence: targeted negative fixture evidence and pr-gate dry check.
- Acceptance AC-3 -> test evidence: local validation, current-head review, PR gate, hosted checks, controlled merge, and closeout evidence.
- Acceptance AC-4 -> structural evidence: Git diff review, no-release judgment, and closeout boundary statements.
