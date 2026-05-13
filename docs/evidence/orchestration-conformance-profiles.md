# Orchestration Conformance Profiles

本文件定义 Loom 的 orchestration conformance profiles。

这些 profiles 最初冻结于 v0.7.0，并由后续版本继续扩展。

这些 profiles 回答的是“当前 release 的编排能力是否可证明”，不得替代 governance maturity profile。

## 1. Profile 分工

| Profile | 目标 | 默认阻断性 | 权威输入 |
| --- | --- | --- | --- |
| `orchestration-core` | 证明 Loom core 恢复、workspace、ledger、merge-ready、closeout 与生成面可在本仓稳定运行 | blocking | `loom_check`、skills surface、installer payload、repo-local demo、main gates |
| `orchestration-extension` | 证明可选宿主能力、repo companion、repo interop、dynamic tool / host action locator 边界可被读取和 fail-closed | profile-local blocking / advisory | repo companion、repo interop、host action contract、adapter boundary fixtures |
| `orchestration-live` | 证明至少一个 adopted repo 或 adopted-repo smoke path 能给 release confidence 提供真实反馈 | non-blocking by default | versioned live smoke evidence |

## 2. `orchestration-core`

`orchestration-core` 是普通 PR 和 release closeout 的默认 blocking profile。

最小覆盖面：

- fact-chain / recovery entry / execution ledger 读取一致
- workspace locate / attach / cleanup / retire 边界一致
- resume / handoff / merge-ready 消费同一 recovery / ledger contract
- generated `skills/**`、`.loom-runtime/**`、`examples/new-project/.loom/**` 与 `src/skills/**` 同步
- installer payload、version surface、runtime-state 和 `loom_check` 自检可运行
- structured event evidence validator 和 fake agent / fake tracker fixtures 可证明 success、failure、tool failure、active、closed、drift 行为

Core 缺口必须 fail closed，因为这些能力构成 Loom v0.7.0 的可恢复 harness 执行控制面。

## 3. `orchestration-extension`

`orchestration-extension` 只覆盖可选宿主能力和 adopted repo 扩展面。

最小覆盖面：

- repo companion / repo interop locator-only 合同
- host action / dynamic tool declaration-time locator contract
- hook locator safety declarations, mapped hook envelopes, and unsafe
  host-adapter results
- host-backed tracker state 只能作为 structured event evidence 或 retained host result 被消费
- required locator missing / unreadable / invalid boundary 的 fail-closed 行为
- optional / advisory missing in-repo locator 只进入 profile-local `missing_optional`
- adapter drift、shadow parity、external runtime、repo-native carrier 只作为 retained evidence 或 advisory/profile-local gate 消费

Extension 缺口不得污染 `orchestration-core` pass/fail。若某 adopted repo 显式启用 stronger extension gate，该启用点必须记录 owner、fallback、override path 与 authority-of-truth。

### `orchestration-extension/hooks`

`orchestration-extension/hooks` 是 hooks 的 optional extension profile。未声明
`hook_locators` 时，该 profile 固定输出 `not_applicable`，core profile remains pass。

启用条件仅来自 repo companion `.loom/companion/repo-interface.json` 的
`hook_locators`。启用后：

- required hook safety、locator、host trust 或 permission risk 缺口可以在
  hooks extension path 内返回 `block`
- optional/advisory hook 缺口只进入 profile-local `warn` 和
  `missing_optional`
- mapped hook envelope 的 `adapter_result: unsafe` 只影响对应 configured
  hook path，不改写 authored progress、status truth、review verdict 或
  closeout basis
- `orchestration-core` 不因为 hooks 未启用、optional/advisory hooks 缺失或
  profile-local warnings 改变 pass/fail

该 profile 的 live evidence 命令是
`python3 tools/loom_flow.py live-smoke hooks-extension --target <repo>`，输出
schema 为 `loom-hooks-extension-profile/v1`。

## 4. `orchestration-live`

`orchestration-live` 是 release confidence profile，不是普通 PR 的默认 blocking gate。

最小覆盖面：

- 至少一个 adopted repo 或 adopted-repo smoke path
- 明确记录 target、branch/commit/worktree、命令、结果与日期
- smoke 不可运行时，必须输出 explicit skip / unavailable evidence，说明缺少的宿主、路径、凭据或环境前置
- live smoke 失败可以降低 release confidence，但不得自动替代 `orchestration-core` 的 blocking 判定

当前 live smoke 的稳定命令与 evidence 形态见 [live-smoke-profile.md](./live-smoke-profile.md)。

Live profile 的目标是防止 release 只在模型内自洽；它提供真实反馈证据，但不把外部仓库可用性变成每个普通 PR 的默认阻断条件。

## 5. 与 Governance Maturity Profile 的关系

Governance maturity profile 回答的是一个仓库处于 `light -> standard -> strong` 的哪一档。

Orchestration conformance profiles 回答的是 Loom release 的编排能力是否具备可消费证据。

二者关系固定如下：

- `orchestration-core` 可以作为 release readiness 的 blocking 输入
- `orchestration-extension` 只在对应 extension scope 内阻断或 advisory
- `orchestration-live` 只提升或降低 release confidence
- 任何 orchestration profile 都不得把下游仓库成熟度改写成 Loom core truth
