# Adoption Maturity Upgrade Automation Validation

本记录归档 `#326` 的验证结果。

## 1. 验证目标

证明 GitHub governance profile 的 `light -> standard -> strong` 升级路径不再只是文档说明，而是具备 dry-run-first 的可执行升级入口。

## 2. Runtime Entry

```bash
python3 tools/loom_flow.py governance-profile upgrade \
  --target <repo> \
  --to standard \
  --dry-run
```

输出固定使用 `schema_version: loom-governance-upgrade/v1`。

## 3. Write Boundary

默认行为是 dry-run，只输出 action plan。

非 dry-run 必须显式使用 `--apply`，并且只允许写 Loom-owned scaffold：

- `.loom/companion/manifest.json`
- `.loom/companion/repo-interface.json`
- `.loom/companion/interop.json`
- `.loom/companion/AGENTS.md`

遇到 repo-owned 文件或已存在 Loom-owned scaffold 且未显式 `--force` 时必须 `block`。

## 4. Boundary

本轮只产品化升级动作入口与安全写入边界。成熟度强制字段矩阵由 `#327` 冻结；`loom-adopt` / `loom-resume` 消费升级路径由 `#328` 承接。
