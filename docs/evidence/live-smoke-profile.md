# Live Smoke Profile

本文件定义 v0.10.0 的 adopted-repo live smoke foundation。

它回答的不是“某个 adopted repo 是否已经通过所有治理面”，而是“Loom 是否能用真实 adopted repo 或 versioned prior-pass evidence 产出可消费的 `orchestration-live` confidence input”。

## Command

`python3 tools/loom_flow.py live-smoke run --target <repo> [--item <id>] [--dry-run] [--include-blocking-shadow]`

`python3 tools/loom_flow.py live-smoke replay --prior-evidence <path>`

输出 schema 固定为 `loom-live-smoke/v1`。

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

`shadow-parity --blocking` 只能通过显式 `--include-blocking-shadow` 加入 command set。单个 adopted repo smoke 不得被描述为 blocking shadow parity 升级证据。

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
