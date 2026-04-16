---
name: loom-adopt
description: 负责把仓库接入 Loom 的初始化场景入口。Use when Codex needs to initialize a new repository with Loom or retrofit Loom into an existing repository.
---

# Loom Adopt

这个 skill 承接初始化与 retrofit 场景。

它只编排已有 root bootstrap 能力，不新增并行事实源。

优先入口：

- `python3 tools/loom_init.py bootstrap --target <repo>`
- `python3 tools/loom_init.py verify --target <repo>`
- `python3 tools/loom_init.py fact-chain --target <repo>`

使用时机、输入信号与输出合同分别见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
