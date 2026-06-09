# Repo-Local Gate Starter

Loom 可以提供 repo-local gate starter aliases，让新仓库在没有宿主控制面之前也能启动一致的本地检查入口。

这些 aliases 是 Loom source/runtime 的可执行启动器，不是 GitHub、CI、branch protection 或 merge queue 的替代物。

## Stable Aliases

| Alias | Runtime entry | Purpose |
| --- | --- | --- |
| `verify` | `python3 .loom/bin/loom_init.py verify --target .` | 读取 bootstrap 与事实链是否完整。 |
| `status` | `python3 .loom/bin/loom_status.py --target . --item <current-item>` | 汇总当前 Work Item、review、merge checkpoint 与 host 读面。 |
| `merge-ready` | `python3 .loom/bin/loom_flow.py flow merge-ready --target . --item <current-item>` | 编排本地 merge-ready 检查。 |
| `closeout-check` | `python3 .loom/bin/loom_flow.py closeout check --target .` | 检查 closeout 是否能消费本地 carrier 与可读 host 输入。 |
| `reconciliation-audit` | `python3 .loom/bin/loom_flow.py reconciliation audit --target .` | 审计 issue / PR / project / branch drift，不写宿主状态。 |

## Repo-Local CLI Local Validation

Loom source repo 的 `repo-local-cli` 本地 aliases 只用于重放 GitHub Actions `repo-local-cli` job 内部的稳定 command groups。它们不创建新的 hosted required check name，也不替代 `repo-local-cli`、`loom-check`、PR gate、merge-ready 或 controlled merge。

Fast validation 表示复现一个失败的 frozen group：

```bash
make repo-local-cli-fast GROUP=<group>
```

`GROUP` 必须是下表中的 frozen group name。也可以直接运行对应 `make repo-local-cli-<group>` target。

Full local replay 表示按 CI 内部顺序运行全部 frozen groups：

```bash
make repo-local-cli-full
```

Full local replay 是本地诊断证据，不是 merge-ready 放行证据。merge-ready 仍必须消费当前 PR head、review、fact-chain、CI/hosted checks、PR metadata、release/no-release 判断和 scheduler-owned gates。

| Order | Frozen group name | CI step name | Local alias | Execution surface |
| --- | --- | --- | --- | --- |
| 0 | `setup-demo-bootstrap` | `repo-local-cli: setup-demo-bootstrap` | `make repo-local-cli-fast GROUP=setup-demo-bootstrap` or `make repo-local-cli-setup-demo-bootstrap` | `make loom-demo-new-project-check` from repo root. |
| 1 | `init-runtime` | `repo-local-cli: init-runtime` | `make repo-local-cli-fast GROUP=init-runtime` or `make repo-local-cli-init-runtime` | `python3 .loom/bin/loom_init.py runtime-state --target .`; `python3 .loom/bin/loom_init.py verify --target .` from `examples/new-project`. |
| 2 | `fact-chain` | `repo-local-cli: fact-chain` | `make repo-local-cli-fast GROUP=fact-chain` or `make repo-local-cli-fact-chain` | `python3 .loom/bin/loom_init.py fact-chain --target .`; `python3 .loom/bin/loom_flow.py runtime-state --target . --item INIT-0001`; `python3 .loom/bin/loom_flow.py fact-chain --target . --item INIT-0001`; `python3 .loom/bin/loom_flow.py runtime-evidence --target . --item INIT-0001`; `python3 .loom/bin/loom_flow.py state-check --target . --item INIT-0001` from `examples/new-project`. |
| 3 | `flow-gates` | `repo-local-cli: flow-gates` | `make repo-local-cli-fast GROUP=flow-gates` or `make repo-local-cli-flow-gates` | `python3 .loom/bin/loom_flow.py flow pre-review --target . --item INIT-0001`; `python3 .loom/bin/loom_flow.py checkpoint admission --target . --item INIT-0001` from `examples/new-project`. |
| 4 | `workspace-locate` | `repo-local-cli: workspace-locate` | `make repo-local-cli-fast GROUP=workspace-locate` or `make repo-local-cli-workspace-locate` | `python3 .loom/bin/loom_flow.py workspace locate --target . --item INIT-0001` from `examples/new-project`. |
| 5 | `purity-check` | `repo-local-cli: purity-check` | `make repo-local-cli-fast GROUP=purity-check` or `make repo-local-cli-purity-check` | `python3 .loom/bin/loom_flow.py purity-check --target . --item INIT-0001` from `examples/new-project`. |
| 6 | `runtime-state-scene-conflict-negative` | `repo-local-cli: runtime-state-scene-conflict-negative` | `make repo-local-cli-fast GROUP=runtime-state-scene-conflict-negative` or `make repo-local-cli-runtime-state-scene-conflict-negative` | `LOOM_SOURCE_REPO_ROOT="$PWD" LOOM_INSTALLED_SKILLS_ROOT="$PWD/skills" LOOM_RUNTIME_SCENE=upgrade-rehearsal python3 skills/shared/scripts/loom_flow.py runtime-state --target examples/new-project --item INIT-0001` from repo root; the alias fails if this command succeeds. |

The group names and order are intentionally identical to the frozen `repo-local-cli` CI command groups. Do not rename these local group labels or move the runtime-state scene conflict negative check into a positive group; that check must remain fail-closed.

## Machine Contract

`governance_surface.gate_starter` 与 `governance_control_plane.gate_starter` 必须使用：

- `schema_version: loom-gate-starter/v1`
- `authority: local`
- `enforcement: advisory`
- `host_enforcement: false`
- `host_enforcement_status: not_host_enforced`

每个 alias 必须声明：

- `surface`
- `entrypoint`
- `command`
- `authority`
- `enforcement`
- `host_enforcement`
- `summary`

## Failure Semantics

本地 alias 的存在只能证明 Loom starter 已定义或 repo-local runtime 可读。

它不能证明：

- GitHub Actions workflow 已安装。
- required checks 已配置为 blocking。
- branch protection 或 ruleset 已强制。
- PR merge path 已受控。
- merge queue、squash policy 或 host merge button 已由 Loom 接管。

若 repo-local runtime 尚未安装，`missing_entrypoints` 可以列出缺失入口；但 alias 合同本身仍保持 advisory。升级到 `strong` 必须由 host enforcement 读面单独证明。
