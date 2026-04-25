# Syvert Residue Closeout

本文归档 Loom `#332` 的 Syvert residue 分类与迁移边界。

结论：Syvert 的治理栈不应被整体复制进 Loom，也不应被 Phase D 直接删除。Loom 已承接通用强治理能力；Syvert 继续保留产品、运行时、release/sprint 与 repo-native guardian 细节。

## 1. `loom-core-consumed`

以下能力已由 Loom core 承接，Syvert 后续可以把平行说明降级为 repo-local 指向或 migration note：

| Capability | Loom owner | Syvert current carriers | Migration guidance |
| --- | --- | --- | --- |
| Work Item 唯一执行入口 | Loom core work item / admission contract | `AGENTS.md`, `WORKFLOW.md`, `docs/process/delivery-funnel.md` | Syvert 可保留业务上下文说明，但不需要维护另一套通用入口语义。 |
| gate chain | Loom core gate chain | `WORKFLOW.md`, `docs/process/agent-loop.md`, `docs/process/delivery-funnel.md` | Syvert 可引用 Loom gate chain，再补充 repo-specific guardian 和 release gate。 |
| status control plane | Loom core governance surface / status surface | `WORKFLOW.md`, `docs/process/agent-loop.md`, governance scripts | Syvert 不应再平行定义通用 status taxonomy，只保留 repo-native status carrier。 |
| maturity upgrade | Loom governance maturity model | Syvert governance rollout docs / workflow docs | Syvert maturity 应映射到 Loom `light -> standard -> strong`，不另建跨仓成熟度模型。 |
| closeout / reconciliation boundary | Loom closeout and reconciliation contracts | `docs/exec-plans/*closeout*`, `docs/process/delivery-funnel.md` | Syvert closeout 保留业务与 release 证据；通用 closeout 语义由 Loom 承接。 |
| shadow parity boundary | Loom repo interop / shadow parity | Phase D smoke `.loom/companion/interop.json` | 默认 validation-only；Syvert 不应把 shadow parity 自动升级成 merge gate。 |

## 2. `github-profile-consumed`

以下能力属于 Loom GitHub profile，不应留在 Syvert 作为跨仓默认治理定义：

| Capability | Loom owner | Syvert current carriers | Migration guidance |
| --- | --- | --- | --- |
| Phase / FR / Work Item / PR / merge commit binding | GitHub governance profile | `.github/ISSUE_TEMPLATE/*`, `WORKFLOW.md`, `docs/process/delivery-funnel.md` | Syvert 保留模板内容，但对象关系与 binding 判断由 Loom profile 统一消费。 |
| parent / sub-issue tree | GitHub governance profile | GitHub native issue hierarchy, Syvert issue templates | Syvert 不再需要解释通用 hierarchy 规则，只保留产品化命名与字段。 |
| ProjectV2 orchestration | GitHub governance profile with GraphQL budget guard | Sprint / Project 排期说明 | Project 细节继续属于 GitHub profile；Syvert 保留 release/sprint 业务含义。 |
| host drift reconciliation | GitHub governance profile reconciliation audit | closeout exec-plans, governance closeout practice | Drift taxonomy 与 fallback 由 Loom profile 承接；Syvert 保留 repo-specific closeout evidence。 |
| controlled merge binding | GitHub profile + Loom merge gate | `code_review.md`, `scripts/pr_guardian.py`, merge workflow | Loom 承接 PR/head/merge commit 绑定；Syvert guardian verdict 继续作为 repo-native retained host action result。 |

## 3. `syvert-residue`

以下内容必须继续留在 Syvert，不进入 Loom core，也不应被 Loom profile 泛化为跨仓默认：

| Residue | Why it stays in Syvert | Canonical Syvert carriers |
| --- | --- | --- |
| 产品使命与愿景 | 这是 Syvert 的业务边界，不是通用治理能力。 | `vision.md`, `framework-positioning.md` |
| roadmap / release / sprint 语义 | 这些字段服务 Syvert 的阶段规划和产品节奏，只能作为 repo-specific context。 | `docs/roadmap-v0-to-v1.md`, `WORKFLOW.md`, `docs/releases/` |
| adapter/runtime 业务规则 | Syvert runtime、adapter、resource lifecycle 是业务实现，不属于 Loom governance core。 | `syvert/`, `adapter-sdk.md`, `docs/specs/FR-*` |
| Syvert guardian 策略 | guardian 的不设超时、head binding、review context 是 Syvert 当前 repo-native gate 实现。 | `scripts/pr_guardian.py`, `code_review.md`, `docs/decisions/ADR-GOV-0030*.md`, `docs/decisions/ADR-GOV-0031*.md` |
| Syvert issue/template 命名 | `FR-000x`, `CHORE-xxxx`, release/sprint 字段是 Syvert 自身调度习惯。 | `.github/ISSUE_TEMPLATE/*`, `docs/exec-plans/` |
| integration contract 具体字段 | 字段集合与 Syvert runtime/platform integration 绑定，不应成为 Loom 默认 schema。 | `scripts/policy/integration_contract.json`, `.github/PULL_REQUEST_TEMPLATE.md`, `WORKFLOW.md` |

## 4. Migration Boundary

后续 Syvert migration 可以做：

- 把 Syvert 平行说明中的通用治理语义改成指向 Loom core / GitHub profile。
- 将 `.loom/companion` 正式引入 Syvert，用于 locator-first 读取 repo-specific requirements、specialized gates 与 shadow parity。
- 让 Syvert guardian、integration contract、release/sprint 继续作为 repo-native retained action / residue 被 Loom 消费。

后续 Syvert migration 不应做：

- 直接删除 `AGENTS.md`、`WORKFLOW.md` 或 `docs/process/*`。
- 把 Syvert 产品愿景、release/sprint、adapter/runtime 语义提升成 Loom core。
- 把 Syvert guardian 实现复制进 Loom。
- 把 Phase D smoke branch 当作已经可合并的 Syvert migration PR。

## 5. Closeout Judgment For #332

Loom 已具备承接 Syvert 通用强治理语义的上游位置；Syvert 剩余治理内容应被拆成 repo-owned residue 和 GitHub profile 消费面。

因此，Syvert 后续不需要维护与 Loom core 重复的通用治理解释，但仍需要保留自身产品、运行时、guardian 策略、release/sprint 与 integration contract 细节。
