# WI-1534 Implementation Contract

- Suite path: minimal

## Contract Surface

- `docs/methodology/harness/closeout-gate.md` defines the canonical closeout modes: `inline`, `auto_no_op`, `light`, `batched`, and `full`.
- `docs/methodology/harness/cli-command-matrix.md` maps queue/status diagnostics `auto_no_op`, `light_carrier_sync`, `batched_closeout`, `full_closeout`, and `blocked` back to canonical modes.
- `skills/loom-merge-ready/SKILL.md` consumes `loom-closeout-specific-gate/v1` as closeout admission only; `closeout_pr_allowed=true` is not implementation approval.
- `skills/loom-pre-review/SKILL.md` routes closeout-only carrier PRs to closeout admission or full review / guardian escalation based on mode and gate flags.
- `skills/loom-retire/SKILL.md` keeps local cleanup separate from host/repo carrier closeout and does not choose closeout mode.
- `tools/check_cli_contract.py --surface governance-closeout` asserts the docs, shared references, skill text, and queue/status mapping stay in sync.

## Consumer Boundary

- #1515 may consume this contract as closeout mode docs/skills/fixture evidence after #1534 merges.
- Merge-ready and pre-review skills may use it to route closeout-only PRs without treating closeout admission as implementation approval.
- Retire flow may use it to refuse replacing `carrier closeout-sync`, `reconciliation sync`, `closeout check`, or closeout-only PR evidence.

## Non-Goals

- Do not implement runtime closeout behavior, host mutation, batch execution, release/no-release judgment, issue closure, PR merge, or Project mutation.
- Do not redefine #1513 classifier authority, #1533 closeout-specific gate schema, #1555 one-shot closeout run, or #1515 final milestone closeout.
- Do not make skills or docs a new truth source; Work Item, review, PR metadata, host/git/carrier readback, and closeout evidence remain authoritative.

## Validation Binding

- `git diff --check`
- `python3 tools/check_cli_contract.py --surface pr-metadata`
- `python3 tools/check_cli_contract.py --surface closeout-wrapper`
- `python3 tools/check_cli_contract.py --surface governance-closeout`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/loom.py suite validate --target . --item WI-1534 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1534 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1534 --json`
- `python3 tools/loom.py fact-chain --target . --item WI-1534 --json`
- `python3 src/skills/shared/scripts/loom_flow.py shadow-parity --target . --surface all --blocking`
- `python3 src/skills/shared/scripts/loom_flow.py work-item-audit --target .`
- `python3 tools/py_compile_clean.py tools/check_cli_contract.py`
