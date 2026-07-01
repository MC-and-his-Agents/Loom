# Loom

<a href="https://zread.ai/MC-and-his-Agents/Loom"><img height="28" alt="Ask Zread" src="https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff"></a>
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
6. `loom ship` checks that the Work Item, branch, PR, review, and evidence
   agree before merge.
7. After merge, the same ship run reads back the host state and completes the
   shortest legal closeout path.

Under the hood, work moves through a gate chain: spec gate, build gate, review
gate, and merge gate.

The goal is not to make the agent type faster. The goal is to make the work
harder to lose, misread, or merge prematurely.

## Daily Delivery Path

After Loom is installed and a Work Item has a PR, the default delivery command is
`loom ship`. It is the product path for ordinary work: check PR metadata, confirm
the gate inputs, merge through the host control plane when `--apply` is present,
then complete inline or host-only closeout without opening a second closeout PR.

```bash
loom ship \
  --target . \
  --item WI-123 \
  --issue 123 \
  --pr 456 \
  --branch work/123-example \
  --head-sha "$(git rev-parse HEAD)" \
  --apply \
  --json
```

The wrapper contract stays narrow and ordered:

- dry-run reads `pr-metadata preflight -> pr gate -> controlled merge check ->
  validation profile -> closeout policy`, then reports the first blocker
  summary, `missing_inputs`, and `next_action` without mutating host or repo
  state;
- `--validation-profile auto` uses changed paths to pick the smallest useful
  profile and reports the matching `loom_check --source-surface` command;
  explicit `--validation-profile full` still forces the full path;
- `--apply` may add one deterministic safe metadata repair step before that
  read-only sequence, but only when `--issue`, `--branch`, and `--head-sha` are
  explicit;
- that safe repair boundary never invents or resolves conflicting Work Item,
  branch, head SHA, release, or closeout facts on its own;
- `--json` stays on short wrapper diagnostics and may collapse detailed steps
  behind an artifact locator when stdout would be too large, while
  `--full-output` is only for explicit debugging, audit, or blocker
  classification;
- closeout policy decides whether ordinary delivery can continue through the
  shared inline/host-only host closeout path or must stop and hand off to an
  explicit batched carrier / full closeout path.

Light and standard changes should normally finish in that one command. Loom only
upgrades to a batched carrier PR or an explicit full closeout PR when the work is
a release, parent or milestone closeout, multi-Work-Item delivery, host/repo
conflict, reinforced-governance change, or another case that needs versioned
terminal evidence.

Today `loom ship` only executes the ordinary inline/host-only host closeout
path. Batched carrier writes and explicit full closeout PR execution stay in
follow-up issue scope; this wrapper blocks and points callers at the explicit
path instead of guessing.

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

`loom install` and `loom upgrade` manage only the target repository's
metadata-only adoption state. To inspect or refresh the local Codex plugin
provider, use `loom host doctor|install|register --host codex --scope user`.

For an already adopted single repository that pins Loom in a GitHub workflow,
use the runtime upgrade maintenance flow instead of hand-assembling the fact
chain:

```bash
loom -v
loom runtime-upgrade status --target . --json
loom runtime-upgrade prepare --target . --item <maintenance-work-item> --to <version> --apply --json
loom runtime-upgrade pr --target . --item <maintenance-work-item> --to <version> --create --json
loom runtime-upgrade check --target . --item <maintenance-work-item> --to <version> --pr <pr> --branch <branch> --head-sha <head-sha> --json
loom runtime-upgrade closeout --target . --item <maintenance-work-item> --issue <maintenance-issue> --pr <merged-pr> --sync --create-pr --json
```

This flow is workflow-only maintenance scaffolding. It still requires a real
maintenance Work Item, PR metadata readback, semantic review, hosted checks,
head binding, PR gate, and carrier closeout sync. The closeout lane reads the
host issue/PR state for `closedAt`, merge commit, target branch, and hosted run
URL; carrier-only review evidence covers only terminal carrier metadata drift,
not product implementation approval.

After a release is already published and read back, use the release closeout
sync wrapper to terminalize repo carriers without republishing:

```bash
loom release closeout-sync --target . --version <version> --item <work-item> --pr <release-pr> --apply --json
```

It only writes repo carrier surfaces under `--apply`: progress terminal
metadata, status sync, closeout/merge-ready shadow refresh, and post-commit PR
metadata/gate next commands. It does not create tags, publish npm, edit the
GitHub Release, or merge the closeout PR.

`runtime-upgrade status|prepare|check` also reports the local Codex
plugin/cache freshness and points to `loom host doctor --host codex --scope user
--json` plus `loom host install|register --host codex --scope user --apply
--json` when that workstation surface is stale. That is diagnostic guidance,
not a repository PR mutation. Plugin/cache stale state is advisory for the repo
PR unless the PR explicitly claims workstation Codex runtime/plugin readiness.

Start working from `loom-init` in a new Codex session. Restart Codex Desktop if
it had already loaded the plugin list.

For day-to-day delivery after a PR exists, ask the agent to use `loom ship`
instead of manually chaining merge-ready, reconciliation, carrier closeout, and
closeout checks.

For command discovery, start from the task path instead of scanning every
command:

| Task | First command |
| --- | --- |
| Resume work | `loom resume --target . --item <WI> --json` |
| Prepare a PR carrier set | `loom pr-intent prepare --intent <intent> --target . --item <WI> --apply --json` |
| Check PR readiness | `loom pr-intent check --intent <intent> --target . --item <WI> --pr <pr> --head-sha <sha> --json` |
| Review | `loom review --target . --item <WI> --json` |
| Merge-ready | `loom merge-ready --target . --item <WI> --json` |
| Release readback | `loom release readback --target . --version <version> --commit <sha> --json` |
| Release closeout | `loom release closeout-sync --target . --version <version> --item <WI> --pr <release-pr> --apply --json` |
| Runtime upgrade | `loom runtime-upgrade status --target . --json` |
| Codex plugin/cache | `loom host doctor --host codex --scope user --json` |

Prepare/apply commands report local readiness and the next command before a
hosted gate. Hosted gates still remain the final confirmation.

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

Target repository upgrade commands do not refresh the Codex plugin cache. Use
`loom host doctor --host codex --scope user --json` first, then
`loom host install --host codex --scope user --apply --json` and
`loom host register --host codex --scope user --apply --json` when the local
workstation plugin provider needs repair or refresh.

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
through scenario skills such as `loom-adopt`, `loom-resume`, `loom-build`, and
`loom-review`. When a PR is ready to deliver, `loom ship` is the primary CLI
path for merge plus closeout.

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
