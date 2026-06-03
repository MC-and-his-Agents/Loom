# Adoption

`adoption/` 负责回答两个问题：

1. 为什么需要 Loom。
2. 一个项目如何采用 Loom 这个 agent-first project operating layer，以及当前已识别能力应落到哪里。

术语约束：

- 正式术语统一使用 `repo companion`
- 历史材料中的 `companion docs` 仅作迁移/回溯表述

本目录当前承接：

- 提取台账：[extraction-ledger.md](../evidence/extraction-ledger.md)
- 总落点映射：[landing-map.md](../evidence/landing-map.md)
- 采用动机与上游边界：[rationale.md](./rationale.md)
- 事项分流、checkpoint 与入口策略：[routing-and-checkpoints.md](./routing-and-checkpoints.md)
- `repo companion` 主合同：[repo-companion-contract.md](./repo-companion-contract.md)
- `repo interop` 主合同：[repo-interop-contract.md](./repo-interop-contract.md)
- agent-assisted zero-friction adoption 合同：[zero-friction-adoption-contract.md](./zero-friction-adoption-contract.md)
- 小型既有仓库的默认 retrofit 策略：[lightweight-retrofit-default.md](./lightweight-retrofit-default.md)
- 成熟治理重仓的默认 attach 策略：[deep-existing-repo-default.md](./deep-existing-repo-default.md)
- 成熟治理重仓的 authority migration playbook：[complex-existing-authority-migration-playbook.md](./complex-existing-authority-migration-playbook.md)
- GitHub 默认治理实现 profile：[github-profile.md](./github-profile.md)
- GitHub profile 升级路径：[github-profile-upgrade.md](./github-profile-upgrade.md)
- CI required checks bootstrap：[ci-required-checks-bootstrap.md](./ci-required-checks-bootstrap.md)
- 目标仓库 release / version 合同：[target-repo-version-contract.md](./target-repo-version-contract.md)
- `.loom` surfaces 版本控制策略：[loom-surfaces-version-control.md](./loom-surfaces-version-control.md)
- 统一安装体验：[unified-install-experience.md](./unified-install-experience.md)
- CLI-only 安装合同：[cli-only-install-contract.md](./cli-only-install-contract.md)
- 宿主适配矩阵：`host-adapter-matrix.md`
- 安装 taxonomy 与权威边界：[installation-taxonomy.md](./installation-taxonomy.md)
- 单 skill 安装合同：[single-skill-contract.md](./single-skill-contract.md)
- 已安装 Loom status 与升级演练：[installed-loom-status.md](./installed-loom-status.md)
- CLI-first installed-state 合同：[loom-installed-state-v2.md](./loom-installed-state-v2.md)
- 版本权威图：[version-authority-map.md](./version-authority-map.md)

边界约束：

- Adoption 只负责说明项目如何进入 Loom operating layer，不把 Loom 收窄成治理套件。
- 外部方法论来源只进入抽象入口、分发、行为回归和 adapter 边界；本目录不新增来源专属文档树，也不复制外部 skill/file layout。

当前目录对应的主要 `EXT-*` 条目：

- 核心：`EXT-0005`、`EXT-0010`、`EXT-0021`、`EXT-0030`
- 采用路径：`EXT-0007`、`EXT-0019`、`EXT-0024`、`EXT-0032`、`EXT-0044`、`EXT-0045`、`EXT-0046`、`EXT-0047`
- agent-assisted adoption：`EXT-0056`
- operating layer 定位与外部方法论抽象边界：`EXT-0057`
- behavior-first evidence loop：`EXT-0058`
- 待验证能力：`EXT-0020`、`EXT-0027`、`EXT-0043`
