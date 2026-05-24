# Loom CLI Command Matrix

The `loom` CLI is the primary control plane for the CLI-first operating layer. The current matrix is exposed mechanically through:

```bash
python3 tools/loom.py help --json
```

The JSON output is the canonical machine-readable matrix for tests and downstream consumers. This document freezes the naming rules and command families for human review.

## Naming Rules

- Commands are verb-first where the domain is implicit: `loom detect`, `loom doctor`, `loom verify`.
- Domain commands use `<domain> <verb>`: `loom installed-state validate`, `loom host doctor`, `loom skills release-check`.
- Gate and checkpoint commands use the stable gate name as the subcommand: `loom gate merge`, `loom checkpoint admission`.
- Host-control commands keep the host object name: `loom issue inspect`, `loom pr gate`, `loom workspace check`.
- Scenario commands keep the skill-facing scenario names: `loom spec-review`, `loom merge-ready`, `loom handoff`.

## Core And Installation

| Command | Status | Contract |
| --- | --- | --- |
| `loom version` | implemented | Emits repository, skills, plugin, host-adapter, runtime, and package version context. |
| `loom help` | implemented | Emits the full command matrix and fail-closed rules. |
| `loom installed-state show` | implemented | Reads `loom-installed-state/v2` from the target repo. |
| `loom installed-state validate` | implemented | Validates schema, layers, graph, and version metadata. |
| `loom installed-state export` | implemented | Emits valid installed-state plus installation graph. |
| `loom detect` | implemented | Detects current, legacy, symlink, single-skill, plugin, and mixed installed surfaces. |
| `loom doctor` | implemented | Diagnoses installed-state and legacy surface readiness with fail-closed repair fallback. |
| `loom repair plan` | implemented | Emits a non-mutating repair plan for missing, invalid, or legacy installed surfaces. |
| `loom repair apply` | implemented | Fails closed until write ownership and rollback semantics are approved by a later Work Item. |

## Reserved Phase Commands

These names are frozen for #885. Until their Work Items implement them, invoking them returns `result=block`.

```text
loom install
loom upgrade-plan
loom upgrade
loom rollback
loom verify
loom profile status|upgrade-plan|upgrade
loom story
loom spec
loom plan
loom build
loom pre-review
loom closeout
loom handoff
loom retire
loom checkpoint admission|build|merge
loom gate pre-review|spec-review|review|pr|merge|closeout
loom workspace create|locate|check|retire
loom issue inspect|bind|reconcile
loom project status|reconcile
loom pr inspect|metadata-preflight|gate
loom merge check|run
loom reconcile
loom host list|doctor|install|verify|upgrade|remove
loom skills list|generate|sync|check|doctor|package|release-check
```

## Delegated Compatibility Commands

These commands currently route to existing wrappers and remain compatibility paths while the CLI-first execution layer is filled in:

```text
loom init
loom adopt
loom route
loom status
loom fact-chain
loom resume
loom spec-review
loom review
loom merge-ready
loom check
```

Delegated commands are allowed only when the wrapper is the existing authoritative implementation for that workflow. Missing wrappers fail closed.

## Verification

The command matrix is checked by:

```bash
python3 tools/check_cli_contract.py
```

This covers #899 and #901 by asserting that required names appear in `loom help --json`, version output is structured, and installed-state positive and negative fixtures behave consistently.

For #906-#909 it also checks:

- empty targets classify as `uninstalled`;
- legacy `.loom/bin` surfaces are detected but not trusted as installed-state;
- mixed `.agents/skills`, skills registry, and plugin manifests classify as mixed legacy surfaces;
- valid installed-state makes `doctor` pass and `repair plan` no-op;
- invalid graph edge endpoints fail closed;
- `repair apply` remains a structured blocking command until mutation semantics are approved.
