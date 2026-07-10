# WI-1512 Implementation Contract

- Suite path: minimal

## Contract Surface

- Runtime `pr-gate check` accepts hosted admission inputs:
  - `--body-file`
  - `--compare-body-file`
  - `--gate-freeze-snapshot-file`
- `tools/loom.py pr gate` forwards those hosted admission inputs to the shared runtime.
- Hosted admission emits `loom-hosted-freeze-admission/v1`.
- Hosted admission recomputes `loom-gate-freeze/v1` inputs from the current checkout, PR payload, PR body readback, carrier refresh, shadow freshness, review binding, and PR metadata.
- Hosted admission blocks PR body drift and retained freeze snapshot mismatch without weakening fact-chain, review, PR metadata, or merge checkpoint enforcement.
- `.github/workflows/pr-merge-gate.yml` reads PR body/payload from GitHub and passes them into `pr-gate check`.

## Consumer Boundary

- #1512 consumers may rely on this contract for hosted PR gate freeze admission only.
- #1532/#1533 may consume the merged behavior as a prerequisite for closeout freeze/gate work, but they own closeout-specific profile semantics.
- #1514/#1534/#1515 must read back PR #1572 and #1512 closeout evidence before treating this item as complete.

## Non-Goals

- Do not define `loom-closeout-freeze/v1`.
- Do not implement a closeout-specific gate.
- Do not implement #1555 one-shot post-merge closeout run.
- Do not change release/no-release behavior.
- Do not bypass current Work Item, review, PR metadata, suite, or merge checkpoint gates.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py skills/loom-adopt/.loom-runtime/shared/scripts/loom_flow.py skills/loom-build/.loom-runtime/shared/scripts/loom_flow.py skills/loom-handoff/.loom-runtime/shared/scripts/loom_flow.py skills/loom-init/.loom-runtime/shared/scripts/loom_flow.py skills/loom-merge-ready/.loom-runtime/shared/scripts/loom_flow.py skills/loom-pre-review/.loom-runtime/shared/scripts/loom_flow.py skills/loom-resume/.loom-runtime/shared/scripts/loom_flow.py skills/loom-retire/.loom-runtime/shared/scripts/loom_flow.py skills/loom-review/.loom-runtime/shared/scripts/loom_flow.py skills/loom-spec-review/.loom-runtime/shared/scripts/loom_flow.py skills/loom-story/.loom-runtime/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `make loom-demo-new-project-check`
- `python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1512`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1512 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1512 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1512 --json`
- `git diff --check`
