# GitHub Delivery Funnel

本文件定义 Loom strong governance 默认 `GitHub governance profile` 的交付漏斗。

GitHub 是默认宿主实现，但不是唯一宿主内核。
Loom 冻结的是对象语义、前置关系与绑定链，不冻结 GitHub 私有命名。

## 1. 默认漏斗

默认路径固定为：

- `Roadmap / 阶段目标`
- `GitHub Phase`
- `GitHub FR`
- `GitHub Work Item`
- `spec / contract`
- `spec review`
- `implementation PR`
- implementation review
- `merge-ready`
- `controlled merge`
- `closeout`

## 2. 对象分工

### 2.1 `Roadmap / 阶段目标`

负责表达阶段存在理由、阶段边界与阶段完成标准。
不进入执行，不承接 PR。

### 2.2 `Phase`

负责把阶段目标映射到一组稳定治理范围。
只承载阶段边界，不承接执行现场。

### 2.3 `FR`

`FR` 默认承接 formal spec / planning 层。

它回答：

- 为什么值得进入正式承诺
- 共享边界和风险是什么
- 应拆出哪些 `Work Item`

默认约束：

- `FR` 不直接承接 implementation PR
- formal spec 绑定到 `FR`
- `FR` 不替代 `Work Item`

### 2.4 `Work Item`

`Work Item` 是唯一默认执行入口。

只有 `Work Item` 可以进入：

- worktree / branch
- recovery / resume
- implementation PR
- implementation review
- `merge-ready`
- `controlled merge`
- `closeout`

## 3. 强前置关系

默认前置关系固定如下：

- `Roadmap / Phase` 为 `FR` 提供阶段边界
- `FR` 为 `Work Item` 提供 requirement 边界
- 命中 formal spec 路径时，`Work Item` 必须先绑定到 `FR`
- formal spec 必须先完成 `spec review`
- `spec review` 通过后，`Work Item` 才能进入 `implementation PR`
- implementation review 必须消费 `spec review`
- `merge-ready` 必须消费 `spec review`、implementation review 与当前 `head_sha`
- `controlled merge` 必须消费 `merge-ready` 与宿主 merge 控制面
- `closeout` 必须消费 merge commit 与 `reconciliation audit`

## 4. 绑定链要求

GitHub host 下默认至少要能稳定读取：

- `FR -> Work Item`
- `Work Item -> implementation PR`
- `PR -> reviewed head_sha`
- `PR -> merge commit`
- `merge commit -> default branch`

任何后序 gate 都不得再用口头解释补齐这条链。

## 5. enforcement 规则

以下路径必须 fail-closed：

- `FR -> implementation PR`
- PR 先于 `Work Item`
- formal spec 路径绕过 `spec review`
- implementation review 不消费 `spec review`
- `merge-ready` 不消费 implementation review
- `closeout` 不消费 merge / reconciliation basis

## 6. 非目标

- 不把 `Phase / FR / Work Item` 三个名字冻结为 Loom 永恒唯一命名
- 不把 GitHub API 细节提升为 Loom core 规则
- 不让 `FR`、PR 或 merge commit 越权替代 `Work Item`
