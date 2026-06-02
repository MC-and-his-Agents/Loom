# Current Status

## Derived Fact Chain View

- Item ID: WI-1203
- Goal: Close out release readiness for Codex workstation registration by bumping Loom CLI version to an unpublished release after PR #1212 changed CLI behavior.
- Scope: WI-1203 owns only release-readiness closeout for #1196 after PR #1212: VERSION, package.json, skills/*/loom-package.json repo_version metadata, WI-1203 Loom carriers, PR/CI/release evidence, and issue closeout comments. Ownership excludes #1204 downstream plugin layout implementation, target repository layout migrations, command naming changes, user-level Codex config semantics, and any change to workstation registration behavior.
- Execution Path: issue #1203 -> branch work/1203-release-version-bump -> PR pending -> main release workflow validation.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1203.md
- Review Entry: .loom/reviews/WI-1203.json
- Validation Entry: python3 tools/version_surface_check.py; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; python3 tools/check_cli_contract.py; git diff --check; PR/CI; main release workflow.
- Closing Condition: #1203 has closeout evidence, release workflow on main passes for merge commit after version bump, and #1197-#1203 then #1196 issue tree is closed with evidence.
- Current Checkpoint: build checkpoint
- Current Stop: Release version bump to v0.13.8 is implemented on branch `work/1203-release-version-bump`; local release/version/npm checks are passing and CLI contract is being re-consumed under WI-1203 scope.
- Next Step: Finish local CLI contract, record spec and implementation review, open PR, merge after CI, validate main release workflow, then close #1197-#1203 and #1196 with evidence.
- Blockers: None recorded.
- Latest Validation Summary: Passing: `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `git diff --check`. Pending: `python3 tools/check_cli_contract.py`, PR/CI, main release workflow, and issue closeout.
- Recovery Boundary: WI-1203 owns only release-readiness version metadata and closeout evidence for #1196 after PR #1212. It must not implement #1204 downstream plugin layout, alter workstation registration behavior, rename commands, or change user-level Codex configuration semantics.
- Current Lane: loom-hardening/codex-workstation-registration/release-closeout

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make loom-check
- Lane Entry: loom-hardening/codex-workstation-registration/release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1203.md
- Dynamic Truth: .loom/progress/WI-1203.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
