# Daily Entry Matrix

本文件定义 Loom 日常高频动作的统一入口矩阵与职责边界。

它只回答三件事：

- 哪个动作由 `skills`、CLI、gate 哪一层承接
- 每个入口读取哪类输入
- 哪些动作属于“执行入口”，哪些属于“放行入口”

宿主动作的统一结果词表与 `fallback_to` 纪律见 [host-action-contract.md](./host-action-contract.md)；本文件只保留矩阵视图。

本文统一把 repo-local 次级操作面写成 `loom ...`。这组命令主要服务自动化、验证、调试和宿主编排；用户首层入口仍是 plugin 安装后的 `loom-init` 与其余 scene skills。当前仓库开发态或安装态可以把这组命令映射到底层 `tools/` / `scripts/` carrier，但不改变这里定义的入口职责。

## 1. 入口矩阵

| 动作 | 首选入口 | 读取基线 | 结果形态 | 备注 |
| --- | --- | --- | --- | --- |
| `bootstrap` | `loom init bootstrap --target <repo>` | intake + 仓库信号 | 初始化结果 JSON + 首批工件 | `skills/loom-init` 负责路由，repo-local `loom CLI` 负责落盘 |
| `verify` | `loom init verify --target <repo>` | init-result + fact-chain + flow 子命令 | `ok` / `errors` | 核验初始化产物与入口可读性 |
| `fact-chain` | `loom flow fact-chain --target <repo> [--item <id>]` | 单一事实链 | `pass` / `block` | 日常统一读取入口 |
| `pre-review`（统一高频入口） | `loom flow pre-review --target <repo> [--item <id>]` | runtime-state + fact-chain + state-check + runtime evidence + admission + workspace locate | `pass` / `block` / `fallback` | 第一版聚焦 review 前高频检查流；`runtime_state` 不一致时直接 fail-closed |
| `review` | `loom flow review --target <repo> [--item <id>]` -> `loom review record --target <repo> [--item <id>] ...` | runtime-state + fact-chain + state-check + runtime evidence + build checkpoint + review record | `pass` / `block` / `fallback` | 正式 review 先读基线，再显式记录 reviewer 结论；`runtime_state` 不一致时直接 fail-closed |
| `checkpoint` | `loom flow checkpoint <admission\\|build\\|merge> --target <repo> [--item <id>]` | fact-chain + purity + merge 放行材料 | `pass` / `block` / `fallback` | `merge` 可额外消费 PR 模板 |
| `resume` | `loom flow resume --target <repo> [--item <id>]` | runtime-state + fact-chain + state-check + workspace locate + recovery 的 `next_step` / `blockers` / `checkpoint` | `pass` / `block` | 只输出恢复摘要，不回写任何载体；`runtime_state` 不一致时直接 fail-closed |
| `handoff` | `loom flow handoff --target <repo> [--item <id>]` | runtime-state + fact-chain + state-check + workspace locate + recovery/status locator + handoff writeback fields | `pass` / `block` | 只输出最小回写清单与载体定位，不直接写 authored 状态；`runtime_state` 不一致时直接 fail-closed |
| `recovery writeback` | `loom flow recovery writeback --target <repo> [--item <id>] ...` | 当前 fact-chain + recovery authored 字段 | `pass` / `block` | 只写 recovery 主入口，再同步状态面 |
| `work item authoring` | `loom flow work-item create|update --target <repo> --item <id> ... [--activate]` | init-result locator + work item static fields | `pass` / `block` | `--activate` 只切当前 locator，不隐式写动态状态 |
| `host lifecycle boundary` | `loom flow host-lifecycle --target <repo> [--item <id>]` | fact-chain + purity + 当前 branch/worktree 观测 | `pass` / `block` | 明确 workspace 由 Loom 管，branch/PR/worktree 由宿主管 |
| `reconciliation audit` | `loom flow reconciliation audit --target <repo> [--issue <n>] [--pr <n>] [--project <n>]` | runtime-state + issue tree + PR merge事实 + Project 状态 | `pass` / `warn` / `fix-needed` / `block` | 只报出 drift，不修改 GitHub 控制面；runtime/layout 漂移时直接 fail-closed；非 `pass` 的去向由 [host-action-contract.md](./host-action-contract.md) 统一定义 |
| `reconciliation sync` | `loom flow reconciliation sync --target <repo> [--issue <n>] [--pr <n>] [--project <n>] [--comment-file <path>] [--dry-run]` | runtime-state + 同范围 reconciliation audit + issue/PR/project 控制面 | `pass` / `block` | 只修机械可证明的 `fix-needed` drift；runtime/layout 漂移时直接 fail-closed；`block` 零写入，`warn` 仅保留提示，不提升成第二套 closeout 语义 |
| `merge-ready` | `loom flow merge-ready --target <repo> [--item <id>]` | runtime-state + fact-chain + state-check + runtime evidence + build checkpoint + merge checkpoint | `pass` / `block` / `fallback` | 只输出统一放行摘要，不替代宿主平台 merge；`runtime_state` 不一致时直接 fail-closed，`fallback_to` 只能回到 Loom 内部 checkpoint |
| `merge` | `merge checkpoint` + 仓库平台合并动作 | build 结果 + 风险回滚 + 验证摘要 | 放行或阻断 | Loom 不替代宿主平台合并接口 |
| `retire` | `loom flow purity-check --target <repo> [--item <id>]` -> `loom flow workspace cleanup --target <repo> [--item <id>]` -> `loom flow workspace retire --target <repo> [--item <id>]` | runtime-state + purity 结果 + cleanup 结果 + recovery 主入口 | checkpoint 终态 `retired` | 默认先解释 retire 前置条件，不默认删除现场目录；runtime/layout 漂移时直接 fail-closed |
| `closeout` | `loom flow closeout check|sync --target <repo> [--issue <n>] [--pr <n>] [--project <n>]` | runtime-state + loom_check + 同范围 reconciliation audit/sync + issue/PR/project/main | `pass` / `block` | closeout 负责消费 reconciliation 结果；`fix-needed` / `block` 必须先停下并处理，`warn` 只显式展示，且不得伪装成 `fallback`；runtime/layout 漂移时直接 fail-closed |

## 2. 分层边界

- `skills`
  - 负责“把执行者导向正确入口”
  - 不承接 authored 执行真相
- repo-local `loom CLI`
  - 负责读取、校验、回写与输出稳定 JSON 语义
  - 作为自动化、验证、调试和宿主编排的次级入口
  - 不替代 reviewer 的语义判断
- `reconciliation audit`
  - 负责把 GitHub drift 显式化
  - 不替代后续 sync
- `reconciliation sync`
  - 必须先消费同范围 `reconciliation audit`
  - 不绕过 `block` finding，不伪造实现完成
- `closeout`
  - 负责把 reconciliation 结果接入 closeout 判定与控制面对齐
  - 不另写新的 reconciliation 主合同，也不绕过先处理 `fix-needed` / `block` 再 closeout 的顺序
- gate (`loom check` / CI)
  - 负责复用同一 repo-local CLI 入口做机械阻断
  - 不维护第二套检查口径

## 3. 非目标

- 不把宿主特定 UI/按钮/平台命令写成 Loom 内核默认入口
- 不把 `review` 结论伪装成脚本可自动生成的语义判断
- 不把 `resume`/`handoff`/`merge-ready` 另写为并行真相文件
