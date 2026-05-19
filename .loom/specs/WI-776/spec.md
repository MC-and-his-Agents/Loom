# WI-776 Spec

## Goal

Loom adoption must identify docs-first existing repositories before execution surfaces exist, without treating them as mature complex-existing repos or defaulting them to heavy generation.

## Acceptance

- A repository with `AGENTS.md`, `README.md`, `VISION.md`, and `docs/**`, but no code, CI, tests, or validation entry, reports `run.scenario_key = pre-execution-existing`.
- The same dry-run reports structured maturity for document truth, execution surface, and governance carriers.
- Default adoption for the classification does not choose `full-bootstrap` or an execution-control scaffold profile.
- Explicit `--intent execution-control` can still select `full-bootstrap`, proving classification does not directly determine generation strength.
- Product or domain docs named `CONTRACT_MODEL.md` or `DOMAIN_MODEL.md` do not imply shared runtime contract or governance-module risk.
