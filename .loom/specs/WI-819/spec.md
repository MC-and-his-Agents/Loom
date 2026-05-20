# WI-819 Spec

## Objective

Freeze the shared governance foundation for #819/#821/#845/#853/#854 without turning any repo-specific rule into Loom core.

## Required Outcomes

- #819 has one default governance scaffold policy truth source under `docs/methodology/templates/`.
- #821 has one Project / Phase / FR / Work Item goal schema truth source under `docs/methodology/governance/`.
- #845 has one Governance Lint taxonomy truth source under `docs/methodology/harness/`.
- #853 separates versioned closeout truth from post-merge local workspace retire evidence.
- #854 reports structured active workspace diagnostics and distinguishes stale carriers from true shared workspace conflicts.

## Non-Goals

- Do not add repo-specific review rules to Loom core.
- Do not create a second truth source in skills references or generated runtime surfaces.
- Do not replace GitHub, CI, review engine, or worktree host controls.

## Acceptance

- Source docs, generated skills surfaces, `.loom/bin`, and bootstrap runtime hashes are aligned.
- Local py_compile, surface checks, smoke commands, and `python3 tools/loom_check.py` pass.
- PR #855 records validation evidence and is merge-ready unless host checks or permissions block merge.
