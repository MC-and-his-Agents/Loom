# Execution Entry Compatibility And Operation Flow

本文定义 Loom 日常执行入口的升级兼容边界，并给出可复验的操作流。

对应 Loom issue：`#60`

当前正式产品版本：`v0.5.0`

当前发布判断：`minor`

## 1. 四层交付面的入口兼容

`v0.5.0` 在保持既有四层 repo-local 交付形态不变的前提下，当前稳定入口按以下四层兼容：

| 交付面 | 稳定入口 | 兼容承诺 |
| --- | --- | --- |
| `repo-local plugin` | 完整 Loom install surface | 继续作为默认安装对象，暴露 `loom-init` 与其余 scenario skills，不把宿主实现细节抬升为 Loom 真相 |
| repo-local `loom CLI` | `loom ...` | 继续作为自动化、验证、调试与宿主编排的次级执行面，不替代用户首层入口 |
| `scenario skills` | `loom-init` + 7 个 scenario skills | 继续作为用户执行面；`loom-init` 保持唯一 root entry 身份 |
| `single-skill standard-skill packages` | 单个标准 skill 的 package + 最小 launcher / shim | 只承接该 skill 的场景合同与最小运行切片，不承诺整包 Loom 默认能力 |

## 2. 执行内核兼容边界

当前稳定执行入口按以下分层兼容：

| 层级 | 稳定入口 | 兼容承诺 |
| --- | --- | --- |
| root 入口与基础验证 | `loom route` / `loom init verify` | `loom-init` 继续作为唯一 root entry，路由能力不替代底层 CLI |
| 初始化与恢复公共治理读面 | `loom-init` 输出合同 + `loom-adopt` / `loom-resume` 场景合同 | `governance_surface` 作为稳定公共字段存在；其中 `repo_interface` 只承接 `repo companion` locator、机读 requirements / typed gates，以及 `v2` 下的 metadata/context 合同摘要，场景 skill 只能复用或摘要，不新增第二套治理真相 |
| 日常读取与检查 | `loom flow fact-chain` / `loom flow runtime-evidence` / `loom flow state-check` | 输出保持 JSON 结果语义（`result/summary/missing_inputs/fallback_to`） |
| 正式 review 执行 | `loom flow review` + `loom review run` + `loom review read|record` | `flow review` 保持只读，`review run` 负责默认 engine 执行与 evidence 落盘，正式 authored truth 仍只允许写回单一 `review record` |
| checkpoint 执行 | `loom flow checkpoint admission/build/merge` | 三阶段语义与回退关系保持不变 |
| 现场与纯度治理 | `loom flow workspace <create/locate/cleanup/retire>` + `purity-check` | 生命周期动作与失败语义保持不变 |
| 宿主动作与 closeout | [../harness/host-action-contract.md](../harness/host-action-contract.md) + `loom flow host-lifecycle` + `reconciliation audit|sync` + `closeout check|sync` | 新增统一主落点，不改变现有 CLI；Loom 冻结 host-facing actions 的结果与去向，但不接管宿主 branch / PR / worktree 生命周期 |
| drift 审计与 sync | `loom flow reconciliation audit|sync` | `audit` 只生成 absorbed-but-open / parent drift / project drift；`sync` 只消费这些 finding 做机械写回，不扩展为新的 gate / 验证入口 |
| 高频组合入口 | `loom flow pre-review/review/resume/handoff/merge-ready` | 聚合入口扩张不破坏单命令入口，统一保持 JSON 结果语义；`review` / `merge-ready` 只增量暴露 `repo_specific_requirements`，不改 `result/summary/missing_inputs/fallback_to` 顶层纪律 |
| scenario skills | `loom-adopt/resume/pre-review/review/handoff/retire/merge-ready` | 场景 skill 只做入口编排，不新增第二套事实真相源 |

## 3. 升级策略

