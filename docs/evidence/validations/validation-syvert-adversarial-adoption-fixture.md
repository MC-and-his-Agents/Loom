# Validation: Syvert-style adversarial adoption fixture

本记录证明 `#357` 把 Syvert PR #259 暴露出的 hardening 缺口收成 Loom-owned upstream acceptance gate。

## Scope

本 fixture 不是替代 Syvert guardian，也不是继续用 Syvert 作为探测器。

它在 `loom_check` 内构造一个 Syvert-style strong governance adopted repo，并对同一基线施加对抗性变体，验证 Loom core 会在正确层级 fail-closed。

## Coverage

组合 smoke 覆盖：

- env poisoning
  - `LOOM_SOURCE_REPO_ROOT=/tmp/not-loom` 不得覆盖 bootstrapped target runtime 判定
- runtime provenance drift
  - `.loom/bootstrap/manifest.json` 中 `.loom/bin/*` sha256 漂移必须阻断 runtime parity
- active item rollover
  - bootstrap item `INIT-0001` 与 active item `WORK-0002` 分离，resume 必须消费当前 active item
- shadow evidence closure
  - 缺失 `source_sha256` 时 validation-only 返回 `warn`，blocking 返回 `block`
- metadata spoofing
  - canonical section 内重复字段必须 fail-closed，后文正确 bullet 不得覆盖前序 truth
- review head binding
  - review 后 implementation drift 必须分类为 `implementation-drift-only`

## Acceptance Gate

Syvert PR #259 恢复前，必须先满足：

```bash
python3 tools/loom_check.py .
```

该命令必须包含并通过 `adversarial-adoption` category。

## Validation Commands

```bash
python3 -m py_compile tools/loom_init.py tools/loom_flow.py tools/loom_status.py tools/loom_check.py skills/shared/scripts/*.py
python3 tools/loom_check.py .
make loom-check
npm --prefix packages/loom-installer test
```

## Result

Loom 不再依赖 guardian 暴露这些 generic adoption hardening 缺口。Syvert official adoption 后续恢复时，应先刷新到包含本 fixture 的 Loom runtime，再运行本地 hardening gate。
