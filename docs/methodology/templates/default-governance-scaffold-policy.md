# Default Governance Scaffold Policy

本文件冻结 Loom 默认治理模板与 locator 分层策略。

它是 `#819` 的主落点。它定义 Loom 在目标仓库缺少根规则、workflow、review instruction、vision 或 roadmap 文件时可以如何提供默认 scaffold、如何声明 locator、以及何时必须保持 intentionally absent。

## 1. 目标

默认 scaffold 的目标是降低 adoption 摩擦，同时不伪造宿主仓库的业务真相、规划真相或 repo-specific review 规则。

Loom 可以提供：

- 最小 agent 入口模板
- GitHub profile 下的最小 workflow 协议模板
- Loom default review instruction 选择
- product / planning truth 的待填写模板
- 缺失 locator 的机读缺口语义

Loom 不得因此生成：

- review verdict
- closeout result
- runtime state
- 产品完成事实
- roadmap 完成事实
- repo-specific review rule

## 2. Scaffold 分类

| Surface | 默认提供 | 默认落盘 | 缺失时默认 action | 权威边界 |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | 是 | 新仓库或显式 adoption 时 | `generate` 或 `require_user_input` | Loom-owned agent entry，只说明读取顺序、Loom 入口、验证命令与业务真相边界 |
| `WORKFLOW.md` | 是 | `light-governance` / `execution-control` 时 | `generate` 或 `require_user_input` | Loom-owned execution protocol，承接 GitHub profile 下 Phase / FR / Work Item / PR / closeout 执行协议 |
| `code_review.md` | 是 | 仅显式选择 repo-owned review rules 时 | `declare_loom_default` | review instruction locator；默认不猜测 repo-owned 文件路径 |
| `spec_review.md` | 是 | formal spec path 启用且显式选择 repo-owned review rules 时 | `declare_loom_default` 或 `require_user_input` | review instruction locator；不得把缺失 spec gate 伪装成仓库已有规则 |
| `VISION.md` | 是，模板 | 默认不落盘；仅新项目初始化或用户明确要求时 | `intentionally_absent` 或 `requires_user_authored_truth` | repo-owned product truth，模板必须标记待填写 |
| `ROADMAP.md` / `docs/roadmap/*` | 是，模板和 locator | 默认不落盘；仅新项目初始化、用户明确要求或宿主仓库声明 locator 时 | `intentionally_absent`、`requires_user_authored_truth` 或 repo-declared locator 解析 | repo-owned planning truth，模板不得成为自动生成的计划事实 |

## 3. Action 语义

adoption dry-run 必须为每个缺失 surface 输出一个 action：

- `generate`
  - 本轮可以生成最小 scaffold。
  - 只允许写入声明性入口、读取顺序、执行协议、验证入口或待填写模板。
- `declare_loom_default`
  - 本轮不创建 repo-owned 文件，而是在 locator 合同中声明使用 Loom default。
  - 适用于缺失 `code_review.md` / `spec_review.md` 且目标仓库未显式选择 repo-owned review rules 的场景。
- `intentionally_absent`
  - 本轮明确不生成该 surface，verify 应把缺失读作有意缺席。
  - 适用于没有用户授权的 `VISION.md`、roadmap surface、release target surface 或其他 repo-owned truth。
- `requires_user_authored_truth`
  - 该 surface 属于宿主产品、规划或业务真相，Loom 只能提示用户补写或声明 locator。
  - 不得由 Loom 自动代写为完成事实。
- `require_user_input`
  - 当前 adoption intent、locator 或 write target 不足以安全决定是否写入。
  - 必须先回到 decision prompt，不得静默生成。

## 4. Review Locator 规则

`code_review.md` 与 `spec_review.md` 的缺失不等于目标仓库已有 repo-owned review rule。

默认处理：

- 未声明 repo-owned review rules 时，写入 `repo-interface.json.review_instruction_locators` 的 `mode: loom_default`
- 已声明 repo-owned review rules 时，locator 必须指向仓内可读路径，`mode: repo_declared`
- formal spec path 启用但 `spec_review` locator 缺失时，不得猜测 `spec_review.md` 路径
- mature / deep-existing 仓库中 repo-owned locator 缺失、不可读或越界时必须 fail closed

`loom_default` 只表示使用 Loom 默认 review instruction。它不是 repo-owned rule，不承载 review verdict、finding disposition、validation status 或 retained host action result。

## 5. Product 与 Planning Truth

`VISION.md` 与 roadmap surface 属于宿主仓库的 product / planning truth。

默认规则：

- 缺失 `VISION.md` 时，不自动创建产品愿景
- 缺失 `ROADMAP.md` 或 `docs/roadmap/*` 时，不自动创建计划事实
- 模板若被显式生成，必须标记为待填写，不得写成已验证目标、已承诺路线图或完成事实
- repo-declared locator 可以指向宿主已有 product / planning truth，但 Loom 不猜测文件名
- Project view、Phase、FR、Work Item 可以引用 roadmap / vision locator，但不得让 roadmap 或 vision 替代 Work Item 执行入口

## 6. Decision Prompt 要求

写入前的 decision prompt 至少必须覆盖：

- `target_repository`
- `adoption_intent`
- `repository_mode`
- `missing_surfaces`
- 每个 missing surface 的 proposed action
- `write_targets`
- `forbidden_writes`
- `review_instruction_locator_decision`
- `vision_locator_decision`
- `roadmap_locator_decision`
- `validation_commands`
- `source_locators`

当 `adoption_intent = unspecified` 且 proposed action 会生成 governance scaffold、review locator 或 product / planning 模板时，必须 fail closed 并要求用户确认 intent。

## 7. Verify 规则

verify 必须能区分：

- `intentionally_absent`
- `loom_default` locator
- `repo_declared` locator
- generated scaffold
- `requires_user_authored_truth`

verify 必须阻断以下情况：

- generated scaffold 承载 review verdict、closeout result 或 runtime state
- generated `VISION.md` 被写成产品完成事实
- generated roadmap 被写成计划完成事实
- `loom_default` 被伪装成 repo-owned review rule
- repo-owned review locator 缺失、不可读、越界或与 declared mode 不一致
- 缺失 roadmap / vision 被猜测为默认路径

## 8. 与其他合同的关系

- [repo-companion-contract.md](../../adoption/repo-companion-contract.md)
  - 承接 `review_instruction_locators`、repo-specific requirements 与 companion-owned locator 合同
- [zero-friction-adoption-contract.md](../../adoption/zero-friction-adoption-contract.md)
  - 承接 `read -> judge -> write -> verify` adoption 闭环与 decision prompt
- [deep-existing-repo-default.md](../../adoption/deep-existing-repo-default.md)
  - 承接成熟既有仓库的 attach-only 默认路径
- [github-delivery-funnel.md](../governance/github-delivery-funnel.md)
  - 承接 GitHub profile 下 Phase / FR / Work Item / PR 的执行链语义

本文件不复制这些合同的 schema 或 gate 规则，只定义默认 scaffold 与缺失 surface 的落点策略。
