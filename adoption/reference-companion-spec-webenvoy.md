# Reference Companion Spec: WebEnvoy

本文提供 `WebEnvoy` 的 `repo companion` 参考样本。

它只证明当前 `.loom/companion/repo-interface.json` 最小 schema 足以承接另一类真实下游；不把 `WebEnvoy` 的模板负担、流程命名或 host gate 直接提升为 Loom core 默认规则。

## 1. Companion Rules

`WebEnvoy` 样本中的 companion rules 可抽象为：

- 规则真相保持唯一主落点
- 设计说明与 review 输入必须控制负担
- 关闭语义必须与成熟度绑定

这些规则继续保留在 companion 文档中，而不是扩张 `repo-interface.json` 的顶层 schema。

## 2. Specialized Gates

`WebEnvoy` 样本中的 specialized gates 可抽象为：

- review 前的仓库特定准备要求
- formal review 的仓库特定附加检查
- merge-ready 前的仓库特定提示与例外

这些 gate 通过 locator 被 companion 暴露给 Loom，而不是写成 Loom core 默认 gate。

## 3. Retained Host Actions

以下动作仍属于 retained host actions，不进入 `repo-interface.json`：

- PR lifecycle
- CI / ruleset / deployment product 实现
- branch / worktree / environment lifecycle 的宿主底层动作

对应边界继续由 [host-action-contract.md](/Users/mc/dev/Loom/harness/host-action-contract.md) 与 [closeout-gate.md](/Users/mc/dev/Loom/harness/closeout-gate.md) 承接。

## 4. `repo-interface.json` 样本

```json
{
  "schema_version": "loom-repo-interface/v1",
  "companion_entry": ".loom/companion/README.md",
  "repo_specific_requirements": {
    "review": [
      {
        "id": "webenvoy-review-context",
        "summary": "Read the WebEnvoy review appendix before treating review as complete.",
        "locator": ".loom/companion/review.md",
        "enforcement": "blocking"
      }
    ],
    "merge_ready": [
      {
        "id": "webenvoy-merge-ready-advisory",
        "summary": "Review the WebEnvoy merge-ready advisory note for repo-specific exceptions.",
        "locator": ".loom/companion/merge-ready.md",
        "enforcement": "advisory"
      }
    ],
    "closeout": [
      {
        "id": "webenvoy-closeout-advisory",
        "summary": "Read the WebEnvoy closeout appendix before host closeout sync.",
        "locator": ".loom/companion/closeout.md",
        "enforcement": "advisory"
      }
    ]
  },
  "specialized_gates": [
    {
      "id": "webenvoy-pre-review",
      "summary": "WebEnvoy-specific pre-review appendix.",
      "locator": ".loom/companion/pre-review.md"
    },
    {
      "id": "webenvoy-formal-review",
      "summary": "WebEnvoy-specific formal review appendix.",
      "locator": ".loom/companion/review.md"
    }
  ]
}
```
