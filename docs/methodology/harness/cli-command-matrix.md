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

## Implemented Phase Commands

#893 implements the host-control command family:

```text
loom workspace create|locate|check|retire
loom issue inspect|bind|reconcile
loom project status|reconcile
loom pr inspect|metadata-preflight|gate
loom merge check|run
loom reconcile
```

These commands use JSON wrappers over existing harness control-plane readers. GitHub and git remain the host-owned truth sources; Loom only freezes the command names, output shape, fail-closed reasons, and fallback names.

#894 implements the host adapter command family:

```text
loom host list|doctor|install|verify|upgrade|remove
```

`host list` and `host doctor` are read-only. Adapter-managed mutations fail closed unless explicit `--apply` is present. Full-repo/native discovery remains operator-owned and is not mutated by the CLI.

#895 implements the generated SKILLS command family:

```text
loom skills list|generate|sync|check|doctor|package|release-check
```

`skills generate` and `skills sync` require `--apply`; check, doctor, package, and release-check are read-only.

#890 implements the adoption and governance profile command family:

```text
loom init
loom adopt verify
loom route
loom profile status|upgrade-plan|upgrade
```

`init`, `route`, and `adopt verify` are CLI-first wrappers over the existing initialization and adoption runtimes. `loom adopt verify` is the adoption contract verifier; bootstrap remains under `loom init bootstrap` to avoid mixing adoption verification with repository scaffolding.

`profile status`, `profile upgrade-plan`, and `profile upgrade` wrap the existing governance profile runtime. `profile upgrade` inherits the underlying dry-run-by-default semantics and does not promote validation-only parity into a blocking gate.

#891 implements the fact-chain, checkpoint, and gate command family:

```text
loom status
loom fact-chain
loom checkpoint admission|build|merge
loom gate pre-review|spec-review|review|pr|merge|closeout
```

`status` and `fact-chain` are derived reads over the existing Loom carriers. `checkpoint` commands consume the established checkpoint payloads. `gate merge` checks host merge readiness through controlled-merge check but does not execute a merge. `gate closeout` checks closeout state but does not sync or close host objects.

## Reserved Phase Commands

These names are frozen for #885. Until their Work Items implement them, invoking them returns `result=block`.

```text
loom install
loom upgrade-plan
loom upgrade
loom rollback
loom verify
loom story
loom spec
loom plan
loom build
loom pre-review
loom closeout
loom handoff
loom retire
```

## Delegated Compatibility Commands

These commands currently route to existing wrappers and remain compatibility paths while the CLI-first execution layer is filled in:

```text
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

For #929-#943 it also checks:

- host-control, host, and skills command names are implemented in `loom help --json`;
- `loom host list` emits `loom-host-orchestration/v1`;
- `loom host install` fails closed without `--apply`;
- `loom skills list` emits the generated registry and root entry;
- `loom skills generate` fails closed without `--apply`;
- `loom skills package` emits package metadata for generated skills.
