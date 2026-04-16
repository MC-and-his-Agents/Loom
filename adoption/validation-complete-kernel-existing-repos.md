# Real Adoption Validation: Complete Kernel In Existing Repos

## 1. 样本标识

- 小型既有样本：`mail-listener`（验证副本：`/tmp/loom-val-mail`）
- 复杂既有样本：`hotcp`（验证副本：`/tmp/loom-val-hotcp`）
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#62`

## 2. 统一复验方法

两个样本都执行同一组动作：

1. bootstrap + verify
2. 提交 bootstrap 基线
3. 运行统一入口链路：
   - `fact-chain`
   - `runtime-evidence`
   - `state-check`
   - `flow pre-review`
   - `checkpoint admission/build/merge`
   - `workspace locate`
   - `purity-check`

## 3. 复验结果

### `mail-listener`

| 命令 | 结果 |
| --- | --- |
| `verify` | `ok: true` |
| `fact-chain` / `runtime-evidence` / `state-check` / `flow pre-review` | 全部 `pass` |
| `checkpoint admission` / `checkpoint build` | `pass` |
| `checkpoint merge` | `fallback` |
| `workspace locate` / `purity-check` | `pass` |

### `hotcp`

| 命令 | 结果 |
| --- | --- |
| `verify` | `ok: true` |
| `fact-chain` / `runtime-evidence` / `state-check` / `flow pre-review` | 全部 `pass` |
| `checkpoint admission` / `checkpoint build` | `pass` |
| `checkpoint merge` | `fallback` |
| `workspace locate` / `purity-check` | `pass` |

## 4. 结论

- 完整执行内核不再只在 Loom 仓库内部成立，既有仓库样本可消费同一入口链路
- 下游仓库可以明确识别应采用的脚本、入口和 gate，不需要再手工拼接流程
- `#62` 的“既有仓库复验完整执行内核”已满足关闭条件
