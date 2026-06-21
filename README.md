# Loom

Language: English | [中文版本](./README.zh-CN.md)

Loom is an agent-first project operating layer.

It gives coding agents a behavior-first execution path across adopt, resume, spec, plan, build checkpoints, review, merge-ready, handoff, and closeout. The goal is not to produce business code faster at any cost, but to keep work from stopping at "files changed" and to converge on a state where goals, behavior evidence, test evidence, review state, trunk truth, and host control plane all agree.

Spec-driven development is an execution discipline inside Loom, not a narrower replacement for Loom. For formal spec, new feature, high-risk, or cross-module work, Loom can internalize SDD patterns such as staged artifacts, template-constrained specs, implementation plans, task or breakdown carriers, and cross-artifact consistency analysis. Those patterns must still feed Loom's wider operating layer: Work Item admission, recovery, review, merge-ready, controlled merge, closeout, host binding, and evidence consumption.

## How It Works

Loom is now CLI-first. The `loom` command is the execution control plane: it diagnoses installed state, reads fact chains, runs verification, exposes upgrade and repair plans, and wraps scenario execution with structured fail-closed output.

`SKILLS` remain the agent-facing entrances, but users do not install them as a separate surface. The root `loom` CLI installs and verifies metadata-only repository adoption, and it installs/registers the Codex user-level Loom plugin from the global package. The published skills payload lives in the Codex user plugin, not in each target repository. `.loom/` remains the repository execution fact surface. The npm `loom-installer` package is a deprecated legacy artifact. It is not the current CLI, release line, or recommended installation path.

Agents can still start from `loom-init` when they need routing help. Once inside the work, the CLI is the stable machine interface:

```bash
loom doctor --target . --json
loom upgrade-plan --target . --json
loom verify --target . --json
loom skills release-check --json
```

The core execution model is:

1. `loom doctor` and `loom verify` answer whether the repository is consuming a valid Loom layer.
2. `loom upgrade-plan` and `loom repair plan` describe the next non-mutating action for current, legacy, or mixed installs.
3. Scenario skills route human and agent intent into CLI-backed flows such as story, spec, build, review, merge-ready, and closeout.
4. Work Item, spec, plan, build checkpoint, review, merge-ready, and closeout consume a dual evidence loop: behavior evidence describes the observable contract, and test evidence proves the implementation loop.
5. Formal spec paths can use SDD-style staged artifacts and consistency analysis, while light paths and non-implementation work can mark non-applicable pieces explicitly.
6. Runtime evidence, review records, merge checkpoints, and closeout checks keep repository state aligned with host control.

Idle closeout recovery has three separate layers:

1. `loom workspace retire` is local-only worksite cleanup evidence. It does not close GitHub issues, merge PRs, update Projects, or write versioned terminal carriers.
2. Host closeout sync belongs to GitHub/git host control, such as PR merge readback, issue/project reconciliation, and target-branch verification.
3. `loom carrier closeout-sync` is the repo carrier repair path for HotCP-style stale carriers: when the host says a Work Item is complete but `.loom/progress/**`, `.loom/status/current.md`, or `.loom/bootstrap/init-result.json` still point at an active item, the carrier sync writes terminal metadata and lets the fact-chain return `idle` / `no_active_item`.

On a second repository checkout or after a post-merge closeout, read the host truth first, then sync carriers:

```bash
loom workspace retire --target . --item WI-1236 --json
loom carrier closeout-sync --target . --item WI-1236 --dry-run --terminal-state closed_out --issue 1236 --pr 1516 --merge-commit <merge-sha> --target-branch main --closed-at <closed-at> --evidence-locator <pr-url>
loom carrier closeout-sync --target . --item WI-1236 --apply --terminal-state closed_out --issue 1236 --pr 1516 --merge-commit <merge-sha> --target-branch main --closed-at <closed-at> --evidence-locator <pr-url>
loom fact-chain --target . --json
```

The expected final readback for a completed item is `fact_chain.mode = idle` and `current_item_id = no_active_item`, with terminal metadata retained in `.loom/progress/<item>.md`.

## Output Modes

Loom command output is context-safe by default. Commands emit direct JSON only
when it fits the effective stdout budget. Larger diagnostics are summarized on
stdout with an artifact locator, so agents and handoff notes can cite the
locator instead of pasting full reports or long logs.

