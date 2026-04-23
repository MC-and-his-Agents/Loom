# Loom

Loom is a skills-first methodology repository for agent coding workflows.

It gives coding agents a governed path from adoption to resume, review, merge-ready, handoff, and closeout. The point is not to generate business code faster; the point is to stop agent work from ending at “code changed” and drive it to merge-ready and closed.

## How It Works

Loom installs as a complete skills library. Agents start from `loom-init`, then route into the right scenario skill based on the current task and repository state.

The basic flow is:

1. `loom-init` decides whether the agent should adopt, resume, review, hand off, retire, or check merge readiness.
2. Scenario skills execute the concrete workflow and consume the shared Loom runtime contracts.
3. Methodology docs stay behind the skills layer, so users do not need to browse governance internals before using Loom.
4. Runtime evidence, review records, merge checkpoints, and closeout checks keep the repository state consistent.

## Install

### Codex Native Skill Discovery

Tell Codex:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/MC-and-his-Agents/Loom/refs/heads/main/.codex/INSTALL.md
```

Manual install:

```bash
git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom
mkdir -p ~/.agents/skills
ln -s ~/.codex/loom/skills ~/.agents/skills/loom
```

Restart Codex after installing so native skill discovery can load the Loom skills.

### npm Installer

If you want an installer to wire the plugin into a target repository, use:

```bash
npx @mc-and-his-agents/loom-installer add plugin --host codex
npx @mc-and-his-agents/loom-installer add plugin --host claude
```

Or pin the installer first:

```bash
npm install -D @mc-and-his-agents/loom-installer
npx loom-installer add plugin --host codex
npx loom-installer add plugin --host claude
```

Requirements:

- Node `>=20`
- Python `>=3.10`, recommended `3.11+`

The installer handles installation, discovery, and verification. Loom execution still runs through the Python runtime shipped with the skills library.

## Basic Workflow

1. Start with `loom-init` when you are unsure what should happen next.
2. Use `loom-adopt` to initialize a new repository or retrofit Loom into an existing one.
3. Use `loom-resume` to recover context and continue a work item.
4. Use `loom-pre-review` before formal review to catch obvious readiness gaps.
5. Use `loom-review` to produce a structured review result.
6. Use `loom-merge-ready` before merge to verify the release boundary.
7. Use `loom-handoff` or `loom-retire` to leave the worksite in a recoverable or closed state.

The agent should not treat “changed files exist” as completion. Loom completion means the goal, docs, review state, validation evidence, main-branch truth, and host control plane are aligned.

## Skills Library

Loom currently exposes one root entry and seven scenario skills:

| Skill | Purpose |
| --- | --- |
| `loom-init` | Root entry; initializes or routes to the right scenario. |
| `loom-adopt` | Creates the minimal Loom adoption surface for a repository. |
| `loom-resume` | Restores context and continues a work item. |
| `loom-pre-review` | Checks readiness before formal review. |
| `loom-review` | Runs formal review and records the result. |
| `loom-handoff` | Writes a recoverable handoff point. |
| `loom-merge-ready` | Verifies merge readiness. |
| `loom-retire` | Cleans up and retires a worksite without discarding user changes. |

The canonical skills library is [skills/](./skills/). Generated plugin and single-skill payloads are not committed; release tooling builds them from the canonical root `.codex-plugin/` and `skills/` sources.

## Advanced / Compatibility

Single-skill installation remains available for compatibility and advanced use, but it is not the primary Loom experience:

```bash
npx @mc-and-his-agents/loom-installer add skill loom-retire --host codex
npx @mc-and-his-agents/loom-installer add skill loom-retire --host claude
```

A single installed skill exposes only that named skill to the host. If you need routing through `loom-init` and the full scenario surface, install the complete Loom plugin or skills library.

## Maintainer Docs

- Vision and boundaries: [VISION.md](./VISION.md)
- Repository constitution: [AGENTS.md](./AGENTS.md)
- Skills surface: [skills/README.md](./skills/README.md)
- Methodology: [docs/methodology/](./docs/methodology/)
- Architecture notes: [docs/architecture/](./docs/architecture/)
- Adoption contracts: [docs/adoption/](./docs/adoption/)
- Evidence ledger: [docs/evidence/](./docs/evidence/)
- Distribution contract: [skills/distribution-and-adapter-contract.md](./skills/distribution-and-adapter-contract.md)

## Philosophy

Loom is merge-readiness-centered. Review, validation, host state, and closeout are separate surfaces that must converge before work is complete.

Loom is not a business template, a code generator, or a replacement for GitHub, CI, review engines, or `git worktree`. It is the methodology and executable skills layer that lets agents consume those host capabilities consistently.
