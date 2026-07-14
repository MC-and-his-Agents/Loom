# Review Execution

本文件定义 Loom 当前公共 review 路径：语义审查发生在 reviewer/宿主中，Loom
只编排并认证 exact PR head 的 host attestation。

## 1. 默认路径

```text
loom pre-review -> semantic review -> host attestation -> loom review
```

- `loom pre-review` 读取 GitHub PR、live head、typed Work Item、branch 与正式
  worktree binding；
- reviewer 检查当前 diff、behavior/test evidence、targeted validation 与风险；
- trusted workflow 产生绑定 repository、PR、head、review kind、run、artifact
  digest、verifier 和 policy 的 attestation；
- `loom review` 只消费该 current-head attestation，不写 repo review carrier。

`review_instruction_locators` 可由 repo companion 声明 spec/implementation review
说明；locator 不可读或越界时 fail closed，Loom 不猜测仓库特定文件名。

## 2. Review truth

只有 current-head host attestation 可满足默认 semantic approval。以下内容只能
作为输入或诊断：

- raw reviewer/model output；
- PR body summary 或 GitHub comment；
- CI green；
- 本地 JSON、runtime cache 或历史 head 的 evidence；
- subagent 结果。

subagent 输出只能作为 review 输入证据，由主 reviewer 复核后才能进入结论。
attestation 中的 `findings[].disposition` 与 `disposition.status` 必须反映当前
head；repeated blocker 必须升级 reasoning/review 强度，而不是反复试探 gate。

## 3. Review policy

- 普通变更使用 current-head semantic review；
- security、permission、runtime、shared contract 与 release 变更提高 review
  强度并保留 specialized findings；
- single-maintainer 仓库可声明 `single_maintainer` policy，但不能跳过可信
  current-head attestation；
- spec review 与 implementation review 可使用不同 `review_kind`，但共享 exact
  head、run 与 artifact digest 绑定。

模型、reasoning effort 或 adapter 选择属于 reviewer/host 执行细节，不得成为
第二份 approval truth。缺少 model proof 可以是风险诊断，但不能由 repo carrier
伪造。

## 4. Findings contract

finding 至少包含 id、severity、summary、location、disposition 与 owner。修复后先
系统排查同类问题，再为新 head 生成新的 attestation。旧 head 的 approval 不能
通过“carrier-only drift”声明跨越语义改动。

`allow` 表示当前审查没有未解决 blocker；`block` 表示仍有 P0/P1；`follow_up`
只允许承接非阻断事项。delivery gate 消费 review verdict，但不产生 review verdict。

## 5. 非目标

- 不运行隐藏 review-record authoring 命令；
- 不提交 `.loom/reviews/**` 或 `.loom/runtime/review/**`；
- 不让 shadow evidence、CI 或 PR metadata 替代 approval；
- 不从 review/merge 推导 product acceptance；
- 不因 review wording 变化重复启动完整 aggregate。

PR gate 的消费边界见 [pr-merge-gate.md](./pr-merge-gate.md)。
