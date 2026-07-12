# loom_check Runtime Purity

本文件定义 `loom_check` 的并发隔离与运行现场纯度合同。

本合同承接 #962 P0-A 批次，并作为 #964、#965、#966、#967、#968 的实现和 review 依据。

## 1. 能力定位

`loom_check` 是 Loom source/distribution 仓库与 bootstrapped consumer 仓库的本地验证入口。

它必须验证当前目标，而不是把当前 shell、Codex App 会话、固定临时路径、Node 构建目录或稳定 fixture 当作共享运行现场。

本合同同时冻结 #953 的 source self-check 分层入口，但不扩大 closeout gate、PR metadata 或 review profile 的判定范围。

## 2. Profile 边界

`loom_check.py --profile auto|source|consumer` 的运行现场边界如下：

- `source` profile 检查 Loom source/distribution 仓库，允许消费 source repo 的 checked-in docs、skills surface、installer package 与 demo fixture。
- `consumer` profile 检查 bootstrapped consumer repo，必须只消费 consumer runtime/adoption surface，不得回退到 Loom source self-check。
- `auto` 只负责选择 `source` 或 `consumer`，不得因为宿主环境变量或 live host proof 改变 profile。

`source` profile 还支持 `--source-surface full|contract-only|source-self-fixture|bootstrap-regression|distribution-regression`。这些 selector 的 shared vocabulary、最小 evidence schema 与 fast/full policy 见 [regression-surface-contract.md](./regression-surface-contract.md)：

- `full` 是默认值，等价于既有完整 source/distribution self-check。
- `contract-only` 面向普通本地 closeout 与快速合同验证，只消费文档、schema、fixture contract、routing、profile 和 link 检查。
- `source-self-fixture` 面向 Loom source repo 深层 harness fixture，覆盖 daily execution、adversarial adoption、repo companion / interop 等重型行为样本。
- `bootstrap-regression` 面向 scaffold、demo bootstrap、repo-local CLI 与 root self-adoption 回归。
- `distribution-regression` 面向 installer、generated artifacts、GitHub CLI budget 与分发一致性。

所有 source surface 必须向 stderr 输出阶段化进度，至少包含 surface、step、elapsed 和本 step 新增 failure 数。stdout 仍保留最终机器/人工可读报告。

所有 profile 都必须设置唯一 `run_id`，并把运行态写入限定在当前 worktree 或本次运行拥有的唯一临时目录。本次运行创建的 `loom-check-*` 临时目录必须在使用结束后及时清理，不得成为后续检查的隐式输入。

## 3. 并发语义

同一 worktree 内的 full `loom_check` 必须 single-flight。

第二个 full check 启动时可以 fail-fast 或 bounded wait，但输出必须包含当前 lock owner 信息，至少包括：

- `run_id`
- `pid`
- `started_at`
- `command`
- `cwd`

stale lock 必须可恢复，不得永久阻断后续检查。stale 判定可以基于 pid 不存在、超时或 lock payload 不可读后的保守恢复策略。

同仓不同 worktree 可以并发执行。任何 lock 或运行态目录都不得使用仓库级全局路径阻断不同 worktree。

跨仓并发可以并行执行。`loom_check` 不得使用固定 `/tmp` 路径、全机器 lock 或当前 Codex App 会话状态作为默认 blocking 输入。

## 4. 允许写入面

默认 `loom_check` 允许写入：

- 当前 worktree 内明确属于运行态的 lock、cache 或生成 staging 目录
- 本次运行创建并拥有的唯一临时目录
- 工具在隔离 cache、临时目录或受 lock 保护目录中的构建输出

默认 `loom_check` 不得重写：

- checked-in stable fixture，例如 `examples/new-project`
- authored governance truth，例如 work item、progress、review、status 或 closeout carrier
- 其他 worktree 或其他仓库的运行态目录
- 固定 `/tmp` 负样本路径

需要刷新 stable fixture 时，必须走显式 generate/sync 入口，并在 PR 中把 fixture drift 作为正常变更审查。

## 5. 宿主环境纯度

`loom_check` 默认 subprocess 环境必须清理只应由专用 fixture 显式传入的宿主变量，包括：

- `CODEX_*`
- `LOOM_CODEX_APP_REVIEW_*`
- `CODEX_CI`
- `CI` 中会改变 review adapter 或 live proof 默认路径的值

保留 `PATH`、`HOME` 与 `gh` keyring 可读性，但不得全局导出 token。

live GitHub、Codex App proof、dynamic tool live smoke 与 host adapter live drift 只能在显式 opt-in 或专用 synthetic fixture 中进入验证。默认 source self-check 不得因为当前 Codex Desktop thread 环境自动切换 review adapter 或 live host proof。

## 6. 回归要求

#968 至少覆盖以下 P0-A 回归：

- 同一 worktree 双 `loom_check` 启动证明 single-flight 行为
- 同仓不同 worktree 并行不共享 worktree-local mutable outputs
- 跨仓或临时 clone 不受固定 `/tmp` 路径影响
- 默认 subprocess 环境不会继承 Codex App / host proof 污染源
- 默认 `make loom-check` 不让 `examples/new-project` 因检查本身变脏

重型并发矩阵可以作为显式 opt-in validation，但 P0-A 默认回归必须可在本地和 CI 中稳定消费。

`make loom-check-runtime-regression` 保留为显式 compatibility diagnostics，不再由默认 `make loom-check` 或 main CI 消费。默认 `make loom-check` 只聚合 host-native lifecycle contracts；需要排查旧 runtime lock、环境纯度或 demo fixture 时才显式运行该诊断入口。

## 7. Runtime Regression Surface Closeout

#1263 consumes the runtime regression split through named local surfaces while
preserving the aggregate `loom-check-runtime-regression` entrypoint:

| Surface label | Command |
| --- | --- |
| `single-flight-locking` | `make loom-check-runtime-single-flight-locking` |
| `worktree-local-lock-paths` | `make loom-check-runtime-worktree-local-lock-paths` |
| `subprocess-env-purity` | `make loom-check-runtime-subprocess-env-purity` |
| `temp-dir-cleanup` | `make loom-check-runtime-temp-dir-cleanup` |
| `demo-fixture-cleanliness` | `make loom-check-runtime-demo-fixture-cleanliness` |

The aggregate commands remain `python3 tools/check_loom_check_runtime_regressions.py`,
`make loom-check-runtime-regression`. It is not a default CI or `make loom-check`
consumer. The retained historical closeout record is
[validation-runtime-regression-surface-closeout.md](../../evidence/validations/validation-runtime-regression-surface-closeout.md).

This is evidence only. It does not close parent #1263/#1255, publish a release,
or authorize changes to shared contract/schema/parser/failure vocabulary.
