# Live Smoke Profile

本文件定义 v0.10.0 以来的 adopted-repo live smoke foundation。

它回答的不是“某个 adopted repo 是否已经通过所有治理面”，而是“Loom 是否能用真实 adopted repo 或 versioned prior-pass evidence 产出可消费的 `orchestration-live` confidence input”。

## Command

`python3 tools/loom_flow.py live-smoke run --target <repo> [--item <id>] [--dry-run] [--include-blocking-shadow]`

`python3 tools/loom_flow.py live-smoke replay --prior-evidence <path>`

`python3 tools/loom_flow.py live-smoke host-adapter-drift --target <repo>`

`python3 tools/loom_flow.py live-smoke dynamic-tool-availability --target <repo> [--surface attempt_time|review|merge_ready|closeout|build|admission|pre_review|all]`

`python3 tools/loom_flow.py live-smoke hooks-extension --target <repo>`

`python3 tools/loom_flow.py live-smoke external-orchestrator-interop --target <repo>`

输出 schema 固定为 `loom-live-smoke/v1`。

`host-adapter-drift` 输出 schema 固定为 `loom-host-adapter-live-drift/v1`。

`dynamic-tool-availability` 输出 schema 固定为 `loom-dynamic-tool-live-availability/v1`。

`hooks-extension` 输出 schema 固定为 `loom-hooks-extension-profile/v1`。

`external-orchestrator-interop` 输出 schema 固定为
`loom-external-orchestrator-conformance/v1`。

## Run Contract

`run` 必须记录：

- target path
- branch / commit / worktree
- planned commands
- command reports
- result
- date
- release interpretation

默认 command set：

- target / worktree availability check
- `governance-profile status`
- `governance-profile upgrade-plan`
- `runtime-parity validate`
- `shadow-parity` validation-only
- `flow resume --item <id>`

`shadow-parity --blocking` 只能通过显式 `--include-blocking-shadow` 加入 command set。单个 adopted repo smoke 不得被描述为 blocking shadow parity 升级证据；该步骤 is not sufficient blocking-upgrade evidence on its own.

## Unavailable Evidence

若 adopted repo target、worktree、宿主、路径或凭证不可用，`run` 必须输出 explicit unavailable evidence，而不是静默 pass。

最小 unavailable evidence 字段：

- target path
- commands that were planned
- result
- missing precondition
- date
- release interpretation

这类 unavailable evidence 是 non-blocking confidence input，`fallback_to` 为 `live-smoke-retry-or-record-unavailable`。

## Replay Contract

`replay` 只读取 versioned evidence，不执行 adopted-repo commands。

它至少要读取：

- prior evidence path
- prior evidence status
- recorded target family
- recorded branch / commit / worktree when present
- recorded command set
- recorded release interpretation

当前 v0.10.0 允许 replay v0.7 prior-pass evidence，例如 [validation-v0.7-live-orchestration-smoke.md](./validations/validation-v0.7-live-orchestration-smoke.md)。

## Result Semantics

顶层 `result` 只允许：

- `pass`
- `warn`
- `block`

稳定语义：

- target 不存在、路径 / 凭证不可用、profile-local live command failure：`warn`
- replay evidence 缺失或不可读、subcommand JSON 不可读、runtime state 不一致：`block`
- 全部 planned live checks 成功，或 prior-pass evidence replay 成功：`pass`

`run` / `replay` 都不得把 `orchestration-live` 提升为普通 PR 的默认 blocking gate。

## Host Adapter Drift Contract

`host-adapter-drift` 读取 adopted repo `.loom/companion/interop.json` 中声明的 `host_adapters[*]`，并对每个 retained host action locator 产出 profile-local drift evidence。

最小检查面：

- repo interop contract 是否存在且可读
- `host_adapters[*]` 是否声明合法的 `id`、`owner`、`requirement`、`surfaces`、`locator`、`fallback_to`
- locator 是否缺失、越界、不可读或指向目录
- envelope 是否显式报告 `permission_unavailable`
- envelope 若声明 `host_adapter_version`，是否与当前 Loom host adapter authority 一致

稳定 drift classification：

- `version_drift`
- `locator_missing`
- `locator_unreadable`
- `permission_unavailable`
- `unsafe_locator`
- `invalid_declaration`

