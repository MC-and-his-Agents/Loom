# Real Adoption Validation: Complete Kernel In New Project

## 1. 样本标识

- 样本仓库：`loom-adoption-new-project`
- 仓库类型：`新项目`
- 仓库位置：`/Users/mc/dev/loom-adoption-new-project`
- 验证副本：`/tmp/loom-val-new`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#61`

## 2. 复验路径

1. 在空仓副本执行 bootstrap：
   - `python3 tools/loom_init.py bootstrap --target /tmp/loom-val-new --write --force --verify --install-pr-template`
2. 提交 bootstrap 基线后，执行完整入口链路：
   - `.loom/bin/loom_init.py verify`
   - `.loom/bin/loom_flow.py fact-chain`
   - `.loom/bin/loom_flow.py runtime-evidence`
   - `.loom/bin/loom_flow.py state-check`
   - `.loom/bin/loom_flow.py flow pre-review`
   - `.loom/bin/loom_flow.py checkpoint admission/build/merge`
   - `.loom/bin/loom_flow.py workspace locate`

## 3. 结果

| 命令 | 结果 |
| --- | --- |
| `verify` | `ok: true` |
| `fact-chain` | `pass` |
| `runtime-evidence` | `pass` |
| `state-check` | `pass` |
| `flow pre-review` | `pass` |
| `checkpoint admission` | `pass` |
| `checkpoint build` | `fallback` |
| `checkpoint merge` | `fallback` |
| `workspace locate` | `pass` |
| `purity-check` | `pass` |

## 4. 结论

- 新项目样本可以按统一入口从“最小起步”升级到“完整执行内核可消费”状态
- 入口链路已能机械回答事实读取、状态一致性、运行时证据与 checkpoint 承接
- `#61` 的新项目复验目标已满足并进入版本控制
