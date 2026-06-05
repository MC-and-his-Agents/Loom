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
- Current Checkpoint: closed
- Current Stop: PR #1325 merged to `main` at merge commit `bbb01778626f9783e4fc068c506c5aa09f30a92f`; issue #1315 is closed with post-merge closeout evidence; #1316/#1317 can reference the frozen generic change governance intensity model without redefining its tiers.
- Next Step: No WI-1315 implementation action remains; downstream #1316/#1317 should consume this frozen generic model through their own Loom-specific mapping/gate work.
- Blockers: None
- Latest Validation Summary: Post-merge closeout evidence, 2026-06-05: PR #1325 merged/closed with head `dfe6b0f07f9a29b1ee60dd1bcf985af4c4f53639` and merge commit `bbb01778626f9783e4fc068c506c5aa09f30a92f`; `origin/main` readback returned the same merge commit; hosted checks passed (`loom-pr-merge-gate`, two aggregate `loom-check` runs, `py-compile`, `demo-bootstrap`, `repo-local-cli`, `root-self-governance`); `python3 .loom/bin/loom_flow.py pr-gate check --target . --item WI-1315 --pr 1325 --head-sha dfe6b0f07f9a29b1ee60dd1bcf985af4c4f53639` passed; `python3 .loom/bin/loom_flow.py controlled-merge check --target . --item WI-1315 --pr 1325 --head-sha dfe6b0f07f9a29b1ee60dd1bcf985af4c4f53639 --merge-method merge --delete-branch` passed; controlled merge wrapper delegated host merge and PR #1325 merged; `python3 .loom/bin/loom_flow.py reconciliation sync --target . --issue 1315 --pr 1325 --branch work/1315-generic-governance-intensity --apply` added post-merge evidence and closed #1315; `python3 .loom/bin/loom_flow.py closeout check --target . --issue 1315 --pr 1325 --branch work/1315-generic-governance-intensity --gate-profile closeout-contract` passed; issue closeout comment recorded at https://github.com/MC-and-his-Agents/Loom/issues/1315#issuecomment-4629547759; no-release evidence is recorded in PR #1325 and the issue closeout comment.
- Recovery Boundary: This Work Item only owns #1315 generic governance methodology docs, landing links, and WI-1315 readiness carriers. Do not implement Loom gate behavior, CLI metadata, fixtures, generated skills, runtime behavior, release behavior, or AGENTS.md rules here.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: local docs review, `git diff --check`, Loom-specific term scan, suite validate not_applicable, PR #1325 hosted checks, controlled merge readback, reconciliation sync, and closeout check
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1315.md
- Dynamic Truth: .loom/progress/WI-1315.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
