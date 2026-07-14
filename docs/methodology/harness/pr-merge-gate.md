# PR Merge Gate

本文件定义公共 `loom pr gate` 如何把 current-head semantic review 与 GitHub
required checks 连接起来。它不运行 review，也不把 CI green 推导为产品完成。

## 1. 权威输入

gate 只消费：

- typed Work Item locator；
- GitHub PR number、body、head SHA、base branch 与 check runs live readback；
- 绑定 exact PR head 的 GitHub host attestation；
- repo companion 声明的最小 policy fields；
- 仓库原生 targeted test results。

branch、head、checks 与 merge facts 不得手写进 PR body。committed current、status、
progress、review、shadow、suite 或 closeout carrier 都不是 gate 输入。

## 2. Approval truth

semantic approval 只能由 current-head host attestation 满足。attestation 必须绑定
repository、PR、head、review policy、run、artifact digest 与 verifier；旧 head、
本地 JSON、PR 摘要、raw model output、CI success 或 GitHub comment 都不能替代。

单维护者仓库可使用明确的 `single_maintainer` policy，但仍必须产生可信的
current-head attestation，不能静默跳过 review。

## 3. 输出与交接

`loom pr gate --full-output --json` 每次失败只返回一个 primary cause，并输出当前
host snapshot。完整结果保存在 repo-relative ignored workstation file；随后由：

```text
loom merge-ready --pr-gate-result-file <file> ...
```

重新验证 exact PR head、attestation、required checks 与 mergeability。retained
result 不能替代 GitHub live readback，也不能跨 head 复用。

## 4. 非目标

- 不创建或修复 repo execution carrier；
- 不修改 PR、issue、branch protection 或 ruleset；
- 不承担产品验收；
- 不以 fallback 掩盖独立失败；
- 不在普通 PR 上重复完整 aggregate。

受控 merge 语义见 [controlled-merge.md](./controlled-merge.md)，公共命令集合见
[cli-command-matrix.md](./cli-command-matrix.md)。
