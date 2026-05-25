# Current Status

## Derived Fact Chain View

- Item ID: WI-998
- Goal: Update README entrypoints so #885 presents Loom as a CLI-first operating layer.
- Scope: README.md and README.zh-CN.md only, plus WI-998 carriers required for PR readiness; align the public entrypoint with #885, #896, and #996 without changing CLI behavior or release versions.
- Execution Path: issue #998 -> branch work/998-cli-first-readme -> formal worktree /Users/mc/dev/Loom-998-cli-first-readme -> PR TBD
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-998.md
- Review Entry: .loom/reviews/WI-998.json
- Validation Entry: python3 tools/check_cli_contract.py; python3 tools/version_surface_check.py; npm --prefix packages/loom-installer run check:docs; make check; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-998; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py pr-gate check --target . --pr <PR> --head-sha <HEAD> --item WI-998
- Closing Condition: README.md and README.zh-CN.md present `loom` CLI as the primary control plane, describe loom-installer as compatibility shim / adapter-managed install / legacy bridge, #998 PR is merged, and #996 can consume the PR, checks, and merge commit.
- Current Checkpoint: build
- Current Stop: README.md and README.zh-CN.md have been updated in the formal worktree; local CLI, version, doc sync, fact-chain, and shadow-parity checks pass; review is next.
- Next Step: Record spec/general review, run full validation, then open PR.
- Blockers: None recorded.
- Latest Validation Summary: Passed before review: `python3 tools/check_cli_contract.py`; `python3 tools/version_surface_check.py`; `npm --prefix packages/loom-installer run check:docs`; `python3 .loom/bin/loom_flow.py fact-chain --target .`; `python3 .loom/bin/loom_flow.py shadow-parity --target .`; `git diff --check`.
- Recovery Boundary: Continue from `/Users/mc/dev/Loom-998-cli-first-readme` on branch `work/998-cli-first-readme`; do not change CLI behavior, installer versions, release tags, or #996 release judgment in this batch.
- Current Lane: cli-first readme entrypoint

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_cli_contract.py; python3 tools/version_surface_check.py; npm --prefix packages/loom-installer run check:docs; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-998.md
- Dynamic Truth: .loom/progress/WI-998.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
