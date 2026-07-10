# Milestone 13 Convergence Validation

## Scope

WI-1598 consumes the stable milestone 13 front-lane outputs for docs, skills protocol, targeted fixtures, generated runtime parity, and downstream release closeout inputs.

It does not implement host auth, PR metadata, release resume, closeout role, dependency parser, AGENTS governance behavior, or v0.15.0 release closeout.

## Consumed Inputs

- #1595 / PR #1603: PR metadata preflight and drift diagnostics.
- #1597 / PR #1607: host API auth/readback classifier and token bridge.
- #1599 / PR #1605: closeout PR role model.
- #1600 / PR #1604: native dependency / structured machine-block dependency parsing boundary.
- #1601 / PR #1606: release readback and resume classifier.
- #1318 / PR #1602: AGENTS classify-before-execute governance principle.

## Convergence Evidence

- `docs/methodology/templates/pull-request.md` documents PR metadata machine carrier expectations.
- `docs/adoption/host-adapter-matrix.md` documents host auth/readback classifier behavior and token bridge next action.
- `docs/methodology/harness/closeout-gate.md` documents closeout PR role consumption.
- `docs/methodology/harness/native-dependency-contract.md` documents native dependency and structured machine-block boundaries.
- `docs/adoption/loom-cli-release-surface.md` documents non-mutating release readback/resume and release/no-release evidence boundaries.
- `docs/evidence/fixtures/release-readback-fixtures.json` covers release readback/resume fixture stories.
- `skills/shared/scripts/loom_flow.py`, `src/skills/shared/scripts/loom_flow.py`, `examples/new-project/.loom/bin/loom_flow.py`, and generated skill runtime copies carry the same shared closeout/dependency/PR metadata surfaces.

## Validation Commands

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py workspace audit --target . --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1598 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1598 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface release-readback`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py --surface release-doc-contract`
- `git diff --check`
