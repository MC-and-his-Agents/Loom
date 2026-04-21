# Adoption

`adoption/` 负责回答两个问题：

1. 为什么需要 Loom。
2. 一个项目如何采用 Loom，以及当前已识别能力应落到哪里。

术语约束：

- 正式术语统一使用 `repo companion`
- 历史材料中的 `companion docs` 仅作迁移/回溯表述

本目录当前承接：

- 提取台账：[extraction-ledger.md](./extraction-ledger.md)
- 总落点映射：[landing-map.md](./landing-map.md)
- 采用动机与上游边界：[rationale.md](./rationale.md)
- 事项分流、checkpoint 与入口策略：[routing-and-checkpoints.md](./routing-and-checkpoints.md)
- `repo companion` 主合同：[repo-companion-contract.md](./repo-companion-contract.md)
- `repo companion` scoped adoption/workflow contract：[companion-oriented-workflow.md](./companion-oriented-workflow.md)
- 成熟治理重仓接入树 workflow contract：[deep-existing-repo-workflow.md](./deep-existing-repo-workflow.md)
- `repo companion` migration contract：[repo-companion-migration.md](./repo-companion-migration.md)
- `repo companion` Syvert 参考接口样本：[reference-companion-spec-syvert.md](./reference-companion-spec-syvert.md)
- `repo companion` WebEnvoy 参考接口样本：[reference-companion-spec-webenvoy.md](./reference-companion-spec-webenvoy.md)
- `repo companion` 接口状态验证：[validation-repo-companion-interface.md](./validation-repo-companion-interface.md)
- 小型既有仓库的默认 retrofit 策略：[lightweight-retrofit-default.md](./lightweight-retrofit-default.md)
- 成熟治理重仓的默认 attach 策略：[deep-existing-repo-default.md](./deep-existing-repo-default.md)
- 暂不固化、待继续验证的候选模式：[candidate-patterns.md](./candidate-patterns.md)
- 外部优秀 `SKILLS` 仓库设计清单与 Loom gap analysis：[skills-repo-design-checklist.md](./skills-repo-design-checklist.md)
- 初始化 `SKILL` 模拟验证：[demo-init-validation.md](./demo-init-validation.md)
- 真实 adoption 验证记录合同：[validation-record-contract.md](./validation-record-contract.md)
- 经验回流机制：[experience-feedback-loop.md](./experience-feedback-loop.md)
- 新项目真实验证：[validation-new-project.md](./validation-new-project.md)
- 新项目主路径验证：[validation-main-path-new-project.md](./validation-main-path-new-project.md)
- 既有仓库反例验证：[validation-devskills.md](./validation-devskills.md)
- 既有仓库执行与 sync repo companion 验证：[validation-existing-repo-execution-sync.md](./validation-existing-repo-execution-sync.md)
- `#143` 树 live retrofit 验证：[validation-retrofit-143-tree.md](./validation-retrofit-143-tree.md)
- 复杂既有仓库真实验证：[validation-hotcp.md](./validation-hotcp.md)
- 场景 skill `loom-adopt` 验证：[validation-skill-loom-adopt.md](./validation-skill-loom-adopt.md)
- 场景 skill `loom-resume` 验证：[validation-skill-loom-resume.md](./validation-skill-loom-resume.md)
- 场景 skill `loom-pre-review` 验证：[validation-skill-loom-pre-review.md](./validation-skill-loom-pre-review.md)
- 场景 skill `loom-handoff` 验证：[validation-skill-loom-handoff.md](./validation-skill-loom-handoff.md)
- 场景 skill `loom-retire` 验证：[validation-skill-loom-retire.md](./validation-skill-loom-retire.md)
- 场景 skill `loom-merge-ready` 验证：[validation-skill-loom-merge-ready.md](./validation-skill-loom-merge-ready.md)
- installed-skills pre-merge 链验收：[validation-installed-skills-pre-merge-chain.md](./validation-installed-skills-pre-merge-chain.md)
- installed-skills post-merge closeout 验收：[validation-installed-skills-post-merge-closeout.md](./validation-installed-skills-post-merge-closeout.md)
- 事实链消费验证：[validation-fact-chain-mail-listener.md](./validation-fact-chain-mail-listener.md)
- checkpoint 链路复验：[validation-checkpoints-hotcp.md](./validation-checkpoints-hotcp.md)
- 运行时证据复验：[validation-runtime-evidence-hotcp.md](./validation-runtime-evidence-hotcp.md)
- automation-frontload 复验：[validation-automation-frontload-hotcp.md](./validation-automation-frontload-hotcp.md)
- `SKILLS` 产品面收敛验证与 closeout：[validation-skills-surface-convergence.md](./validation-skills-surface-convergence.md)
- 执行入口兼容与操作流：[execution-entry-compatibility.md](./execution-entry-compatibility.md)
- 新项目完整执行内核复验：[validation-complete-kernel-new-project.md](./validation-complete-kernel-new-project.md)
- 既有仓库完整执行内核复验：[validation-complete-kernel-existing-repos.md](./validation-complete-kernel-existing-repos.md)
- 版本化与升级路径：[versioning-and-upgrades.md](./versioning-and-upgrades.md)
- 上游交付面：[upstream-delivery-surface.md](./upstream-delivery-surface.md)

Issue -> 验证 / 回写索引：

- `#168` -> [validation-main-path-new-project.md](./validation-main-path-new-project.md)
- `#170` -> [validation-existing-repo-execution-sync.md](./validation-existing-repo-execution-sync.md)
- `#180` -> [validation-retrofit-143-tree.md](./validation-retrofit-143-tree.md)
- `#209` -> [validation-installed-skills-pre-merge-chain.md](./validation-installed-skills-pre-merge-chain.md)
- `#210` -> [validation-installed-skills-post-merge-closeout.md](./validation-installed-skills-post-merge-closeout.md)
- `#227` -> [validation-skills-surface-convergence.md](./validation-skills-surface-convergence.md)
- `#223` -> [skills-repo-design-checklist.md](./skills-repo-design-checklist.md)
- `#233` -> [../docs/skills-surface-delivery-judgment.md](../docs/skills-surface-delivery-judgment.md); [../docs/skills-surface-issue-tree-draft.md](../docs/skills-surface-issue-tree-draft.md)
- `#226` -> [upstream-delivery-surface.md](./upstream-delivery-surface.md); [versioning-and-upgrades.md](./versioning-and-upgrades.md); [../skills/distribution-and-adapter-contract.md](../skills/distribution-and-adapter-contract.md)
- `#169` -> [landing-map.md](./landing-map.md); [upstream-delivery-surface.md](./upstream-delivery-surface.md); [versioning-and-upgrades.md](./versioning-and-upgrades.md); [../docs/complete-kernel-release.md](../docs/complete-kernel-release.md)

当前目录对应的主要 `EXT-*` 条目：

- 核心：`EXT-0005`、`EXT-0010`、`EXT-0021`、`EXT-0030`
- 采用路径：`EXT-0007`、`EXT-0019`、`EXT-0024`、`EXT-0032`、`EXT-0044`、`EXT-0045`、`EXT-0046`、`EXT-0047`
- 待验证能力：`EXT-0020`、`EXT-0027`、`EXT-0043`
