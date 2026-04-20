# Reference Companion Spec: Syvert

本文提供 `Syvert` 的 `repo companion` 参考样本。

它只证明当前 `.loom/companion/repo-interface.json` 最小 schema 足以承接一类真实下游；不把 `Syvert` 的 gate、目录名或命名习惯直接提升为 Loom core 默认规则。

## 1. Companion Rules

`Syvert` 样本中的 companion rules 可抽象为：

- 受控执行入口
- 唯一恢复主入口
- 以 merge-ready 为中心的 checkpoint 组织

这些规则由 companion 文档承接，不直接写入 `repo-interface.json` 的顶层字段。

## 2. Specialized Gates

`Syvert` 样本中的 specialized gates 可抽象为：

- admission/build checkpoint 的仓库特定执行约束
- merge-ready 的仓库特定总结入口
- closeout 的仓库特定检查入口

这些 gate 通过 `specialized_gates` 给出 locator，而不是让 Loom core 直接吸收实现细节。

## 3. Retained Host Actions

以下动作仍属于 retained host actions，不进入 `repo-interface.json`：

- branch / worktree lifecycle
- PR create / update / merge / close
- CI / ruleset / required-checks 的底层产品实现

这些边界继续由 [host-action-contract.md](/Users/mc/dev/Loom/harness/host-action-contract.md) 与 [closeout-gate.md](/Users/mc/dev/Loom/harness/closeout-gate.md) 承接。

## 4. `repo-interface.json` 样本

```json
{
  "schema_version": "loom-repo-interface/v1",
  "companion_entry": ".loom/companion/README.md",
  "repo_specific_requirements": {
    "review": [
      {
        "id": "syvert-formal-review",
        "summary": "Consume the Syvert semantic review checklist before treating review as complete.",
        "locator": ".loom/companion/review.md",
        "enforcement": "blocking"
      }
    ],
    "merge_ready": [
      {
        "id": "syvert-merge-ready-summary",
        "summary": "Read the Syvert merge-ready summary and remaining repo-specific gates.",
        "locator": ".loom/companion/merge-ready.md",
        "enforcement": "blocking"
      }
    ],
    "closeout": [
      {
        "id": "syvert-closeout-check",
        "summary": "Confirm Syvert-specific closeout obligations before host closeout.",
        "locator": ".loom/companion/closeout.md",
        "enforcement": "blocking"
      }
    ]
  },
  "specialized_gates": [
    {
      "id": "syvert-admission-checkpoint",
      "summary": "Syvert-specific admission checkpoint appendix.",
      "locator": ".loom/companion/checkpoints.md"
    },
    {
      "id": "syvert-build-checkpoint",
      "summary": "Syvert-specific build checkpoint appendix.",
      "locator": ".loom/companion/checkpoints.md"
    }
  ]
}
```
