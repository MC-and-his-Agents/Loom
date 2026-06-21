# Loom

<a href="https://zread.ai/MC-and-his-Agents/Loom"><img height="28" alt="Ask Zread" src="https://img.shields.io/badge/Ask_Zread-_.svg?style=for-the-badge&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff"></a>
<a href="https://deepwiki.com/MC-and-his-Agents/Loom"><img height="28" alt="Ask DeepWiki" src="https://deepwiki.com/badge.svg"></a>

Language: English | [中文版本](./README.zh-CN.md)

Loom helps coding agents turn issues into merge-ready pull requests.

Coding agents can already write code. The hard part is everything around the
code: knowing what work is active, where it is running, which branch and PR own
it, what was verified, what review decided, whether CI agrees, and whether the
work is actually ready to merge.

Loom is CLI-first. It is an agent-first project operating layer for that
execution state. It turns a loose request into a tracked Work Item, binds that
work to a branch and PR, carries validation and review evidence forward, and
gives agents a clear path to resume, review, merge readiness, and closeout.

Without Loom, an agent often resumes from chat history and reconstructs the
state by guessing.

With Loom, the agent resumes from repository facts:

- what the Work Item is;
- where the workspace is;
- which branch and PR own the work;
- what changed;
- what has been validated;
- what review decided;
- how the work aligns with trunk truth;
- what still blocks merge readiness;
- what must be closed out after merge.

## When To Use Loom

Use Loom when agent work is bigger than a single prompt.

Loom is useful when:

- an issue may take more than one session;
- multiple agents or humans may touch the same work;
- a PR needs review evidence, CI evidence, and merge-readiness checks;
- the agent must resume after interruption without rereading the whole chat;
- the project needs a reliable record of what happened before and after merge;
- closing the PR is not enough, because docs, status, or project state also need
  to agree.

## What Loom Adds To A Repository

After adoption, Loom gives the repository an agent-operable execution path:

- Work Items: every implementation starts from a named unit of work.
- Workspace binding: the work is tied to a branch, workspace, and PR.
- Resume path: a new agent can recover the current state without guessing.
- Review path: review decisions become part of the work record.
- Validation evidence: checks and evidence are carried forward instead of lost
  in chat.
- Merge readiness: the PR is checked against the Work Item, branch, review, and
  evidence.
- Closeout: after merge, Loom helps retire the work cleanly instead of leaving
  stale state.

## How A Loom-Driven Task Feels

A typical Loom task looks like this:

1. Start from an issue or request.
2. Loom creates or resumes a Work Item.
3. The agent works in a bound branch and workspace.
4. The agent records what changed and what was validated.
5. Review checks the current head, not an outdated memory of the work.
6. Merge readiness checks that the Work Item, branch, PR, review, and evidence
   agree.
7. After merge, closeout records the completed state and retires the workspace.

Under the hood, work moves through a gate chain: spec gate, build gate, review
gate, and merge gate.

The goal is not to make the agent type faster. The goal is to make the work
harder to lose, misread, or merge prematurely.

## Try It In A Repository

The quickest way to understand Loom is to enable it in a real repository and ask
an agent to start from `loom-init`.

The install flow has three parts:

1. Install the global Loom CLI.
2. Install and register the Codex plugin.
3. Adopt the target repository with metadata-only Loom state.

Copy this self-contained prompt to your coding agent:

```text
Enable Loom in this target repository. Do not assume this repository already
knows Loom.

Loom has three layers:
1. Loom CLI: the global `loom` command on this machine.
2. Codex plugin: the user-level Codex interaction surface installed by the CLI.
3. Repository adoption: metadata written into the target repository so Loom can
   manage work items there.

First install the CLI:
node --version
npm --version
npm install -g @mc-and-his-agents/loom
loom version --json

Then install and register the Codex plugin:
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --apply --json

Then go to the target repository root and enable Loom:
cd /path/to/target-repository
loom install --target . --apply --json

Validate the result:
loom installed-state validate --target . --json
loom host verify --host codex --target . --json
loom skills check --target . --json
loom doctor --target . --json

Use metadata-only repository adoption. Do not clone the Loom repository into
this project. Do not manually create `.loom/bin`, `.agents/skills`, or root
`skills`. If any command fails, stop, report the failing command, then run:
loom repair plan --target . --json
```

Start working from `loom-init` in a new Codex session. Restart Codex Desktop if
it had already loaded the plugin list.

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

## Why Loom Works

Loom separates the parts of agent execution that often get mixed together:
governance rules, execution harness, evidence, structured artifacts, and
executable skills.

That separation matters because a PR can look done while the Work Item, review
record, validation evidence, or closeout state is still stale. Loom keeps those
channels separate, then uses the CLI to check whether they agree.

At the repository boundary, Loom keeps only metadata. The global `loom` command
installs the Codex user-level plugin, records repository adoption, reads the
fact chain, and runs verification. Agents start from `loom-init`, then move
through scenario skills such as `loom-adopt`, `loom-resume`, `loom-build`,
`loom-review`, and `loom-merge-ready`.

At the repository level, Loom lands as five stable parts:

- Governance defines rules, review models, and closeout semantics.
- Harness provides execution support, workspace isolation, recovery, and runtime visibility.
- Templates carry structured artifacts.
- Behavior evidence and test evidence keep validation separate from claims.
- Skills assemble these capabilities into executable entry points.
- Adoption records where capabilities came from and where they currently land.

The dependency flow is one-way: governance defines rules, templates carry
structure, harness runs within governance constraints, skills read all of them
and assemble entry points, and adoption provides evidence and evolution. Skills
do not redefine governance rules, templates do not become the only truth source,
and status surfaces do not become a second item truth source.

## What Loom Is Not

Loom does not decide what product to build, how to design product architecture,
how to model a business domain, or whether every project must use the same file
layout. It focuses on project operation, not business substance.

Loom is not a business template, a code generator, an SDD-only tool, or a
replacement for GitHub, CI, review engines, or `git worktree`. It is a project
operating layer with executable skills so agents can consume those host
capabilities consistently.

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

Loom is merge-readiness-centered and behavior-first. Review, validation, host
state, behavior evidence, test evidence, and closeout are separate surfaces, but
they must converge. If any one of them is still open, the work should not be
treated as finished.
