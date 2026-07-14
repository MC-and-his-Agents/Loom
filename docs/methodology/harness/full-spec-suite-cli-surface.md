# Full Spec Suite CLI Surface（已退役）

本文件保留原合同 locator，说明 full-spec suite 的专用 CLI 计划已经退出公共产品
面。历史命令、schema、fixture 设计与迁移过程由 Git 历史保留，不再作为 Agent
的执行建议。

当前规则：

- 公共命令固定为 `loom help --json` 返回的 30 个入口；
- 正式规划由 GitHub Issue / Work Item 与仓库原生文档承载；
- `loom build` 不要求 repo-local spec、plan、task 或 suite carrier；
- `loom pre-review`、`loom review`、`loom pr gate` 与 `loom merge-ready`
  消费 GitHub host facts、current-head attestation 和仓库原生测试证据；
- light profile 下 committed current、status、progress、review、shadow、suite 与
  closeout carrier 都不是默认生命周期输入；
- 旧 suite surface 只可作为不可达的 compatibility input 被诊断，不能由公共
  help、skills、remediation 或 release readiness 推荐。

公共产品面以 [cli-command-matrix.md](./cli-command-matrix.md) 为准。需要正式
规格时，使用 [spec-suite.md](../templates/spec-suite.md) 作为人类可读模板；模板
存在不构成 gate 或产品验收事实。