- 升级优先“加入口，不改旧入口语义”
- 新增聚合入口（如 `flow pre-review`、`flow merge-ready`）不替换单命令入口
- 新增 authored 入口（如 `review record`、`recovery writeback`、`work-item create|update`）不把只读 flow 变成隐式写入
- 新增场景 skill 入口不替代 `loom-init` 的 root 身份，只补显式入口与隐式路由
- 单 skill package 只补正式交付物，不重写场景 skill 合同
- 新增 [../harness/host-action-contract.md](../harness/host-action-contract.md) 只收口既有 host-facing actions 的合同，不新增 umbrella CLI，也不改写既有命令输出结构
- `governance_surface` 只允许扩充 locator 或职责说明，不允许更名、拆成并行字段或复制实时 authored 状态；`repo_interface` 只允许承接 `repo companion` 的 locator、requirements、typed specialized gates，以及 `v2` 下的 metadata/context 机读摘要
- gate 与 verify 始终复用同一 CLI，不维护第二套检查命令

## 4. 可复验操作流

在样本副本中按以下顺序执行：

1. `loom route`
2. `loom init verify`
3. `loom flow fact-chain`
4. `loom flow runtime-evidence`
5. `loom flow state-check`
6. `loom flow resume`
7. `loom flow pre-review`
8. `loom flow review`
9. `loom review run`
10. `loom review read|record`
11. `loom flow recovery writeback`
12. `loom flow work-item create|update`
13. `loom flow handoff`
14. `loom flow merge-ready`
15. `loom flow checkpoint admission/build/merge`
16. `loom flow workspace locate/cleanup/retire`
17. `loom flow host-lifecycle`
18. `loom flow reconciliation audit`
19. `loom flow reconciliation sync --dry-run`
20. `loom flow closeout check`

预期：

- 前 1-9 步提供“该进入哪个入口 / 可继续执行 / 需阻断 / 是否应回退”的统一判断
- `loom-init`、`loom-adopt`、`loom-resume` 对外公开的治理读面保持同一字段名 `governance_surface`
- `governance_surface.repo_interface` 只区分 `absent | companion_docs_only | incomplete | present` 四类机读状态，不把旧式 companion docs 伪装成稳定 repo interface
- 正式 review 固定按 `flow review -> review run -> review record` 分层；默认 engine 若失败必须 fail-closed，并明确回到 manual review 写回同一 review record
- merge 阶段可按状态返回 `fallback`，而不是伪装成通过
- `flow review`、`flow merge-ready` 与 `closeout check|sync` 只增量暴露 `repo_specific_requirements`；blocking companion requirement 必须显式阻断，advisory requirement 只展示不阻断
- host-facing actions 继续复用既有命令，但 `fallback` 只保留给 Loom 内部 checkpoint / merge control；closeout 与 reconciliation 不把 drift 伪装成 `fallback`
- 单 skill package 若被单独消费，也只应暴露对应场景合同，不伪装成完整 Loom install surface
- 操作流既可拆分执行，也可通过聚合入口执行高频路径

## 5. 验证结论

基于 `mail-listener`、`hotcp`、`loom-adoption-new-project` 的临时副本复验：

- `route`：显式 skill 命中与隐式信号命中均可复验
- `governance_surface`：初始化与恢复场景均通过稳定公共字段暴露治理承接面，不额外发明并行状态源
- `verify`：均返回 `ok: true`
- `fact-chain/runtime-evidence/state-check`：均可读
- `flow resume/pre-review/review/handoff/merge-ready`：均可返回稳定 JSON 结果
- `review run`：可在 build checkpoint 就绪时调用默认 Codex reviewer，并把 raw output 收敛为 Loom evidence 与 normalized findings
- `review record`、`recovery writeback`、`work-item create|update`：可显式回写 authored 结果而不引入第二真相
- `checkpoint merge` 在当前样本阶段按预期返回 `fallback`
- `host-action-contract` 把 `host-lifecycle`、`reconciliation`、`closeout` 的结果与 `fallback_to` 收到唯一主落点，而不改写既有 CLI 入口
- `reconciliation audit` 会把 GitHub drift 显式化，但不提前执行 sync
- `reconciliation sync` 必须先消费同范围 audit；若出现任一 `block` finding，则返回 `block` 且不写控制面
- `reconciliation sync --dry-run` 只输出计划，不伪装成已经完成 closeout

因此，下游仓库可以按 repo-local plugin、显式 scenario skill 或单个 standard-skill package 消费 Loom 的入口层，但单 skill consumption 不应被误读为“已经获得完整 Loom 默认能力”。
