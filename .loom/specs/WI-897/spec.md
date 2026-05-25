# WI-897 Spec

## Goal

Validate WebEnvoy, Syvert, and HotCP legacy Loom installation surfaces against
the CLI-first migration command surface for #885.

## Acceptance

- WebEnvoy, Syvert, and HotCP legacy repository shapes are represented as
  versioned fixtures.
- `tools/check_cli_contract.py` mechanically verifies each fixture with
  `detect`, `doctor`, `repair plan`, `upgrade-plan`, and `verify`.
- Legacy and mixed-legacy repositories fail closed before mutating repair,
  upgrade, install, or rollback actions.
- The migration playbook records the operator sequence and keeps repo-owned
  authority in each adopted repository.
- The validation record states the #897 release judgment and hands final publish
  or no-publish authority to #996.

## Non-Goals

- Do not mutate WebEnvoy, Syvert, or HotCP.
- Do not publish a Loom root release, GitHub tag, or npm package in #897.
- Do not replace repo-specific guardian, hook, live evidence, or controlled
  merge systems.
- Do not broaden into profile finalization or bottom-layer GitHub/CI/review
  rewrites outside #885.
