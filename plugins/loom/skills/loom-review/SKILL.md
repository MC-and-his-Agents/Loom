---
name: loom-review
description: 负责正式 review 执行层。Use when Codex needs to run semantic review after pre-review and produce a host-attested review verdict without replacing merge-ready.
---

# Loom Review

`loom-review` 承接正式语义审查。普通 PR 的最终 review truth 由 GitHub review、
当前 PR head、trusted workflow run 与 artifact digest 共同拥有；Loom 只执行审查并
消费 host attestation，不写 `.loom/reviews/**` 或其他 repo review carrier。

## 1. 使用时机

在 pre-review 通过后，需要 code / implementation / semantic review 时使用。
初始化、恢复、handoff、retire 或 merge-ready 仍回到 root route matrix。

## 2. 普通默认入口

固定顺序：

1. `loom review run --target <repo> --item <id>` 执行语义审查；raw engine output
   不是 review truth。
2. 审查结论由 GitHub review/check-run 或 single-maintainer host assertion 发布。
3. `loom attestation readback --repo <owner/repo> --pr <n> --work-item <n>
   --artifact-input <file> [--review-policy approved|single_maintainer] --json`
   认证当前 head 的正式结论。

Host readback 必须绑定：

- GitHub PR 与当前 head；
- current-head review，或经 policy 允许的 sole-maintainer assertion；
- semantic tree digest；
- trusted default-branch workflow run 与 artifact digest；
- verifier identity、Work Item 类型与 PR/issue 关系。

缺少、过期、冲突或无法认证时 fail closed。不得回退到 repo review JSON、progress、
status、shadow、手写 head 或口头结论。

## 3. Reinforced compatibility

历史 `review record` 只属于明确的 reinforced compatibility backend。使用者必须同时
声明 `reinforced-carrier-compat/v1` 与不超过 90 天的 RFC3339 expiry；普通 skill
不路由到该入口，也不得把 compatibility 自动升级成仓库 profile。

## 4. Codex App 执行边界

`review run` 可选择已认证的 Codex App host adapter；必须绑定 thread、cwd、target、
reviewed head 与 output schema，且不得启动嵌套 `codex exec`。host proof 缺失时可
fail closed 回到人工 GitHub review，但不能写 repo review record 作为替代。

## 5. 输出

输出只包含 agent-safe review 摘要和 GitHub locator：

- reviewed PR/head；
- semantic tree、run 与 artifact digest locator；
- review policy、verifier 与 verdict；
- findings 摘要；
- 缺口的单一 primary cause 与 remediation。

不得内联长 raw output，不新增 review ledger 或第二状态机。

## 6. 完成标准

- 普通 review 从执行到消费产生 0 个 repo carrier mutation；
- attestation 绑定当前 PR head、semantic tree、run、artifact 与 verifier；
- GitHub host truth 可直接供 PR gate / merge-ready 消费；
- host readback 失败不隐式恢复旧 review carrier；
- reinforced compatibility 必须显式且有期限。

输入与输出字段见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