Use the three output modes this way:

- Default `--json`: use for normal agent workflows, reviews, gates, handoff, and
  closeout. Share the summary and artifact locator.
- Artifact locator: use when diagnostics exceed the budget or when another
  thread needs the complete local evidence. Artifacts are diagnostic files, not
  authored truth carriers.
- Explicit `--full-output`: use only for debugging, audit, or blocker
  classification when complete JSON is required on stdout.

The default stdout hard budget is 16 KiB and the summary target is 4 KiB. They
can be adjusted per process with `LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES`,
`LOOM_AGENT_SAFE_SUMMARY_TARGET_BYTES`, and `LOOM_OUTPUT_ARTIFACT_DIR`.

## Install

### Root CLI

Install the root Loom CLI:

```bash
npm install -g @mc-and-his-agents/loom
```

Use the pure global install model:

- the workstation has the global `loom` CLI;
- Codex has a user-level Loom plugin installed and registered from that global
  package;
- each adopted repository records metadata-only Loom adoption and keeps no
  repo-local Loom runtime, plugin payload, or generated skills payload.

See [docs/adoption/unified-install-experience.md](./docs/adoption/unified-install-experience.md),
[docs/adoption/installation-taxonomy.md](./docs/adoption/installation-taxonomy.md),
and [docs/adoption/loom-installed-state-v2.md](./docs/adoption/loom-installed-state-v2.md)
for the detailed adoption contracts and validation commands.

Install the Codex user-level plugin and adopt a target repository:

