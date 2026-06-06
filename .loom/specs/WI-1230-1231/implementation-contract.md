# Implementation Contract

## Work Item

- Item: WI-1230-1231
- Execution Entry: `tools/loom.py carrier closeout-sync`

## Approved Spec

- Spec Path: `.loom/specs/WI-1230-1231/spec.md`
- Spec Review Entry: `.loom/reviews/WI-1230-1231.spec.json`

## Implementation Scope

- In Scope: optional `Terminal Closeout Metadata` parsing, explicit `carrier closeout-sync` dry-run/apply behavior, no-host-mutation contract, CLI contract coverage, generated runtime parity, and methodology docs for local retire / host closeout sync / carrier closeout sync boundaries.
- Out Of Scope: raw host issue/PR/Project mutation, controlled merge implementation changes, workspace deletion, repair/apply flows, release behavior, and unrelated closeout gate semantics.

## Validation Plan

- Automated Checks: `git diff --check`; `python3 tools/py_compile_clean.py ...`; runtime parity cmp; `python3 tools/loom.py skills check --target . --json`; `python3 tools/loom.py suite validate --target . --item WI-1230-1231 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1230-1231 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1230-1231 --json`; `python3 tools/check_cli_contract.py --surface aggregate`; hosted required checks.
- Manual Verification: confirm `carrier closeout-sync` dry-run reports `host_mutations: false`, empty `host_actions`, and no progress carrier mutation; confirm `--apply` writes only `.loom/progress/<item>.md` terminal metadata.

## Risks And Rollback

- Risks: generated runtime copies and demo bootstrap fixture must stay synchronized with shared runtime source.
- Rollback Boundary: revert the implementation PR; no host issue, PR, Project, branch, worktree, or release state is mutated by `carrier closeout-sync`.

## Host Binding

- Pull Request: #1338
- Reviewed Head: pending final review carrier refresh
