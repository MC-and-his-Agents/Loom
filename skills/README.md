# Skills

Language: English | [中文版本](./README.zh-CN.md)

`skills/` is the generated, checked-in Loom skills install surface. The editable source truth lives in `src/skills/`.

This directory is the Loom source repository's generated skills mirror. The
published skills payload is the Codex user plugin payload under
`plugins/loom/skills/`. Each `skills/<skill-id>` directory remains a source
organization and compatibility mirror, not a self-contained single-skill
package. Methodology and architecture documents stay behind this layer; users
should enter through skills instead of internal governance docs.

By default, start from `loom-init` for adoption, routing, and work recovery. It is the unique root entry for Loom and is responsible for two things:

- initialize Loom or retrofit Loom into an existing repository
- route the operator to the correct scenario skill when no explicit skill was named

For ordinary delivery after a Work Item has a PR, use `loom ship` as the primary
CLI path. It consumes PR metadata, the PR gate, controlled merge, and the
closeout policy so light and standard changes can merge and close out without a
follow-up closeout PR.

The `skills/` layer consumes the current strong-governance control plane with these fixed constraints:

- `Work Item` is the only formal execution entry
- delivery planning can produce an issue-tree plan before execution, but it does not replace `Work Item`, spec, review, merge-ready, or closeout truth
- tasks that hit the formal spec path must pass the `spec gate` first
- the release chain converges on `spec gate -> build gate -> review gate -> merge gate`
- `status control plane` only reads and summarizes fact-chain and host control-plane truth, and does not author a second source of truth
- profile maturity upgrades through `light -> standard -> strong`, while item maturity still advances through the governance state machine
- merge is controlled by GitHub or an equivalent host control plane; `loom ship`
  is the default CLI wrapper that consumes the prerequisites, executes host
  merge when requested, and performs inline or host-only closeout when the
  closeout policy allows it

## Skills Library

Loom exposes one root entry and ten scenario skills:

| Skill | Role |
| --- | --- |
| `loom-init` | Root entry; initializes and routes. |
| `loom-adopt` | Initializes a new repository or retrofits Loom into an existing one. |
| `loom-resume` | Restores context and continues execution. |
| `loom-build` | Runs a bounded implementation/build round and validates delegated output integration before review. |
| `loom-story` | Turns product context into a User Story, Story Readiness, and business semantic confirmation point before spec / plan consumption. |
| `loom-pre-review` | Checks readiness before formal review. |
| `loom-spec-review` | Reviews the formal spec path and produces the `spec gate` consumed by later gates. |
| `loom-review` | Runs formal review and records review output. |
| `loom-handoff` | Writes a handoff point and next-step state. |
| `loom-retire` | Cleans up or retires the current worksite. |
| `loom-merge-ready` | Performs the final `merge gate` summary before GitHub-controlled merge. |

Primary delivery command:

```bash
loom ship --target <repo> --item <id> --issue <n> --pr <n> --branch <branch> --head-sha <sha> --apply --json
```

## Entry Model

Loom supports two entry modes:

- Explicit entry: the user names a scenario skill directly.
- Routed entry: the user starts at `loom-init`, and `loom-init` selects the scenario from task signals.

If task signals are incomplete, ambiguous, or missing required execution inputs, route back to `loom-init` and ask for the smallest missing signal. Stable routing rules live in [route-matrix.md](./route-matrix.md).

Routing only decides the scene skill. It does not replace the stable control plane:

- planning output stays on issue-tree plan / host carrier mapping until the user asks to create or update host objects
- execution entry stays on `Work Item`
- gates stay on the shared `gate chain`
- status reads stay on the shared `status control plane`
- merge stays on the host platform control plane, with `loom ship` as the
  ordinary delivery wrapper

## Install Model

The primary install model is the global `loom` CLI plus the Codex user plugin:

```bash
npm install -g @mc-and-his-agents/loom
loom host register --host codex --source <global-loom-package>/plugins/loom --scope user --apply --json
loom install --target . --apply --json
loom skills check --target . --json
```

Target repositories use metadata-only adoption. They must not receive
`plugins/loom/skills/`, `.agents/skills/`, root `skills/`, `loom-package.json`,
or package-internal `.loom-runtime/` as Loom install artifacts.

## Internal Contracts

These files are part of the runtime contract and should remain stable:

- [registry.json](./registry.json)
- [install-layout.json](./install-layout.json)
- [upgrade-contract.json](./upgrade-contract.json)
- [distribution-and-adapter-contract.md](./distribution-and-adapter-contract.md)

Shared runtime scripts, assets, and references live under [shared/](./shared/). They are consumed by scenario skills and by release tooling when generating the Codex user plugin payload.

Generated surface checks:

```bash
python3 tools/skills_surface.py generate
make skills-check
```
