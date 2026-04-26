# Validation: Metadata Parser Hardening

## Goal

验证 Loom fact-chain parser 不再允许 canonical section 内重复字段通过 last-write-wins 覆盖事实。

## Scope

本验证覆盖：

- `Static Facts` 重复字段必须失败
- `Runtime Evidence` 重复字段必须失败
- Runtime Evidence 仅在缺失整个 section 时允许 legacy fallback
- Runtime Evidence 已存在但字段重复时不得 fallback 成功

## Validation Entry

```bash
python3 tools/loom_check.py .
```

## Runtime Evidence

`loom_check` 的 metadata spoofing fixture 会：

- 在 work item `Static Facts` 中插入重复 `Goal`，确认 `inspect_fact_chain()` 报 duplicate field
- 在 status `Runtime Evidence` 中插入重复 `Run Entry`，确认 `loom_flow.py fact-chain` 返回 `block`，而不是被 legacy parser 吞掉

## Result

Pass. Canonical metadata blocks now fail closed on duplicate fields.
