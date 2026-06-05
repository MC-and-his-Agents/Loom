# Current Status

## Derived Fact Chain View

- Item ID: WI-1315
- Goal: Define a project-neutral change governance intensity model.
- Scope: Add the generic governance methodology contract for risk dimensions, `light` / `standard` / `reinforced` intensity tiers, upgrade triggers, minimum evidence for light paths, downgrade prohibitions, and project mapping boundaries. Link it from governance landing docs. Do not implement Loom gate behavior, CLI metadata, fixtures, generated skills, runtime behavior, release behavior, or AGENTS.md rules.
- Execution Path: issue #1315 -> branch work/1315-generic-governance-intensity -> PR #1325 -> docs review -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1315.md
- Review Entry: .loom/reviews/WI-1315.json
- Validation Entry: git diff --check; docs contract review; Loom-specific term scan; suite validate not_applicable; PR CI.
- Closing Condition: PR #1325 is merge-ready, merged to main, #1315 is closed with validation and no-release evidence, and #1316/#1317 can reference the frozen generic model without redefining its tiers.
- Current Checkpoint: merge_ready
- Current Stop: Generic change governance intensity model is frozen in docs at head 2da81f8a393d9683cd71ca7c767b7e21b574659e; carrier head 591ab632e98a196a66bf6837ad80151612bbcc87 binds WI-1315 portable workspace entry, fact-chain, formal suite not_applicable, and review evidence for PR #1325.
- Next Step: Re-run local pr-gate and hosted PR checks for PR #1325; if all pass, proceed to merge-ready handoff.
- Blockers: None
- Latest Validation Summary: Carrier head 591ab632e98a196a66bf6837ad80151612bbcc87 passed `git diff --check`; `python3 tools/loom.py fact-chain --target . --json` passed for WI-1315 with portable workspace entry `.`; `python3 tools/loom.py suite validate --target . --item WI-1315 --json` returned result `not_applicable` with zero blocking gaps and locator `.loom/specs/WI-1315/spec.md`; `python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1315 --dry-run` passed; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed; `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1315` passed; docs review verified risk dimensions, `light` / `standard` / `reinforced` tiers, upgrade triggers, minimum light-path evidence, downgrade prohibitions, and project mapping boundaries; Loom-specific term scan found no `.loom`, `Work Item`, `pr-gate`, `loom_check`, `guardian`, `suite validate`, or `git worktree` terms in the generic model body; PR body records no-release evidence.
- Recovery Boundary: This Work Item only owns #1315 generic governance methodology docs, landing links, and WI-1315 readiness carriers. Do not implement Loom gate behavior, CLI metadata, fixtures, generated skills, runtime behavior, release behavior, or AGENTS.md rules here.
- Current Lane: merge-ready

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: local docs review, `git diff --check`, Loom-specific term scan, suite validate not_applicable, and PR #1325 hosted checks
- Lane Entry: merge-ready

## Sources

- Static Truth: .loom/work-items/WI-1315.md
- Dynamic Truth: .loom/progress/WI-1315.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
