# Current Status

## Derived Fact Chain View

- Item ID: WI-1217
- Goal: Make metadata-only repository adoption a first-class Loom mode while preserving explicit embedded payload compatibility.
- Scope: WI-1217 owns the metadata-only adoption iteration across `docs/adoption/installation-taxonomy.md`, `docs/adoption/README.md`, `docs/adoption/codex-install.md`, `docs/adoption/host-adapter-matrix.md`, `docs/adoption/loom-installed-state-v2.md`, `docs/adoption/unified-install-experience.md`, `docs/methodology/harness/cli-command-matrix.md`, `plugins/loom/.codex-plugin/plugin.json`, `tools/loom.py`, `tools/check_cli_contract.py`, `skills/shared/scripts/loom_check.py`, `src/skills/shared/scripts/loom_check.py`, `skills/loom-adopt/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-build/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-handoff/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-init/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-merge-ready/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-pre-review/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-resume/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-retire/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-review/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-spec-review/.loom-runtime/shared/scripts/loom_check.py`, `skills/loom-story/.loom-runtime/shared/scripts/loom_check.py`, `examples/new-project/.loom/bin/loom_check.py`, `examples/new-project/.loom/bootstrap/init-result.json`, `examples/new-project/.loom/bootstrap/manifest.json`, `.loom/bootstrap/init-result.json`, `.loom/status/current.md`, `.loom/work-items/WI-1217.md`, `.loom/progress/WI-1217.md`, `.loom/progress/WI-1217-build-evidence.json`, `.loom/progress/WI-1204.md`, `.loom/reviews/WI-1217.json`, `.loom/reviews/WI-1217.spec.json`, `.loom/shadow/merge-ready-loom.json`, `.loom/shadow/closeout-loom.json`, `.loom/specs/WI-1217/spec.md`, `.loom/specs/WI-1217/plan.md`, `.loom/specs/WI-1217/implementation-contract.md`, `.loom/specs/WI-1217/evidence-map.md`, and `.loom/specs/WI-1217/task-carrier.md`. Ownership includes #1218-#1226 closeout evidence and release or no-release decision records, plus retiring the stale WI-1204 active progress marker after #1204/#1216 completed. Ownership excludes destructive migration of downstream repo-owned governance evidence, deleting target-owned skills, changing Codex Desktop private state semantics, and publishing without explicit release credentials and release readiness evidence.
- Execution Path: issue #1217 -> branch work/1217-metadata-only-adoption -> PR #1227 / CI -> target branch validation -> child issue closeout -> release or no-release decision.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1217.md
- Review Entry: .loom/reviews/WI-1217.json
- Validation Entry: make loom-check; python3 tools/check_cli_contract.py; python3 tools/check_release_surface.py; python3 tools/skills_surface.py check; metadata-only fixture install/validate/host verify/skills check/detect; embedded payload fixture host install/verify; docs checks; git diff --check; PR/CI.
- Closing Condition: #1218-#1226 and #1217 have closeout evidence, target PR or PRs are merged, target branch validates metadata-only adoption without requiring repo skills payload, embedded payload mode remains valid, and release is published or no-release decision is recorded.
- Current Checkpoint: merge
- Current Stop: PR #1227 is open for `work/1217-metadata-only-adoption`; short chain, focused gates, full `make loom-check`, supplemental checks, and refreshed spec/code review records passed locally; review records bind to implementation head `7de5f7c2e1e7709fb4889f86ce7dc4ec1c909093`.
- Next Step: Push refreshed review and merge-readiness carriers, validate PR #1227 CI, then continue issue closeout and release/no-release decision after target branch validation.
- Blockers: none
- Latest Validation Summary: Passing local evidence: `python3 tools/skills_surface.py check`; `python3 tools/loom.py skills check --target . --json`; `python3 .loom/bin/loom_flow.py shadow-parity --target .`; `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1217`; `python3 tools/loom_check.py --source-surface bootstrap-regression`; `python3 tools/loom_check.py --source-surface source-self-fixture`; full `make loom-check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`; `python3 tools/check_release_surface.py`; `git diff --check`; targeted metadata-only fixture passed `loom install --mode metadata-only --apply`, `installed-state validate`, `host verify --mode metadata-only`, `skills check`, and `detect`; targeted metadata-only pollution fixture blocked unexpected `plugins/loom/skills`; targeted embedded fixture passed `host install --mode plugin --apply` and `host verify --mode plugin`. Pending evidence: PR/CI, target branch validation, issue closeout, and release/no-release record.
- Recovery Boundary: Do not make metadata-only write or require `plugins/loom/skills`, `.agents/skills`, or root `skills`; do not encode user workstation registration as repo truth; do not delete downstream repo-owned governance evidence; preserve embedded payload mode compatibility.
- Current Lane: loom-metadata-only-adoption

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make loom-check
- Lane Entry: loom-metadata-only-adoption

## Sources

- Static Truth: .loom/work-items/WI-1217.md
- Dynamic Truth: .loom/progress/WI-1217.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
