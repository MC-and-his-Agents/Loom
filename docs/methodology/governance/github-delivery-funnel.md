# GitHub Delivery Funnel

本文件定义 Loom 当前默认 `GitHub governance profile` 的交付漏斗。

GitHub 是 Loom 当前默认宿主实现，但不是唯一宿主内核。
其他宿主只要能提供等价对象与状态读取面，也可以实现同一条漏斗。

## 1. 默认漏斗

Loom 当前冻结的默认交付路径如下：

- `Roadmap / 阶段目标`
- `GitHub Phase`
- `GitHub FR`
- `GitHub Work Item`
- `spec / contract`
- `spec review`
- `implementation PR`
- `PR review`
- `squash merge`

Loom 只冻结这条路径的语义，不冻结 GitHub 之外宿主的具体对象名字。

## 2. 对象分工

### 2.1 `Roadmap / 阶段目标`

负责表达当前阶段为什么存在、阶段边界是什么、什么结果才算本阶段完成。

它不直接进入执行，也不直接承接 PR。

### 2.2 `Phase`

负责把阶段目标映射到一组较稳定的治理范围。

它回答：

- 当前阶段在推进什么大面
- 哪些 `FR` 属于同一阶段
- 阶段边界何时允许收口

### 2.3 `FR`

`FR` 默认承接 formal spec / planning 层。

它回答：

- 为什么值得进入正式承诺
- 共享边界和风险是什么
- 应拆出哪些 `Work Item`

默认情况下：

- `FR` 不直接承接实现 PR
- `FR` 不替代 `Work Item`
- `FR` 不并行 authored 执行中停点或验证摘要

### 2.4 `Work Item`

`Work Item` 是 Loom 默认唯一执行入口。

只有 `Work Item` 可以进入：

- worktree / branch 绑定
- recovery / resume
- implementation PR
- review / merge-ready / closeout

任何未收成 `Work Item` 的对象，都默认仍停留在规划或边界层。

## 3. 前置关系

默认前置关系固定如下：

- `Roadmap / Phase` 为 `FR` 提供阶段边界
- `FR` 为 `Work Item` 提供正式目标与共享边界
- `Work Item` 若命中 formal spec 准入，必须先有 `spec / contract`
- `spec review` 通过后，`Work Item` 才能进入 `implementation PR`
- `PR review` 不替代 `spec review`
- `merge-ready` 不承担第一次高质量语义判断

## 4. Loom 与 GitHub 的边界

Loom 不要求自研 GitHub 控制面。

Loom 只要求 GitHub profile 至少能稳定提供：

- `Roadmap / Phase / FR / Work Item` 的映射关系
- 当前事项的 `head_sha`
- PR / review / merge gate 的最小状态读取
- parent / sub-issue 关系

这些读取面应被 Loom 消费，而不是在 skill、脚本和 PR 描述里各自发明一套解释。

## 5. 非目标

- 不把 `Phase / FR / Work Item` 三个名字冻结为 Loom 永恒唯一命名
- 不把 GitHub API 细节提升为 Loom core 规则
- 不让 `FR` 或 `PR` 越权替代 `Work Item`
