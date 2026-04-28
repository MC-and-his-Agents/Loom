# Loom Self-Governance Companion

This companion declares the repository-owned boundary for Loom managing its own product iteration.

## Managed Scope

- Loom core and product iteration are self-managed through the root `.loom` carrier.
- The next managed productization phase is GitHub issue #410: `Phase: Agent-assisted zero-friction adoption`.
- Work under #410 must enter execution through Loom Work Items, review records, gate checks, and closeout evidence.

## Boundary

- Downstream repositories such as Syvert and WebEnvoy remain adoption fixtures and evidence sources, not root truth for Loom.
- Repo-specific downstream policies must stay in each downstream repo companion or residue layer.
- This companion does not make all Loom signals blocking by default; advisory-to-blocking remains explicit and evidence-based.

## Evidence

- Self-governance adoption validation: `docs/evidence/validations/validation-loom-self-governance-adoption.md`
- Root carrier status: `.loom/status/current.md`
- Root validation entry: `python3 .loom/bin/loom_init.py verify --target .`
