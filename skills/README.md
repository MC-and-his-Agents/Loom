# Skills

`skills/` 负责 Loom 的入口层。

当前 ledger 里还没有直接落到 `skills` 的独立核心条目，但 `skills` 已有清晰职责：

- 读取 `adoption/` 中的事项分流与 checkpoint 策略
- 读取 `governance/` 中的原则与审查模型
- 读取 `harness/` 中的执行现场与恢复能力
- 读取 `templates/` 中的模板约束
- 将这些能力装配成初始化、执行、审查与收口入口

当前 `skills/` 的直接输入主要来自：

- [adoption/routing-and-checkpoints.md](../adoption/routing-and-checkpoints.md)
- [adoption/candidate-patterns.md](../adoption/candidate-patterns.md)
- [governance/review-model.md](../governance/review-model.md)
- [harness/recovery-model.md](../harness/recovery-model.md)
- [templates/spec-suite.md](../templates/spec-suite.md)
