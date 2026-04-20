# Daily Entry Matrix

本文件定义 Loom 日常高频动作的统一入口矩阵与职责边界。

它只回答三件事：

- 哪个动作由 `skills`、CLI、gate 哪一层承接
- 每个入口读取哪类输入
- 哪些动作属于“执行入口”，哪些属于“放行入口”

宿主动作的统一结果词表与 `fallback_to` 纪律见 [host-action-contract.md](./host-action-contract.md)；本文件只保留矩阵视图。

## 1. 入口矩阵

| 动作 | 首选入口 | 读取基线 | 结果形态 | 备注 |
| --- | --- | --- | --- | --- |
| `bootstrap` | `python3 loom-init/scripts/loom-init.py bootstrap --target <repo>` | intake + 仓库信号 | 初始化结果 JSON + 首批工件 | `skills/loom-init` 负责路由，CLI 负责落盘 |
| `verify` | `python3 loom-init/scripts/loom-init.py verify --target <repo>` | init-result + fact-chain + flow 子命令 | `ok` / `errors` | 核验初始化产物与入口可读性 |
| `fact-chain` | `python3 shared/scripts/loom_flow.py fact-chain --target <repo> [--item <id>]` | 单一事实链 | `pass` / `block` | 日常统一读取入口 |
| `pre-review`（统一高频入口） | `python3 loom-pre-review/scripts/loom-pre-review.py flow pre-review --target <repo> [--item <id>]` | runtime-state + fact-chain + state-check + runtime evidence + admission + workspace locate | `pass` / `block` / `fallback` | 第一版聚焦 review 前高频检查流；`runtime_state` 不一致时直接 fail-closed |
| `review` | `python3 loom-review/scripts/loom-review.py flow review --target <repo> [--item <id>]` -> `python3 loom-review/scripts/loom-review.py review record --target <repo> [--item <id>] ...` | runtime-state + fact-chain + state-check + runtime evidence + build checkpoint + review record | `pass` / `block` / `fallback` | 正式 review 先读基线，再显式记录 reviewer 结论；`runtime_state` 不一致时直接 fail-closed |
| `checkpoint` | `python3 shared/scripts/loom_flow.py checkpoint <admission\\|build\\|merge> --target <repo> [--item <id>]` | fact-chain + purity + merge 放行材料 | `pass` / `block` / `fallback` | `merge` 可额外消费 PR 模板 |
| `resume` | `python3 loom-resume/scripts/loom-resume.py flow resume --target <repo> [--item <id>]` | runtime-state + fact-chain + state-check + workspace locate + recovery 的 `next_step` / `blockers` / `checkpoint` | `pass` / `block` | 只输出恢复摘要，不回写任何载体；`runtime_state` 不一致时直接 fail-closed |
| `handoff` | `python3 loom-handoff/scripts/loom-handoff.py flow handoff --target <repo> [--item <id>]` | runtime-state + fact-chain + state-check + workspace locate + recovery/status locator + handoff writeback fields | `pass` / `block` | 只输出最小回写清单与载体定位，不直接写 authored 状态；`runtime_state` 不一致时直接 fail-closed |
| `recovery writeback` | `python3 shared/scripts/loom_flow.py recovery writeback --target <repo> [--item <id>] ...` | 当前 fact-chain + recovery authored 字段 | `pass` / `block` | 只写 recovery 主入口，再同步状态面 |
| `work item authoring` | `python3 shared/scripts/loom_flow.py work-item create|update --target <repo> --item <id> ... [--activate]` | init-result locator + work item static fields | `pass` / `block` | `--activate` 只切当前 locator，不隐式写动态状态 |
| `host lifecycle boundary` | `python3 shared/scripts/loom_flow.py host-lifecycle --target <repo> [--item <id>]` | fact-chain + purity + 当前 branch/worktree 观测 | `pass` / `block` | 明确 workspace 由 Loom 管，branch/PR/worktree 由宿主管 |
| `reconciliation audit` | `python3 shared/scripts/loom_flow.py reconciliation audit --target <repo> [--issue <n>] [--pr <n>] [--project <n>]` | runtime-state + issue tree + PR merge事实 + Project 状态 | `pass` / `warn` / `fix-needed` / `block` | 只报出 drift，不修改 GitHub 控制面；runtime/layout 漂移时直接 fail-closed；非 `pass` 的去向由 [host-action-contract.md](./host-action-contract.md) 统一定义 |
| `reconciliation sync` | `python3 shared/scripts/loom_flow.py reconciliation sync --target <repo> [--issue <n>] [--pr <n>] [--project <n>] [--comment-file <path>] [--dry-run]` | runtime-state + 同范围 reconciliation audit + issue/PR/project 控制面 | `pass` / `block` | 只修机械可证明的 `fix-needed` drift；runtime/layout 漂移时直接 fail-closed；`block` 零写入，`warn` 仅保留提示，不提升成第二套 closeout 语义 |
| `merge-ready` | `python3 loom-merge-ready/scripts/loom-merge-ready.py flow merge-ready --target <repo> [--item <id>]` | runtime-state + fact-chain + state-check + runtime evidence + build checkpoint + merge checkpoint | `pass` / `block` / `fallback` | 只输出统一放行摘要，不替代宿主平台 merge；`runtime_state` 不一致时直接 fail-closed，`fallback_to` 只能回到 Loom 内部 checkpoint |
| `merge` | `merge checkpoint` + 仓库平台合并动作 | build 结果 + 风险回滚 + 验证摘要 | 放行或阻断 | Loom 不替代宿主平台合并接口 |
| `retire` | `python3 loom-retire/scripts/loom-retire.py purity-check --target <repo> [--item <id>]` -> `workspace cleanup` -> `workspace retire` | runtime-state + purity 结果 + cleanup 结果 + recovery 主入口 | checkpoint 终态 `retired` | 默认先解释 retire 前置条件，不默认删除现场目录；runtime/layout 漂移时直接 fail-closed |
| `closeout` | `python3 shared/scripts/loom_flow.py closeout check|sync --target <repo> [--issue <n>] [--pr <n>] [--project <n>]` | runtime-state + loom_check + 同范围 reconciliation audit/sync + issue/PR/project/main | `pass` / `block` | closeout 负责消费 reconciliation 结果；`fix-needed` / `block` 必须先停下并处理，`warn` 只显式展示，且不得伪装成 `fallback`；runtime/layout 漂移时直接 fail-closed |

## 2. 分层边界

- `skills`
  - 负责“把执行者导向正确入口”
  - 不承接 authored 执行真相
- CLI
  - 负责读取、校验、回写与输出稳定 JSON 语义
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
- gate (`loom_check` / CI)
  - 负责复用同一 CLI 入口做机械阻断
  - 不维护第二套检查口径

## 3. 非目标

- 不把宿主特定 UI/按钮/平台命令写成 Loom 内核默认入口
- 不把 `review` 结论伪装成脚本可自动生成的语义判断
- 不把 `resume`/`handoff`/`merge-ready` 另写为并行真相文件
