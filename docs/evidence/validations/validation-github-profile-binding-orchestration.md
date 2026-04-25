# GitHub Profile Binding Orchestration Validation

本记录归档 `#322` 的验证结果。

## 1. 验证目标

证明 GitHub governance profile 已具备只读 host binding 编排读面，可以把以下对象收成同一条可检查链：

- `Phase`
- `FR`
- `Work Item`
- implementation PR
- merge commit
- target branch

该读面属于 GitHub profile，不把 GitHub 对象命名提升为 Loom core。

## 2. Runtime Entry

```bash
python3 tools/loom_flow.py governance-profile binding \
  --target . \
  --owner MC-and-his-Agents \
  --repo Loom \
  --phase <phase-issue> \
  --fr <fr-issue> \
  --issue <work-item> \
  --pr <implementation-pr> \
  --branch <branch>
```

输出固定使用 `schema_version: loom-github-binding/v1`，并按 `Phase -> FR -> Work Item -> PR -> merge commit -> target branch` 暴露 `binding.chain`。

## 3. Blocking Semantics

缺少必需对象或绑定关系不可证明时，结果必须为：

- `result: block`
- `fallback_to: github-profile-binding`
- finding 使用 `category: gate_failure` 与 `kind: binding_failure`

`--sync --dry-run` 只输出修复计划，不写 GitHub 控制面。

## 4. Boundary

本轮不处理 drift reconciliation、不优化 ProjectV2 / native sub-issues GraphQL-only 路径，也不把 GitHub profile 对象模型写入 Loom core。
这些能力分别由 `#323` 与 `#324` 承接。
