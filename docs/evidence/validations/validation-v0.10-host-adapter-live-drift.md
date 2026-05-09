# v0.10.0 Host Adapter Live Drift

本记录归档 `#601` 的 host adapter live drift 验证结果。

它证明：

- `python3 tools/loom_flow.py live-smoke host-adapter-drift --target <repo>` 能产出 `loom-host-adapter-live-drift/v1`
- interop absent 或未声明 host adapters 时返回 profile-local `warn`
- required locator 缺失、unsafe locator 或不可读 retained result envelope 会在该命令内 `block`
- optional / advisory drift 不污染 `orchestration-core`

## Commands

```bash
python3 tools/loom_flow.py live-smoke host-adapter-drift --target examples/new-project
python3 tools/loom_flow.py live-smoke host-adapter-drift --target /tmp/loom-missing-live-target
python3 tools/skills_surface.py check
python3 tools/host_adapter_check.py
python3 tools/loom_check.py
make check
```

## Result

- Date: 2026-05-09
- `examples/new-project` result: `warn`
- `examples/new-project` interpretation:
  - repo interop contract is readable
  - no `host_adapters` are declared
  - this is profile-local live evidence, not a core blocker
- `/tmp/loom-missing-live-target` result: `warn`
- Missing-target interpretation:
  - target path unavailable
  - `fallback_to: live-smoke-retry-or-record-unavailable`
  - explicit unavailable evidence remains non-blocking confidence input
- `python3 tools/skills_surface.py check`: `pass`
- `python3 tools/host_adapter_check.py`: `pass`
- `python3 tools/loom_check.py`: `pass`
- `make check`: `pass`
- Remaining risk:
  - current repository fixtures prove drift classification and profile-local boundary, but not yet a fully green retained host action sample from a downstream strong-governance repo