```bash
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom install --target . --apply --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

`loom host install` and `loom host register` mutate only Codex user workstation
state. `loom install` writes repository adoption metadata and the Loom bootstrap
block. `loom host verify` verifies both the metadata-only repository boundary
and the Codex user-level plugin provider registration.

When a repository still carries repo-local wrappers or vendored runtime residue
such as `.loom/bin`, `.loom/bootstrap`, `plugins/loom`, `.agents/skills`, or
Loom-owned root `skills`, current verification blocks until that legacy residue
is explicitly migrated or removed.

On a second development machine for an already adopted repository, install and
register the Codex user-level plugin from the global Loom package:

```bash
loom host verify --host codex --target . --json
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom doctor --target . --json
```

The registration command writes user workstation state such as the personal
Codex marketplace entry, user plugin cache payload, and Codex config enablement.
It does not write target repository truth. Start a new Codex session, or restart
Codex Desktop if the plugin list was already loaded; Loom does not claim that an
existing session hot-loads newly registered plugins.

See [docs/adoption/legacy-install-migration.md](./docs/adoption/legacy-install-migration.md)
for the explicit migration path from older repo-local installs.

Use `npx @mc-and-his-agents/loom ...` only as an ephemeral way to run the same root `loom` CLI.

Requirements:

- Node `>=20`
- Python `>=3.11`

`loom-installer` is not part of the primary install journey. It is retained only as deprecated historical evidence for legacy consumers.

### Advanced / Compatibility

The historical native skills-library clone path is not the primary install path for new users:

```bash
git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom
```

Use the root `loom` CLI instead. Any existing skills-library clone should be treated as a compatibility source that the CLI can verify, repair, or replace; users should not install SKILLS or plugins as independent surfaces.

## Release Surfaces

The Loom CLI release surface is the only active release line for execution behavior. Its authority is root `VERSION` plus the GitHub `v*` tag and Release state. The `loom-installer deprecated legacy line` remains separate only as historical npm/tag evidence and must not advance as a normal release path.

Do not use npm `@mc-and-his-agents/loom-installer` `latest` or `loom-installer-v*` tags as evidence that the `loom` CLI was published. The final legacy baseline is `loom-installer-v0.1.119` / npm `0.1.119` unless a later deprecation action changes only npm metadata. See [docs/adoption/loom-cli-release-surface.md](./docs/adoption/loom-cli-release-surface.md) and [docs/adoption/version-authority-map.md](./docs/adoption/version-authority-map.md).

## Basic Workflow

1. Run `loom doctor --target . --json` or `loom verify --target . --json` to understand the repository's current Loom layer.
2. Run `loom upgrade-plan --target . --json` before changing metadata-only adoption, global CLI provider state, Codex user-level plugin registration, or legacy residue repair.
3. Start from `loom-init` when you need scenario routing, then use scenario skills such as `loom-adopt`, `loom-resume`, `loom-build`, `loom-review`, and `loom-merge-ready`.
4. Use CLI-backed gates such as `loom pr gate`, `loom merge check`, `loom merge run`, and `loom gate closeout` to consume readiness evidence.
5. Use `loom-handoff` or `loom-retire` to leave the worksite in a recoverable local state, then use host closeout readback and `loom carrier closeout-sync` for versioned terminal carrier sync when the issue/PR/project are already complete.

The standard controlled merge path is `loom pr gate <pr> --head-sha <sha> --work-item <WI> --json`, then `loom merge check <pr> --head-sha <sha> --work-item <WI> --json`, then `loom merge run <pr> --head-sha <sha> --work-item <WI> --apply --json`. Required CI, optional triggered checks, and host branch protection are consumed by this path, but they do not replace the authored Loom semantic review record bound to the same PR head.

Agents should not treat "there are changed files" as completion. In Loom, work is only done when goals, documents, review state, validation evidence, trunk truth, and host control plane all agree.

## Skills Library

Loom exposes one root entry and ten scenario skills:

| Skill | Role |
| --- | --- |
| `loom-init` | Root entry; initializes or routes to the correct scene. |
| `loom-adopt` | Creates the minimum Loom adoption surface for a repository. |
| `loom-resume` | Restores context and continues the current `Work Item`. |
| `loom-build` | Runs a bounded implementation/build round before review. |
| `loom-story` | Turns product context into a User Story, Story Readiness, and business semantic confirmation point. |
| `loom-pre-review` | Checks readiness before formal review. |
| `loom-spec-review` | Reviews the formal spec path and produces the `spec-approved` gate. |
| `loom-review` | Runs formal review and records the result. |
| `loom-handoff` | Writes a recoverable handoff point. |
| `loom-merge-ready` | Validates merge readiness. |
| `loom-retire` | Cleans up and exits without discarding user changes. |

The editable skills source lives under `src/skills/`. The Loom source
repository's generated and checked-in payload surface lives under
[skills/](./skills/) as a source mirror. The published skills payload is the
Codex user plugin payload under `plugins/loom/skills/`; `skills/<skill-id>` is
not a self-contained single-skill package and does not carry
`loom-package.json` or `.loom-runtime/` as distribution artifacts. Downstream
top-level `skills/` belongs to the target repository namespace unless an
explicit future profile owns it. The canonical Codex plugin manifest lives under
[plugins/loom/.codex-plugin/](./plugins/loom/.codex-plugin/) and is installed
or verified through `loom host ...`.

## Maintainer Docs

- Vision and boundary: [VISION.md](./VISION.md)
- Repository constitution: [AGENTS.md](./AGENTS.md)
- Change governance intensity: [docs/methodology/governance/change-governance-intensity.md](./docs/methodology/governance/change-governance-intensity.md)
- Loom governance intensity mapping: [docs/methodology/governance/loom-governance-intensity-mapping.md](./docs/methodology/governance/loom-governance-intensity-mapping.md)
- Governance intensity closeout evidence: [docs/evidence/governance-intensity-final-closeout.md](./docs/evidence/governance-intensity-final-closeout.md)
- Skills surface: [skills/README.md](./skills/README.md)
- Methodology docs: [docs/methodology/](./docs/methodology/)
- Architecture docs: [docs/architecture/](./docs/architecture/)
- Adoption contracts: [docs/adoption/](./docs/adoption/)
- Unified install experience: [docs/adoption/unified-install-experience.md](./docs/adoption/unified-install-experience.md)
- Host adapter matrix: `docs/adoption/host-adapter-matrix.md`
- Version authority map: [docs/adoption/version-authority-map.md](./docs/adoption/version-authority-map.md)
- Evidence ledger: [docs/evidence/](./docs/evidence/)
- Distribution contract: [skills/distribution-and-adapter-contract.md](./skills/distribution-and-adapter-contract.md)

## Philosophy

Loom is merge-readiness-centered and behavior-first. Review, validation, host state, behavior evidence, test evidence, and closeout are separate surfaces, but they must converge. If any one of them is still open, the work should not be treated as finished.

Loom is not a business template, a code generator, an SDD-only tool, or a replacement for GitHub, CI, review engines, or `git worktree`. It is a project operating layer with executable skills so agents can consume those host capabilities consistently.
