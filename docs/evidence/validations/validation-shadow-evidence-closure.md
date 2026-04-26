# Validation: Shadow Evidence Closure

## Goal

验证 `shadow-parity` 不再消费裸状态值，而是只消费带 source closure 的 shadow evidence envelope。

## Scope

本验证覆盖：

- evidence 必须声明非空 `source_files`
- evidence 必须声明 `source_sha256`
- `source_files` 与 `source_sha256` key set 必须完全一致
- source 必须是仓库内现存文件
- source sha256 必须匹配当前文件内容
- `.loom/shadow/*.json` 中除 `.loom/shadow/shadow-parity.json` 外，不允许出现未被 `interop.json.shadow_surfaces` 声明的 evidence

## Validation Entry

```bash
python3 tools/loom_check.py .
```

## Runtime Evidence

`loom_check` 的 repo interop fixture 覆盖以下样本：

- matching envelope -> `shadow-parity` returns `pass`
- mismatch envelope -> validation-only returns `warn`, blocking mode returns `block`
- unreadable declared evidence -> blocking mode returns `block`
- missing `source_sha256` -> report result `unreadable`
- partial `source_sha256` key set -> report result `unreadable`
- source content drift after evidence creation -> report result `unreadable`
- rogue `.loom/shadow/rogue.json` not declared by `shadow_surfaces` -> report result `unreadable`

## Result

Pass. Shadow parity now requires closed source evidence before a surface can be considered readable.
