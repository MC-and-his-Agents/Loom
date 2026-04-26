# Validation: external runtime de-vendor migration

本记录证明 `#356` 只定义 external-runtime / de-vendor 路径，不把任何 adopted repo 默认切换到 external runtime。

## Scope

本轮冻结：

- external-runtime companion contract
- vendored `.loom/bin` 到 versioned external runtime 的迁移顺序
- companion / interop / shadow evidence 在 runtime carrier 切换期间的保留边界
- rollback 条件与 advisory fallback

本轮不做：

- 不删除任何下游仓库的 `.loom/bin`
- 不把 external runtime 设成 Loom 默认 carrier
- 不把 runtime locator 塞进 `repo-interface.json` 或 `interop.json`

## Contract anchors

必备合同：

- `docs/adoption/external-runtime-companion-contract.md`
- `docs/adoption/repo-interop-contract.md`
- `docs/adoption/repo-companion-contract.md`
- `skills/shared/references/harness/runtime-state.md`
- `docs/adoption/deep-existing-repo-default.md`

## Migration rule

迁移必须保留：

- `.loom/companion/manifest.json`
- `.loom/companion/repo-interface.json`
- `.loom/companion/interop.json`
- `.loom/status/current.md`
- `.loom/work-items/*`
- `.loom/progress/*`
- `.loom/reviews/*`
- `.loom/shadow/*`

external runtime 只替换执行入口，不替换治理真相源。

## Rollback rule

以下任一失败必须回到 vendored runtime 或 rebootstrap：

- external runtime locator 不可解析
- runtime version 不匹配
- companion / interop 不可读
- shadow evidence hash 漂移
- active item、review head binding 或 metadata parsing 不一致

Rollback 后 gate rollout 必须回到 `advisory`，并保留 evidence。

## Validation commands

```bash
python3 tools/loom_check.py .
python3 tools/loom_flow.py governance-profile status --target examples/new-project
python3 examples/new-project/.loom/bin/loom_init.py runtime-state --target examples/new-project
```

## Result

`loom_check` 现在要求 external-runtime / de-vendor contract 与 validation evidence 存在，并检查这些文档包含 runtime locator、vendored fallback、repo interop 边界和 rollback 语义。
