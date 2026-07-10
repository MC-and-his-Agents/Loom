# WI-1834 Plan

## Phases

- P1: Define runtime-upgrade maintenance profile semantics, version aliases, help output, CLI matrix, and bilingual README guidance.
- P2: Implement runtime-upgrade status and prepare for CLI/repo workflow pin/plugin-cache diagnosis plus repo-only mutation boundary.
- P3: Implement runtime-upgrade check and closeout with fail-closed repo PR validation and advisory-by-default plugin/cache handling.
- P4: Synchronize runtime copies, plugin payload metadata/hash, and examples/new-project fixture.
- P5: Create PR #1839, bind PR metadata and review to stable head, run PR gate/hosted checks, merge.
- P6: Execute #1838 v0.24.0 release/readback/issue closeout/milestone closeout from main after merge.

## Scenario Mapping

- S1 -> P1, P2
- S2 -> P2
- S3 -> P1, P2, P3
- S4 -> P3, P5
- S5 -> P3, P6
- S6 -> P6

## Acceptance Mapping

- A1 -> test evidence: `python3 tools/check_cli_contract.py --surface runtime-upgrade`; structural evidence: `docs/methodology/harness/cli-command-matrix.md`.
- A2 -> test evidence: `python3 tools/check_cli_contract.py --surface runtime-upgrade`; metadata evidence: runtime-upgrade-only PR intent profile.
- A3 -> test evidence: `python3 tools/check_cli_contract.py --surface runtime-upgrade`; manual evidence: README and README.zh-CN mutation-boundary wording.
- A4 -> test evidence: `python3 tools/check_cli_contract.py --surface runtime-upgrade`; PR evidence: PR #1839 metadata preflight/readback.
- A5 -> structural evidence: `python3 tools/check_cli_contract.py --surface aggregate`; package evidence: `python3 tools/check_npm_package.py --surface runtime-copy-parity`; docs evidence: README and README.zh-CN.
- A6 -> manual evidence: PR #1839 readback, review record, PR gate/hosted checks, merge commit, v0.24.0 GitHub Release/npm readback, and terminal closeout evidence.

## Validation

- `make py-compile`
- `make loom-demo-new-project-check`
- `python3 tools/check_cli_contract.py --surface runtime-upgrade`
- `python3 tools/check_cli_contract.py --surface pr-metadata`
- `python3 tools/check_cli_contract.py --surface aggregate`
- `python3 tools/check_npm_package.py`
- `python3 tools/check_npm_package.py --surface runtime-copy-parity`
- `python3 tools/loom.py skills release-check --json`
- `git diff --check`
- PR metadata preflight/readback for PR #1839
- Current-head review, PR gate, hosted checks, merge-ready, v0.24.0 release readback, and closeout after the PR head is stable

## Dependencies

- Implementation merge depends on PR #1839 head/body/review/carrier consistency and hosted check pass.
- #1838 release depends on PR #1839 merge to `main`.
- Multi-repo batch mode is deferred out of this milestone and is not completed by this plan.
