# Adoption Maturity Required Fields Validation

本记录归档 `#327` 的验证结果。

## 1. 验证目标

证明 light / standard / strong 成熟度不再只是一组隐含 requires，而是具备机器可读的强治理补装矩阵。

## 2. Runtime Contract

`governance_control_plane.maturity` 固定包含：

- `required_fields`
- `missing_by_level`
- `missing_details_by_level`

每个 required field 至少声明：

- `id`
- `layer`
- `required`
- `defaulting`
- `recommended_action`

`layer` 只允许：

- `core`
- `github-profile`
- `repo-owned-residue`

## 3. Consumer Contract

`governance-profile upgrade-plan` 必须继续输出稳定 `missing_inputs`，并新增 `missing_details` 与 `recommended_action`。

`governance-profile upgrade --to <level> --dry-run` 的 `satisfy_missing_input` actions 必须携带 `layer` 与 `recommended_action`，让后续 `loom-adopt` / `loom-resume` 可以直接消费。

## 4. Boundary

本轮只冻结矩阵和 runtime 校验，不改变 `loom-adopt` / `loom-resume` 的展示行为；该消费路径由 `#328` 承接。
