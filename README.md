# Loom

Language: English | [中文版本](./README.zh-CN.md)

Loom is an agent-first project operating layer.

It gives coding agents a behavior-first execution path across adopt, resume, spec, plan, build checkpoints, review, merge-ready, handoff, and closeout. The goal is not to produce business code faster at any cost, but to keep work from stopping at "files changed" and to converge on a state where goals, behavior evidence, test evidence, review state, trunk truth, and host control plane all agree.

Spec-driven development is an execution discipline inside Loom, not a narrower replacement for Loom. For formal spec, new feature, high-risk, or cross-module work, Loom can internalize SDD patterns such as staged artifacts, template-constrained specs, implementation plans, task or breakdown carriers, and cross-artifact consistency analysis. Those patterns must still feed Loom's wider operating layer: Work Item admission, recovery, review, merge-ready, controlled merge, closeout, host binding, and evidence consumption.

## How It Works

Loom is now CLI-first. The `loom` command is the execution control plane: it diagnoses installed state, reads fact chains, runs verification, exposes upgrade and repair plans, and wraps scenario execution with structured fail-closed output.

`SKILLS` remain the agent-facing entrances, but users do not install them as a separate surface. The root `loom` CLI installs, synchronizes, and verifies the generated skills and host plugin payloads. Plugins and host adapters provide native discovery and wiring under CLI management. `.loom/` remains the repository execution fact surface. The npm `loom-installer` package is a deprecated legacy artifact. It is not the current CLI, release line, or recommended installation path.

Agents can still start from `loom-init` when they need routing help. Once inside the work, the CLI is the stable machine interface:

```bash
python3 tools/loom.py doctor --target . --json
python3 tools/loom.py upgrade-plan --target . --json
python3 tools/loom.py verify --target . --json
python3 tools/loom.py skills release-check --json
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
python3 tools/loom.py workspace retire --target . --item WI-1236 --json
python3 .loom/bin/loom_flow.py carrier closeout-sync --target . --item WI-1236 --dry-run --terminal-state closed_out --issue 1236 --pr 1516 --merge-commit <merge-sha> --target-branch main --closed-at <closed-at> --evidence-locator <pr-url>
python3 .loom/bin/loom_flow.py carrier closeout-sync --target . --item WI-1236 --apply --terminal-state closed_out --issue 1236 --pr 1516 --merge-commit <merge-sha> --target-branch main --closed-at <closed-at> --evidence-locator <pr-url>
python3 tools/loom.py fact-chain --target . --json
```

The expected final readback for a completed item is `fact_chain.mode = idle` and `current_item_id = no_active_item`, with terminal metadata retained in `.loom/progress/<item>.md`.

## Install

### Root CLI

Install the root Loom CLI:

```bash
npm install -g @mc-and-his-agents/loom
```

Choose the repository runtime provider mode explicitly:

- `global-cli`: the repository records Loom adoption metadata and depends on
  the installed root `loom` command as the runtime provider. No `.loom/bin`
  runtime carrier is expected in this mode; workstation/global CLI availability
  is diagnosed separately from repository truth.
- `repo-local-wrapper`: the repository intentionally keeps repo-local wrapper
  carriers such as `.loom/bin`. Those carriers remain valid when installed-state
  declares them, including compatibility windows where the wrapper delegates to
  the global CLI provider.

See [docs/adoption/unified-install-experience.md](./docs/adoption/unified-install-experience.md),
[docs/adoption/installation-taxonomy.md](./docs/adoption/installation-taxonomy.md),
and [docs/adoption/loom-installed-state-v2.md](./docs/adoption/loom-installed-state-v2.md)
for the detailed adoption contracts and validation commands.

Install and verify the Codex host payload for a target repository:

```bash
loom host install --host codex --mode plugin --target . --apply --json
loom host verify --host codex --mode plugin --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

`loom host install` and `loom host verify` manage and verify the target
repository plugin payload: `.loom/installed-state.json`,
`plugins/loom/.codex-plugin/plugin.json`, and the embedded
`plugins/loom/skills/` skills payload. They do not write or require downstream
top-level `skills/` in plugin mode, and they do not prove that Codex Desktop on
the current workstation has registered, enabled, or loaded the plugin.

When a repository still carries repo-local wrappers or vendored runtime residue
such as `.loom/bin`, treat those surfaces as repository/runtime-carrier facts,
not as automatic proof of the active provider. The active provider may instead
be the global `loom` CLI runtime or a workstation/user-level skills provider,
and Loom diagnostics must keep those boundaries explicit.

On a second development machine for an already adopted repository, register the
repo-local plugin payload with the local Codex Desktop workstation explicitly:

```bash
loom host verify --host codex --mode plugin --target . --json
loom host register --host codex --source ./plugins/loom --scope user --dry-run --json
loom host register --host codex --source ./plugins/loom --scope user --apply --json
loom doctor --target . --json
```

The registration command writes user workstation state such as the personal
Codex marketplace entry, user plugin cache payload, and Codex config enablement.
It does not write target repository truth. Start a new Codex session, or restart
Codex Desktop if the plugin list was already loaded; Loom does not claim that an
existing session hot-loads newly registered plugins.

This means compatibility mode stays diagnosable: repo-local wrapper residue,
global CLI runtime availability, and workstation registration are separate
states, even when the same adopted repository depends on all three during a
migration window.

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
2. Run `loom upgrade-plan --target . --json` before changing installed runtime, skills, plugin, or companion surfaces.
3. Start from `loom-init` when you need scenario routing, then use scenario skills such as `loom-adopt`, `loom-resume`, `loom-build`, `loom-review`, and `loom-merge-ready`.
4. Use CLI-backed gates such as `loom checkpoint merge`, `loom gate pr`, and `loom gate closeout` to consume readiness evidence.
5. Use `loom-handoff` or `loom-retire` to leave the worksite in a recoverable local state, then use host closeout readback and `loom carrier closeout-sync` for versioned terminal carrier sync when the issue/PR/project are already complete.

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
[skills/](./skills/). Each `skills/<skill-id>` directory is a self-contained
skill payload with `loom-package.json` and `.loom-runtime/`, managed by the root
CLI. Downstream Codex plugin installs embed that payload under
`plugins/loom/skills/`; downstream top-level `skills/` belongs to the target
repository namespace unless an explicit future profile owns it. The canonical
Codex plugin manifest lives under
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
