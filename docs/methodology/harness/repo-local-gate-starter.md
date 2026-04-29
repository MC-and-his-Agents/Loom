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