结果纪律：

- required host adapter drift 可以在该命令内返回 `block`
- optional / advisory host adapter drift 只返回 profile-local `warn`
- interop absent 或未声明任何 host adapter 时返回 `warn`
- 命令不得执行 host action、不得写宿主控制面、不得改写 `interop.json`

## Dynamic Tool Live Availability Contract

`dynamic-tool-availability` 读取 adopted repo `.loom/companion/repo-interface.json` 中声明的 `dynamic_tool_locators[*]`，并把已有 `tool_availability` 词表包装成 live/profile-local evidence。

最小检查面：

- repo companion interface 是否存在且可读
- `dynamic_tool_locators[*]` 是否声明合法的 `id`、`owner`、`requirement`、`surface`、`locator`、`fallback_to`
- locator 是否缺失、越界、不可读或指向无效 handshake declaration
- handshake declaration 是否只使用 `advertised | unavailable | unsupported | failed`
- optional/advisory failure 是否保持 profile-local，不污染 `orchestration-core`

结果纪律：

- required dynamic tool unavailable / unsupported / failed / invalid declaration 可以在该命令内返回 `block`
- optional / advisory failure 只返回 profile-local `warn`
- repo interface absent 时返回 explicit unavailable evidence 与 `warn`
- repo interface present 但当前 surface 无 dynamic tools 时返回 `pass`
- 命令 does not execute the tool, 不得探测宿主协议、不得写 repo companion / host state，也不得固化 tool-specific protocol

## Hooks Extension Profile Contract

`hooks-extension` 读取 adopted repo `.loom/companion/repo-interface.json` 中声明的
`hook_locators[*]`，并把 declaration-time hook safety 结果包装成
`orchestration-extension/hooks` profile-local evidence。

最小检查面：

- repo companion interface 是否存在且可读
- `hook_locators[*]` 是否声明合法的 `id`、`summary`、`lifecycle`、
  `locator`、`owner`、`requirement`、`fallback_to` 与 `safety`
- locator 是否缺失、越界、不可读或指向目录
- safety 是否保持 repo-relative path containment、runtime-evidence-only truth
  boundary、Loom-owned cleanup scope、trusted/reviewed host trust 与明确
  permission risk
- optional/advisory gap 是否保持 profile-local，不污染
  `orchestration-core`

结果纪律：

- 未声明 `hook_locators` 时返回 `pass`，`hooks_extension.status` 为
  `not_applicable`
- required unsafe hook declaration 可以在该命令内返回 `block`
- optional/advisory hook gap 只返回 profile-local `warn`
- `core_profile.result` 必须保持 `pass`，`core_profile.hook_enforcement` 固定为
  `not_applicable`
- 命令 does not execute hooks，不生成 host-native hook files，不写 repo
  companion、host state、authored progress 或 status truth

## External Orchestrator Interop Profile Contract

`external-orchestrator-interop` 读取 adopted repo
`.loom/companion/interop.json` 中声明的 `external_orchestrators[*]`，并把
retained read evidence 包装成 `orchestration-extension/external-orchestrator`
profile-local evidence。

最小检查面：

- repo interop contract 是否存在且可读
- `external_orchestrators[*]` 是否声明合法的 `operations`、`locator`、
  `requirement` 与 `fallback_to`
- retained evidence 是否只表达 `work_item_read`、`workspace_attach`、
  `recovery_writeback`、`status_read` 或 `gate_read`
- status/gate consumption 是否只读消费 `status control plane v2` 与现有 gate chain
- retained evidence 是否避免 scheduler state、daemon、tracker polling、host
  lifecycle ownership、status truth、gate truth、review verdict、validation summary、
  host action result 或 closeout basis

结果纪律：

- 未声明 external orchestrator 时返回 `pass`，`external_orchestrator.status`
  为 `not_applicable`
- optional / advisory locator gaps 只返回 profile-local `warn`
- required locator 缺失、truth pollution、scheduler-private fallback 或 lifecycle
  ownership 漂移返回 `block`
- `core_profile.result` 必须保持 `pass`，`core_profile.external_orchestrator_enforcement`
  固定为 `not_applicable`
- 命令不启动 daemon，不调度 worker，不创建/删除 branch、PR、git worktree 或目录，
  不写 recovery/status/gate/review/host state
