# Loom

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=for-the-badge&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/MC-and-his-Agents/Loom) [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/MC-and-his-Agents/Loom)

Language: English | [中文版本](./README.zh-CN.md)

Loom is an agent-first project operating layer: a structured execution framework
for coding agents. It gives agents a behavior-first path from adoption and
merge readiness through closeout.

Loom does not optimize for code generation speed by itself. It makes work
converge on a stronger final state: goals, documents, review state, validation
evidence, trunk truth, and the host control plane all agree. It is CLI-first,
keeps only metadata at repository boundaries, and is built around five
cooperating planes: governance truth, harness orchestration, behavior and test
evidence, spec discipline, and executable skills.

## What Loom Solves

When humans and agents can both generate code quickly, the bottleneck moves from
code generation to continuous, orderly execution. Loom does not reuse business
code. It reuses the operating structure for organizing a project, entering
execution, progressing across multiple rounds, reaching merge readiness, and
closing work out.

New projects no longer need to begin as an empty repository plus temporary
conventions and scattered context. They can begin with a sustainable,
verifiable, agent-operable runtime structure.

Loom does not decide what product to build, how to design product architecture,
how to model a business domain, or whether every project must use the same file
layout. It focuses on project operation, not business substance.

## Architecture

At the vision level, Loom is a three-layer system. At the repository level, it
lands as five stable parts:

- Governance defines rules, review models, and closeout semantics.
- Harness provides execution support, workspace isolation, recovery, and runtime visibility.
- Templates carry structured artifacts.
- Skills assemble these capabilities into executable entry points.
- Adoption records where capabilities came from and where they currently land.

The dependency flow is one-way: governance defines rules, templates carry
structure, harness runs within governance constraints, skills read all of them
and assemble entry points, and adoption provides evidence and evolution. Skills
do not redefine governance rules, templates do not become the only truth source,
and status surfaces do not become a second item truth source.

## Workflow Model

Loom is CLI-first. The global `loom` command installs the Codex user-level plugin,
records metadata-only repository adoption, reads the fact chain, and runs
verification. Agents start from `loom-init`, then move through scenario skills
such as `loom-adopt`, `loom-resume`, `loom-build`, `loom-review`, and
`loom-merge-ready`.

Everything is organized around a Work Item, the formal execution entry. Work
moves through a gate chain: spec gate, build gate, review gate, and merge gate.
Each gate consumes evidence and returns a pass, block, or fallback verdict.

Loom keeps truth sources separate. Governance rules, execution facts, review
records, and host state such as GitHub PRs, CI, and issues stay in their own
channels. The CLI reads and summarizes them; it does not create a second copy of
truth. When a gate passes, the relevant layers have been checked against the
same work.

## Quick Start

Copy this prompt to your coding agent:

```text
Install Loom in this repository with the current global CLI model. Use
metadata-only repository adoption; do not create repo-local Loom runtime,
plugin payload, `.loom/bin`, `.agents/skills`, or Loom-owned root `skills`.
Follow the steps below. If a command fails, stop and report the failing command
plus `loom repair plan --target . --json`.
```

Prerequisites: Node `>=20` and Python `>=3.11`.

1. Install the root CLI:

```bash
npm install -g @mc-and-his-agents/loom
```

2. Install and register the Codex user-level plugin:

```bash
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
```

3. Adopt the current repository:

```bash
loom install --target . --apply --json
```

4. Verify the install:

```bash
loom installed-state validate --target . --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

5. Start working from `loom-init` in a new Codex session. Restart Codex Desktop
   if it had already loaded the plugin list.

On a second development machine for an already adopted repository, install the
global CLI and register the Codex user-level plugin, then verify the repository:

```bash
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json
loom installed-state validate --target . --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json
```

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
