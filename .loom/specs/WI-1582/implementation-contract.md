# WI-1582 Implementation Contract

- Suite path: minimal

## Contract Surface

- Hosted freeze admission preserves `surface=closeout` when consuming closeout PR metadata.
- Terminal closeout review freshness is surface-aware only for `surface=closeout` with a terminal checkpoint.
- `carrier refresh --surface closeout` emits closeout-surface carrier refresh evidence.
- Hosted `gate-freeze check --surface closeout` is accepted and emits closeout snapshot evidence.
- Merge-ready and current-head review gates remain strict and cannot consume terminal closeout retained review.
- Generated skill runtime copies and demo bootstrap runtime copies stay in parity with the source runtime.

## Consumer Boundary

- #1580 closeout-only carrier sync, hosted gate admission, PR gate, implementation review, and milestone/12 closeout may consume this contract only as the terminal closeout admission repair.
- #1554, #1555, and #1533 retain their broader wrapper, one-shot closeout, and closeout-specific gate responsibilities.

## Non-Goals

- Do not mutate #1580 carrier content.
- Do not reopen WI-1512 or bind WI-1582 to WI-1578.
- Do not change release/no-release judgment, controlled merge semantics, or broad wrapper/runtime argument contracts.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- targeted terminal closeout hosted fixture via `assert_terminal_closeout_pr_gate_fixture(Path(tmp))`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `make loom-demo-new-project-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
- `git diff --check`
