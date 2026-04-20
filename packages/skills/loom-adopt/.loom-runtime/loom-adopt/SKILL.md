---
name: loom-adopt
description: 负责把仓库接入 Loom 的初始化场景入口。Use when Codex needs to initialize a new repository with Loom or retrofit Loom into an existing repository.
---

# Loom Adopt

这个 skill 承接初始化与 retrofit 场景。

它只编排已有 root bootstrap 能力，不新增并行事实源，不创建第二套日常执行入口。

## 1. 使用时机

当任务满足以下任一条件时，进入 `loom-adopt`：

- 明确要求初始化新项目
- 明确要求把既有仓库接入 Loom
- 明确要求 retrofit Loom 入口、首批工件或初始化事实链
- 当前任务核心问题是“如何进入 Loom”，而不是“如何恢复、review、handoff、retire 或 merge-ready”

若任务其实是接手当前事项、review 前检查、交接、retire 或 merge-ready，应回到 root route matrix，转向对应场景 skill：

- [../route-matrix.md](../route-matrix.md)

## 2. 读取顺序

按以下顺序读取：

- 目标仓库中的 `AGENTS.md`、`README`、流程文档、模板、验证入口
- Loom 根级定位文档
  - `AGENTS.md`
  - `README.md`
- 初始化相关稳定规则
  - [../shared/references/adoption/lightweight-retrofit-default.md](../shared/references/adoption/lightweight-retrofit-default.md)
  - [../shared/references/adoption/routing-and-checkpoints.md](../shared/references/adoption/routing-and-checkpoints.md)
  - [../shared/references/harness/fact-chain-contract.md](../shared/references/harness/fact-chain-contract.md)
  - [../loom-init/references/input-signals.md](../loom-init/references/input-signals.md)
  - [../loom-init/references/output-contract.md](../loom-init/references/output-contract.md)
- 本 skill 的场景合同
  - [references/input-signals.md](./references/input-signals.md)
  - [references/output-contract.md](./references/output-contract.md)

## 3. 固定编排

本 skill 不新增新 CLI，固定复用：

- `python3 scripts/loom-adopt.py bootstrap --target <repo>`
- `python3 scripts/loom-adopt.py verify --target <repo>`
- `python3 scripts/loom-adopt.py fact-chain --target <repo>`

执行顺序固定为：

1. 先判断这是 `新项目`、`小型既有仓库` 还是 `复杂既有仓库`
2. 再给出本轮启用能力、暂不启用能力与升级触发条件
3. 若用户要求实际落盘，再执行 `bootstrap --write`
4. 落盘后必须能用 `verify` 与 `fact-chain` 复读

## 4. 输出要求

输出必须直接遵守初始化输出合同，而不是另写一套 adopt 专属真相：

- [../loom-init/references/output-contract.md](../loom-init/references/output-contract.md)

至少要明确：

- 当前初始化场景判断
- 本轮启用能力
- 首批工件与首批事项
- 事实链入口
- 验证入口
- 当前不启用什么，以及为什么

## 5. 完成标准

只有当以下条件同时满足时，才算 `loom-adopt` 完成：

- root route 或显式 skill 调用都能稳定命中 `loom-adopt`
- `bootstrap` 输出能解释为什么是这条 adoption 路径
- `verify` 与 `fact-chain` 都能消费落盘结果
- 结果没有引入新的事实链载体或平行状态源
