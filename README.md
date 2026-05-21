# Loom

Language: English | [中文版本](./README.zh-CN.md)

Loom is an agent-first project operating layer.

It gives coding agents a behavior-first execution path across adopt, resume, spec, plan, build checkpoints, review, merge-ready, handoff, and closeout. The goal is not to produce business code faster at any cost, but to keep work from stopping at "files changed" and to converge on a state where goals, behavior evidence, test evidence, review state, trunk truth, and host control plane all agree.

## How It Works

Loom remains a full-repo / plugin / SKILLS / CLI product. The default install model is full repository install plus native or host skill discovery. `SKILLS` expose scenario operations; host adapters expose install and bootstrap wiring; the CLI and fixtures provide machine checks; docs remain the repository truth for methodology, harness, adoption, templates, and evidence.

Agents start from `loom-init`, then route into the right scenario skill based on the task and repository state.

The core execution model is:

1. `loom-init` decides whether the current work should adopt, resume, review, hand off, retire, or validate merge readiness.
2. Scenario skills run the concrete workflow and consume the shared Loom runtime contract.
3. Work Item, spec, plan, build checkpoint, review, merge-ready, and closeout consume a dual evidence loop: behavior evidence describes the observable contract, and test evidence proves the implementation loop.
4. Methodology and architecture documents stay behind the skills layer, so users do not need to study Loom internals before starting.
5. Runtime evidence, review records, merge checkpoints, and closeout checks keep repository state aligned.

## Install

### Codex Native Skill Discovery

You can tell Codex:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/MC-and-his-Agents/Loom/refs/heads/main/docs/adoption/codex-install.md
```

Or install Loom manually:

```bash
git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom
mkdir -p ~/.agents/skills
for skill in ~/.codex/loom/skills/loom-*; do
  ln -sfn "$skill" "$HOME/.agents/skills/$(basename "$skill")"
done
```

Restart Codex after installation so native skill discovery reloads the Loom skills.

### Adapter Installer

The npm installer is not the Codex default path. Use it when you need an adapter-managed plugin install, single-skill helper flow, or installer verification output:

```bash
npx @mc-and-his-agents/loom-installer add plugin --host codex
npx @mc-and-his-agents/loom-installer add plugin --host claude
```

You can also pin the installer first:

```bash
npm install -D @mc-and-his-agents/loom-installer
npx loom-installer add plugin --host codex
npx loom-installer add plugin --host claude
```

Requirements:

- Node `>=20`
- Python `>=3.10`, recommended `3.11+`

The installer reports the distribution layer and version context it touched. Loom execution still runs on the Python runtime bundled with the generated skills surface.

## Basic Workflow

1. Start from `loom-init` when you are unsure what should happen next.
2. Use `loom-adopt` to initialize a new repository or retrofit Loom into an existing one.
3. Use `loom-resume` to restore context and continue the current `Work Item`.
4. Use `loom-pre-review` to expose obvious readiness gaps before formal review.
5. When the task hits the formal spec path, use `loom-spec-review` first to produce the `spec-approved` gate.
6. Use `loom-review` to produce a structured review result.
7. Use `loom-merge-ready` to validate the release boundary before merge.
8. Use `loom-handoff` or `loom-retire` to leave the worksite in a recoverable or closed state.

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

The editable skills source lives under `src/skills/`. The generated and checked-in install surface lives under [skills/](./skills/). Each `skills/<skill-id>` directory is a self-contained single-skill package with `loom-package.json` and `.loom-runtime/`. The canonical Codex plugin manifest lives under [plugins/loom/.codex-plugin/](./plugins/loom/.codex-plugin/).

## Advanced / Compatibility

Single-skill installation remains available as an advanced compatibility path, but it is no longer the default Loom journey:

```bash
npx @mc-and-his-agents/loom-installer add skill loom-retire --host codex
npx @mc-and-his-agents/loom-installer add skill loom-retire --host claude
```

An individually installed skill only exposes that skill to the host. If you need `loom-init` routing and the full scenario surface, install the full repository and complete generated skills surface.

## Maintainer Docs

- Vision and boundary: [VISION.md](./VISION.md)
- Repository constitution: [AGENTS.md](./AGENTS.md)
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

Loom is not a business template, a code generator, or a replacement for GitHub, CI, review engines, or `git worktree`. It is a project operating layer with executable skills so agents can consume those host capabilities consistently.
