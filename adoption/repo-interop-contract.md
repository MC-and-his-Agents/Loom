# Repo Interop Contract

本文冻结 Loom 面向成熟既有仓库的 `repo interop` 主合同。

它承接的是 companion-owned 的只读消费面，而不是新的宿主执行层。

## 1. 目标与边界

`.loom/companion/interop.json` 用于声明三类只读入口：

- retained host action result 的读取入口
- repo-native carrier / evidence / truth 的读取入口
- `shadow mode` parity compare 的读取入口

它不承接：

- branch / PR / worktree / merge 的执行命令
- repo runtime state、review summary、validation status
- host action result 的 authored 真相副本
- 新的 blocking merge gate

换句话说，`interop.json` 只告诉 Loom “去哪里读”，不告诉 Loom “如何替宿主执行”。

## 2. `.loom/companion/interop.json`

当前稳定 schema：

```json
{
  "schema_version": "loom-repo-interop/v1",
  "host_adapters": [],
  "repo_native_carriers": [],
  "shadow_surfaces": {
    "admission": {
      "summary": "Compare admission parity between Loom and the repo-native result.",
      "loom_locator": ".loom/shadow/admission-loom.json",
      "repo_locator": ".loom/shadow/admission-repo.json"
    },
    "review": {
      "summary": "Compare review parity between Loom and the repo-native result.",
      "loom_locator": ".loom/shadow/review-loom.json",
      "repo_locator": ".loom/shadow/review-repo.json"
    },
    "merge_ready": {
      "summary": "Compare merge-ready parity between Loom and the repo-native result.",
      "loom_locator": ".loom/shadow/merge-ready-loom.json",
      "repo_locator": ".loom/shadow/merge-ready-repo.json"
    },
    "closeout": {
      "summary": "Compare closeout parity between Loom and the repo-native result.",
      "loom_locator": ".loom/shadow/closeout-loom.json",
      "repo_locator": ".loom/shadow/closeout-repo.json"
    }
  }
}
```

顶层字段约束：

- `schema_version` 固定为 `loom-repo-interop/v1`
- `host_adapters` 必须存在，可为空数组
- `repo_native_carriers` 必须存在，可为空数组
- `shadow_surfaces` 必须同时声明 `admission`、`review`、`merge_ready`、`closeout`

## 3. `host_adapters`

`host_adapters[*]` 固定字段：

- `id`
- `summary`
- `surfaces`
- `locator`

其中：

- `surfaces` 必须是非空数组
- `surfaces[*]` 只允许 `admission | pre_review | review | build | merge_ready | closeout`
- `locator` 只描述 Loom 如何读取 retained host action 的结果，不描述如何执行动作本身

典型对象包括：

- guardian verdict
- integration contract verdict
- repo settings / ruleset verdict
- repo-native merge readiness verdict

## 4. `repo_native_carriers`

`repo_native_carriers[*]` 固定字段：

- `id`
- `summary`
- `surfaces`
- `locator`

其中：

- `locator` 可以指向 repo-native truth / evidence 目录、文件或生成结果
- 这些 carrier 继续保留为仓库原生真相，不要求先迁成 Loom carrier

典型对象包括：

- exec-plan 目录
- governance status 输出
- integration contract 输出
- repo-native evidence ledger

## 5. `shadow_surfaces`

`shadow_surfaces` 当前只承接四个固定比对面：

- `admission`
- `review`
- `merge_ready`
- `closeout`

每个 surface 固定字段：

- `summary`
- `loom_locator`
- `repo_locator`

稳定约束：

- parity compare 结果只允许 `match | mismatch | unreadable`
- `shadow mode` 在本树内只做 validation / parity，不直接成为 merge gate
- `shadow_surfaces` 只描述比对入口，不声明“哪一方自动获胜”

### 5.1 从 validation-only 升级前必须满足的证据标准

在进入下一阶段之前，`shadow parity` 仍固定保持为 validation-only compare surface。

要讨论是否从 validation-only 升级到更强治理面，必须同时满足以下条件：

1. 至少两个新增的 live adopted repo
   - 不得只重复消费当前 `Syvert` / `WebEnvoy` 基线表述
2. 每个样本都提供版本化 parity 记录
   - 至少覆盖 `admission`
   - `review`
   - `merge_ready`
   - `closeout`
3. `mismatch` 必须能稳定分型
   - 至少区分：
     - contract drift
     - surface unreadable
     - Loom bug
     - repo-native lag
4. 必须证明更强 gate 的收益
   - 也就是自动升级后能减少真实错误放行
   - 同时不会制造不可接受的误阻断
5. blocking ownership、override path、authority-of-truth 必须落在 `interop.json` 之外的权威合同
   - 例如 host action、closeout gate、review / checkpoint 合同

只要以上任一条件未满足，`shadow parity` 就不得从 validation-only 升级。

### 5.2 当前明确不做

在本树当前阶段，明确不做以下升级：

- 不把 `mismatch` 直接视为 blocking merge gate
- 不把 `unreadable` 视为 repo-native 失败或 Loom 自动获胜
- 不在 `interop.json` 中声明 blocking owner、override decision 或 final verdict
- 不要求 `shadow parity` 代替 review、merge-ready 或 closeout 的正式 authority-of-truth

## 6. 与其他合同的关系

- `repo-interface.json`
  - 承接 repo-specific rules、requirements、typed gates、metadata/context contract
- `interop.json`
  - 承接 retained host action result、repo-native carrier 与 shadow parity 的只读入口
- [host-action-contract.md](/Users/mc/dev/Loom/harness/host-action-contract.md)
  - 承接宿主动作 ownership、结果语义与 fallback discipline

纪律重申：

- 不把 interop 细节塞回 `repo-interface.json`
- 不让 `interop.json` 承载运行态或 authored state
- 不让 Loom 因为读取了 interop contract，就接管宿主底层实现
- 不让 `interop.json` 定义 blocking owner、override path 或 final merge authority
