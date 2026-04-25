# Skills Consume Maturity Upgrade Path Validation

本记录归档 `#328` 的验证结果。

## 1. 验证目标

证明 `loom-adopt` / `loom-resume` 不再只依赖文字说明，而是能消费 governance maturity upgrade path。

## 2. Runtime Surfaces

`loom-init` bootstrap / adopt 输出新增：

- `maturity_upgrade_path.current`
- `maturity_upgrade_path.next`
- `maturity_upgrade_path.missing_inputs`
- `maturity_upgrade_path.missing_details`
- `maturity_upgrade_path.upgrade_entry`
- `maturity_upgrade_path.validation_entries`

`loom-resume` 的底层入口：

```bash
python3 tools/loom_flow.py flow resume --target <repo> --item <item>
```

也输出同一 `maturity_upgrade_path`，并把下一档缺口并入 resume 的 `missing_inputs`。

## 3. Consumption Contract

`maturity_upgrade_path` 不只是文本建议。它必须链接到具体 gate / validation entry：

- `governance-profile status`
- `governance-profile upgrade-plan`
- `governance-profile upgrade --dry-run`

## 4. Boundary

本轮不自动应用升级；真实写入仍由 `governance-profile upgrade --apply` 的 Loom-owned scaffold 边界控制。
