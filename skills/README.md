# Skills

`skills/` 负责 Loom 的入口层。

当前 `skills/` 的核心职责，是把 Loom 已有能力装配成可直接使用的入口。

当前已落以下入口与入口合同：

- [loom-init/SKILL.md](./loom-init/SKILL.md)
  - 根据项目场景选择应引入的 Loom 能力、首批工件与首批事项
- [distribution-and-adapter-contract.md](./distribution-and-adapter-contract.md)
  - 约束 `skills/` 作为入口层时的最小分发、发现、升级、版本识别与宿主适配边界

当前 `skills/` 的职责包括：

- 读取 `adoption/` 中的事项分流、checkpoint 策略与默认 retrofit 路径
- 读取 `governance/` 中的原则与审查模型
- 读取 `harness/` 中的执行现场与恢复能力
- 读取 `templates/` 中的模板约束
- 将这些能力装配成初始化、执行、审查与收口入口

对入口层自身，Loom 当前至少要求能表达以下验证面：

- 显式触发是否正确
- 隐式触发是否正确
- 行为是否出现退化
- adapter 失败是否可见
- 版本变化是否可见

这些验证面的最小边界由 [distribution-and-adapter-contract.md](./distribution-and-adapter-contract.md) 承接；宿主完整测试矩阵与 CI 产品细节不进入 Loom 内核。

当前 `skills/` 的直接输入主要来自：

- [adoption/routing-and-checkpoints.md](../adoption/routing-and-checkpoints.md)
- [adoption/lightweight-retrofit-default.md](../adoption/lightweight-retrofit-default.md)
- [governance/review-model.md](../governance/review-model.md)
- [harness/recovery-model.md](../harness/recovery-model.md)
- [templates/spec-suite.md](../templates/spec-suite.md)
- [loom-init/references/intake-signals.md](./loom-init/references/intake-signals.md)
- [loom-init/references/output-contract.md](./loom-init/references/output-contract.md)

其中 `loom-init` 负责把以下入口合同转成实际判断与输出：

- 输入信号合同
  - [loom-init/references/intake-signals.md](./loom-init/references/intake-signals.md)
- 输出合同
  - [loom-init/references/output-contract.md](./loom-init/references/output-contract.md)
- 小型既有仓库默认策略
  - [../adoption/lightweight-retrofit-default.md](../adoption/lightweight-retrofit-default.md)
- `skills` 分发与适配合同
  - [distribution-and-adapter-contract.md](./distribution-and-adapter-contract.md)
